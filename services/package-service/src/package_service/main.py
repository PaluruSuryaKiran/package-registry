from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from package_service.db import Base, engine, get_session
from package_service.models import Package, Release
from package_service.schemas import PackageCreate, PackageOut

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown code

app = FastAPI(title="Package Registry", lifespan=lifespan)


def latest_version_of(session: Session, package_id: int) -> str | None:
    return session.scalar(
        select(Release.version)
        .where(Release.package_id == package_id)
        .order_by(Release.major.desc(), Release.minor.desc(), Release.patch.desc())
        .limit(1)
    )


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
            detail=f"package {body.name!r} already exists",
        )
    return package


@app.get("/packages/{name}", response_model=PackageOut)
def get_package(name: str, session: SessionDep):
    package = session.scalar(select(Package).where(Package.name == name))
    if package is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"package {name!r} not found",
        )
    return PackageOut(
        name=package.name,
        description=package.description,
        created_at=package.created_at,
        latest_version=latest_version_of(session, package.id),
    )