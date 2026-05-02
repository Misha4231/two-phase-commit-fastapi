from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from common.core.database import get_db

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/")
async def get_books(db: AsyncSession = Depends(get_db)):
    return "ok"
