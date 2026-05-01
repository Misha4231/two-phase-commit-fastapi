import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select

from user_service.services import users as user_service
from user_service.schemas.user import UserCreate, UserUpdate
from user_service.models.user import User


@pytest.mark.anyio
async def test_create_user(db_session: AsyncSession):
    data = UserCreate(name="test", balance=100)

    user = await user_service.create_user(data, db_session)

    assert user.id is not None
    assert user.name == "test"
    assert user.balance == 100


@pytest.mark.anyio
async def test_create_user_persisted(db_session: AsyncSession):
    data = UserCreate(name="persist", balance=50)

    user = await user_service.create_user(data, db_session)

    result = await db_session.execute(select(User).where(User.id == user.id))
    db_user = result.scalar_one()

    assert db_user.name == "persist"
    assert db_user.balance == 50


@pytest.mark.anyio
async def test_get_all_users_empty(db_session: AsyncSession):
    users = await user_service.get_all_users(db_session)
    assert users == []


@pytest.mark.anyio
async def test_get_all_users_multiple(db_session: AsyncSession):
    await user_service.create_user(UserCreate(name="a", balance=1), db_session)
    await user_service.create_user(UserCreate(name="b", balance=2), db_session)

    users = await user_service.get_all_users(db_session)

    assert len(users) == 2


@pytest.mark.anyio
async def test_get_user_success(db_session: AsyncSession):
    user = await user_service.create_user(UserCreate(name="a", balance=10), db_session)

    fetched = await user_service.get_user(user.id, db_session)

    assert fetched.id == user.id
    assert fetched.name == "a"


@pytest.mark.anyio
async def test_get_user_not_found(db_session: AsyncSession):
    with pytest.raises(NoResultFound):
        await user_service.get_user(999, db_session)


@pytest.mark.anyio
async def test_update_user_full(db_session: AsyncSession):
    user = await user_service.create_user(UserCreate(name="a", balance=10), db_session)

    updated = await user_service.update_user(
        user.id, UserUpdate(name="updated", balance=50), db_session
    )

    assert updated.name == "updated"
    assert updated.balance == 50


@pytest.mark.anyio
async def test_update_user_partial_name(db_session: AsyncSession):
    user = await user_service.create_user(UserCreate(name="a", balance=10), db_session)

    updated = await user_service.update_user(
        user.id, UserUpdate(name="new"), db_session
    )

    assert updated.name == "new"
    assert updated.balance == 10


@pytest.mark.anyio
async def test_update_user_partial_balance(db_session: AsyncSession):
    user = await user_service.create_user(UserCreate(name="a", balance=10), db_session)

    updated = await user_service.update_user(
        user.id, UserUpdate(balance=999), db_session
    )

    assert updated.name == "a"
    assert updated.balance == 999


@pytest.mark.anyio
async def test_update_user_not_found(db_session: AsyncSession):
    result = await user_service.update_user(999, UserUpdate(name="x"), db_session)

    assert result is None


@pytest.mark.anyio
async def test_update_user_no_fields(db_session: AsyncSession):
    user = await user_service.create_user(UserCreate(name="a", balance=10), db_session)

    result = await user_service.update_user(
        user.id,
        UserUpdate(),  # empty payload
        db_session,
    )

    assert result is None


@pytest.mark.anyio
async def test_delete_user_success(db_session: AsyncSession):
    user = await user_service.create_user(UserCreate(name="a", balance=10), db_session)

    result = await user_service.delete_user(user.id, db_session)

    assert result is True

    # verify deletion
    res = await db_session.execute(select(User).where(User.id == user.id))
    assert res.scalar_one_or_none() is None


@pytest.mark.anyio
async def test_delete_user_not_found(db_session: AsyncSession):
    with pytest.raises(NoResultFound):
        await user_service.delete_user(999, db_session)
