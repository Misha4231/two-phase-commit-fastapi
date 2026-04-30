from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.exc import NoResultFound

from user_service.models.user import User
from user_service.schemas.user import UserCreate, UserUpdate
from user_service.core.logging import logger


async def get_all_users(db: AsyncSession):
    logger.debug("service_get_all_users_start")

    result = await db.execute(select(User))
    users = result.scalars().all()

    logger.debug(
        "service_get_all_users_success",
        users_count=len(users)
    )

    return users


async def get_user(user_id: int, db: AsyncSession):
    logger.debug(
        "service_get_user_start",
        user_id=user_id
    )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(
            "service_get_user_not_found",
            user_id=user_id
        )
        raise NoResultFound()

    logger.debug(
        "service_get_user_success",
        user_id=user_id
    )

    return user


async def create_user(data: UserCreate, db: AsyncSession):
    logger.debug(
        "service_create_user_start",
        name=data.name,
        balance=data.balance
    )

    try:
        user = User(**data.model_dump())
        db.add(user)

        await db.commit()
        await db.refresh(user)

        logger.debug(
            "service_create_user_success",
            user_id=user.id
        )

        return user

    except Exception as e:
        logger.error(
            "service_create_user_failed",
            error=str(e)
        )
        raise


async def update_user(user_id: int, data: UserUpdate, db: AsyncSession):
    logger.info(
        "service_update_user_start",
        user_id=user_id,
        name=data.name,
        balance=data.balance
    )

    try:
        values = {}

        if data.name is not None:
            values["name"] = data.name
        if data.balance is not None:
            values["balance"] = data.balance

        if not values:
            logger.info(
                "service_update_user_no_fields",
                user_id=user_id
            )
            return None

        async with db.begin():
            result = await db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**values)
                .returning(User)
            )

            user = result.scalar_one_or_none()

            if not user:
                logger.warning(
                    "service_update_user_not_found",
                    user_id=user_id
                )
                return None

        logger.info(
            "service_update_user_success",
            user_id=user_id
        )

        return user

    except Exception as e:
        logger.error(
            "service_update_user_failed",
            user_id=user_id,
            error=str(e)
        )
        raise

async def delete_user(user_id: int, db: AsyncSession):
    logger.info(
        "service_delete_user_start",
        user_id=user_id,
    )

    try:
        async with db.begin():
            result = await db.execute(
                delete(User)
                .where(User.id == user_id)
                .returning(User.id)
            )
            deleted_id = result.scalar_one_or_none()

            if deleted_id is None:
                logger.warning(
                    "service_delete_user_not_found",
                    user_id=user_id,
                )
                raise NoResultFound()

        logger.info(
            "service_delete_user_success",
            user_id=user_id
        )

        return True

    except Exception as e:
        logger.error(
            "service_delete_user_failed",
            user_id=user_id,
            error=str(e)
        )
        raise