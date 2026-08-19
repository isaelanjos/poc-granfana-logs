import logging
import time
from contextlib import asynccontextmanager
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from logging_config import configure_logging


logger = configure_logging()


class PetCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    species: Annotated[str, Field(min_length=1, max_length=50)]
    age: Annotated[int, Field(ge=0, le=100)]


class Pet(PetCreate):
    id: int


pets: dict[int, Pet] = {
    1: Pet(id=1, name="Luna", species="cat", age=3),
    2: Pet(id=2, name="Bolt", species="dog", age=5),
    3: Pet(id=3, name="Nemo", species="fish", age=1),
}


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("application_started", extra={"event": "application_started"})
    yield
    logger.info("application_stopped", extra={"event": "application_stopped"})


app = FastAPI(title="API Veterinária Mock", version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    request.state.request_id = request_id
    started = time.perf_counter()
    response = None
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.log(
            logging.ERROR if status_code >= 400 else logging.INFO,
            "request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "client_ip": request.client.host if request.client else None,
                "request_id": request_id,
            },
        )
        if response is not None:
            response.headers["x-request-id"] = request_id


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", str(uuid4()))
    logger.error(
        "validation_error",
        extra={"event": "validation_error", "request_id": request_id},
    )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "request_id": request_id},
        headers={"x-request-id": request_id},
    )


@app.get("/")
async def root():
    return {"service": "api-vet", "message": "API veterinária mock"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/pets", response_model=list[Pet])
async def list_pets():
    logger.info("pet_found", extra={"event": "pet_found"})
    return list(pets.values())


@app.get("/pets/{pet_id}", response_model=Pet)
async def get_pet(pet_id: int):
    pet = pets.get(pet_id)
    if pet is None:
        logger.error("pet_not_found", extra={"event": "pet_not_found"})
        raise HTTPException(status_code=404, detail="Pet não encontrado")
    logger.info("pet_found", extra={"event": "pet_found"})
    return pet


@app.post("/pets", response_model=Pet, status_code=201)
async def create_pet(payload: PetCreate):
    pet = Pet(id=max(pets, default=0) + 1, **payload.model_dump())
    pets[pet.id] = pet
    logger.info("pet_created", extra={"event": "pet_created"})
    return pet
