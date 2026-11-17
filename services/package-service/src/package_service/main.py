from sqlalchemy.orm import Session
from typing import Annotated
from fastapi import Depends, FastAPI, status, HTTPException
from contextlib import asynccontextmanager
from package_service.db import get_session, engine, Base
from package_service.schemas import PackageOut, PackageCreate
from package_service.models import Package
from sqlalchemy.exc import IntegrityError

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown code

app = FastAPI(title="Package Registry", lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/packages", response_model=PackageOut, status_code=status.HTTP_201_CREATED)
def create_package(body: PackageCreate, session: SessionDep):
    package = Package(name=body.name, description=body.description)
    session.add(package)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Package with this name already exists.",
        )
    return package