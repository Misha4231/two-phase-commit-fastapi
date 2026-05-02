from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from common.core.database import get_db
from book_service.schemas.book import BookCreate, BookOut, BookUpdate
from book_service.services import books as book_service
from book_service.core.logging import logger

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=list[BookOut])
async def get_books(db: AsyncSession = Depends(get_db)):
    logger.info("get_books_start")
    try:
        books = await book_service.get_all_books(db)
        logger.info("get_books_success", books_count=len(books))
        return books
    except Exception as e:
        logger.error("get_books_failed", error=str(e))
        raise


@router.get("/{book_id}", response_model=BookOut)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    logger.info("get_book_start", book_id=book_id)
    try:
        book = await book_service.get_book(book_id, db)
        logger.info("get_book_success", book_id=book_id)
        return book
    except NoResultFound:
        logger.warning("get_book_not_found", book_id=book_id)
        raise HTTPException(status_code=404, detail="Book not found")
    except Exception as e:
        logger.error("get_book_error", book_id=book_id, error=str(e))
        raise HTTPException(status_code=500)


@router.post("/", response_model=BookOut)
async def create_book(data: BookCreate, db: AsyncSession = Depends(get_db)):
    logger.info(
        "create_book_start",
        title=data.title,
        author=data.author,
        stock=data.stock,
        price=data.price,
    )
    try:
        book = await book_service.create_book(data, db)
        logger.info("create_book_success", book_id=book.id)
        return JSONResponse(content=jsonable_encoder(book), status_code=201)
    except Exception as e:
        logger.error("create_book_failed", error=str(e))
        raise


@router.put("/{book_id}", response_model=BookOut)
async def update_book(
    book_id: int, data: BookUpdate, db: AsyncSession = Depends(get_db)
):
    logger.info(
        "update_book_start",
        book_id=book_id,
        title=data.title,
        author=data.author,
        stock=data.stock,
        price=data.price,
    )
    try:
        book = await book_service.update_book(book_id, data, db)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        logger.info("update_book_success", book_id=book_id)
        return book
    except HTTPException:
        logger.warning("update_book_not_found", book_id=book_id)
        raise
    except Exception as e:
        logger.error("update_book_failed", book_id=book_id, error=str(e))
        raise


@router.delete("/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    logger.info("delete_book_start", book_id=book_id)
    try:
        await book_service.delete_book(book_id, db)
        logger.info("delete_book_success", book_id=book_id)
        return Response(status_code=204)
    except NoResultFound:
        logger.warning("delete_book_not_found", book_id=book_id)
        raise HTTPException(status_code=404, detail="Book not found")
    except Exception as e:
        logger.error("delete_book_error", book_id=book_id, error=str(e))
        raise HTTPException(status_code=500)
