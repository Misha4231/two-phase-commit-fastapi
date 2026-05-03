from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import text

from common.schemas.purchase import PrepareResponse, UserCommitResponse
from user_service.core.logging import logger
from user_service.models.user import User

"""
Opens a database session, locks user row, validate balance
"""
async def prepare(transaction_id: str, user_id: int, amount: float, db: AsyncSession) -> PrepareResponse:
    logger.info("user_prepare_start", transaction_id=transaction_id, user_id=user_id)
    
    # using raw sql to use prepare
    raw = await db.connection()
    try:
        await raw.execute(text("BEGIN"))
        result = await db.execute(
            select(User).where(User.id == user_id).with_for_update()
        )
        user = result.scalar_one_or_none()

        if user is None:
            await raw.execute("ROLLBACK")

            logger.warning("user_prepare_not_found", transaction_id=transaction_id, user_id=user_id)
            return PrepareResponse(transaction_id=transaction_id, ready=False, reason="User not found")

        if user.balance < amount:
            await raw.execute("ROLLBACK")
            logger.warning(
                "user_prepare_insufficient_balance",
                transaction_id=transaction_id,
                user_id=user_id,
                balance=user.balance,
                required=amount,
            )

            return PrepareResponse(transaction_id=transaction_id, ready=False, reason=f"Insufficient balance: has {user.balance}, needs {amount}")

        user.balance -= amount
        await db.flush() # don't commit
        
        await raw.execute(text(f"PREPARE TRANSACTION '{transaction_id}'")) # detach transaction from connection
        logger.info("user_prepare_ready", transaction_id=transaction_id, user_id=user_id)
        return PrepareResponse(transaction_id=transaction_id, ready=True)

    except Exception as e:
        await raw.execute("ROLLBACK")
        logger.error("user_prepare_error", transaction_id=transaction_id, error=str(e))
        raise


async def commit(transaction_id: str, user_id: int, db: AsyncSession) -> UserCommitResponse:
    raw = await db.connection()
    await raw.execute(text(f"COMMIT PREPARED '{transaction_id}'"))
    
    logger.info("user_commit_success", transaction_id=transaction_id)

    # query updated user after commit
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()

    return UserCommitResponse(transaction_id=transaction_id, remaning_balance=user.balance)


async def rollback(transaction_id: str, db: AsyncSession) -> None:
    raw = await db.connection()
    await raw.execute(text(f"ROLLBACK PREPARED '{transaction_id}'"))

    logger.info("user_rollback_success", transaction_id=transaction_id)
    return