from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.exc import NoResultFound

from book_service.models.book import Book
from book_service.schemas.book import BookCreate, BookUpdate
from book_service.core.logging import logger


async def get_all_books(db: AsyncSession):
    logger.debug("service_get_all_books_start")
    result = await db.execute(select(Book))
    books = result.scalars().all()
    logger.debug("service_get_all_books_success", books_count=len(books))
    return books


async def get_book(book_id: int, db: AsyncSession):
    logger.debug("service_get_book_start", book_id=book_id)
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        logger.warning("service_get_book_not_found", book_id=book_id)
        raise NoResultFound()
    logger.debug("service_get_book_success", book_id=book_id)
    return book


async def create_book(data: BookCreate, db: AsyncSession):
    logger.debug(
        "service_create_book_start",
        title=data.title,
        author=data.author,
        stock=data.stock,
        price=data.price,
    )
    try:
        book = Book(**data.model_dump())
        db.add(book)
        await db.commit()
        await db.refresh(book)
        logger.debug("service_create_book_success", book_id=book.id)
        return book
    except Exception as e:
        logger.error("service_create_book_failed", error=str(e))
        raise


async def update_book(book_id: int, data: BookUpdate, db: AsyncSession):
    logger.info(
        "service_update_book_start",
        book_id=book_id,
        title=data.title,
        author=data.author,
        stock=data.stock,
        price=data.price,
    )
    try:
        values = {}
        if data.title is not None:
            values["title"] = data.title
        if data.author is not None:
            values["author"] = data.author
        if data.stock is not None:
            values["stock"] = data.stock
        if data.price is not None:
            values["price"] = data.price

        if not values:
            logger.info("service_update_book_no_fields", book_id=book_id)
            return None

        result = await db.execute(
            update(Book).where(Book.id == book_id).values(**values).returning(Book)
        )
        book = result.scalar_one_or_none()
        await db.commit()

        if not book:
            logger.warning("service_update_book_not_found", book_id=book_id)
            return None

        logger.info("service_update_book_success", book_id=book_id)
        return book
    except Exception as e:
        logger.error("service_update_book_failed", book_id=book_id, error=str(e))
        raise


async def delete_book(book_id: int, db: AsyncSession):
    logger.info("service_delete_book_start", book_id=book_id)
    try:
        result = await db.execute(
            delete(Book).where(Book.id == book_id).returning(Book.id)
        )
        deleted_id = result.scalar_one_or_none()
        await db.commit()

        if deleted_id is None:
            logger.warning("service_delete_book_not_found", book_id=book_id)
            raise NoResultFound()

        logger.info("service_delete_book_success", book_id=book_id)
        return True
    except Exception as e:
        logger.error("service_delete_book_failed", book_id=book_id, error=str(e))
        raise
