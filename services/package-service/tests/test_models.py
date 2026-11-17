import pytest
from sqlalchemy.exc import IntegrityError

from package_service.models import Package, Release


def test_create_package_sets_id_and_created_at(session):
    pkg = Package(name="curl", description="transfer tool")
    session.add(pkg)
    session.commit()

    assert pkg.id is not None
    assert pkg.created_at is not None


def test_package_name_must_be_unique(session):
    session.add(Package(name="curl"))
    session.commit()

    session.add(Package(name="curl"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_release_is_linked_to_its_package(session):
    pkg = Package(name="curl")
    pkg.releases.append(Release(version="8.5.0", major=8, minor=5, patch=0))
    session.add(pkg)
    session.commit()

    assert pkg.releases[0].package_id == pkg.id


def test_same_version_twice_for_one_package_is_rejected(session):
    pkg = Package(name="curl")
    pkg.releases.append(Release(version="8.5.0", major=8, minor=5, patch=0))
    session.add(pkg)
    session.commit()

    pkg.releases.append(Release(version="8.5.0", major=8, minor=5, patch=0))
    with pytest.raises(IntegrityError):
        session.commit()


def test_same_version_is_allowed_on_different_packages(session):
    for name in ["curl", "wget"]:
        pkg = Package(name=name)
        pkg.releases.append(Release(version="1.0.0", major=1, minor=0, patch=0))
        session.add(pkg)

    session.commit()


def test_release_needs_an_existing_package(session):
    session.add(Release(package_id=999, version="1.0.0", major=1, minor=0, patch=0))
    with pytest.raises(IntegrityError):
        session.commit()