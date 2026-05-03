from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import text

from common.schemas.purchase import BookCommitResponse, BookPrepareResponse
from book_service.core.logging import logger
from book_service.models.book import Book

"""
Opens a database session, locks books row, validate stock
"""
async def prepare(transaction_id: str, book_id: int, quantity: int, db: AsyncSession) -> BookPrepareResponse:
    logger.info("book_prepare_start", transaction_id=transaction_id, book_id=book_id, quantity=quantity)
    
    # using raw sql to use prepare
    raw = await db.connection()
    try:
        await raw.execute(text("BEGIN"))
        result = await db.execute(
            select(Book).where(Book.id == book_id).with_for_update()
        )
        book = result.scalar_one_or_none()

        if book is None:
            await raw.execute("ROLLBACK")

            logger.warning("book_prepare_not_found", transaction_id=transaction_id, book_id=book_id)
            return BookPrepareResponse(transaction_id=transaction_id, ready=False, reason="Book not found")

        if book.stock < quantity:
            await raw.execute("ROLLBACK")
            logger.warning(
                "book_prepare_insufficient_stock",
                transaction_id=transaction_id,
                book_id=book_id,
                quantity=quantity,
                required=book.stock,
            )

            return BookPrepareResponse(transaction_id=transaction_id, ready=False, reason=f"Insufficient stock: has {book.stock}, needs {quantity}")

        book.stock -= quantity
        await db.flush() # don't commit

        total_price = book.price * quantity
        
        await raw.execute(text(f"PREPARE TRANSACTION '{transaction_id}'")) # detach transaction from connection
        logger.info("book_prepare_ready", transaction_id=transaction_id, book_id=book_id)
        return BookPrepareResponse(transaction_id=transaction_id, ready=True, total_price=total_price)

    except Exception as e:
        await raw.execute("ROLLBACK")
        logger.error("book_prepare_error", transaction_id=transaction_id, error=str(e))
        raise


async def commit(transaction_id: str, book_id: int, db: AsyncSession) -> BookCommitResponse:
    raw = await db.connection()
    await raw.execute(text(f"COMMIT PREPARED '{transaction_id}'"))
    
    logger.info("book_commit_success", transaction_id=transaction_id)

    # query updated book after commit
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one()

    return BookCommitResponse(transaction_id=transaction_id, remaining_stock=book.stock)


async def rollback(transaction_id: str, db: AsyncSession) -> None:
    raw = await db.connection()
    await raw.execute(text(f"ROLLBACK PREPARED '{transaction_id}'"))

    logger.info("book_rollback_success", transaction_id=transaction_id)
    return
