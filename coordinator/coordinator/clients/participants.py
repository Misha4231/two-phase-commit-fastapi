import httpx

from coordinator.core.logging import logger
from coordinator.core.settings import settings
from common.schemas.purchase import (
    PrepareResponse,
    UserCommitResponse,
    BookCommitResponse,
)

# --------------- HELPER HTTP FUNCTIONS FOR PREPARE AND COMMIT -------------------


async def prepare_user(
    transaction_id: str, user_id: int, amount: float
) -> PrepareResponse:
    logger.debug(
        "http_prepare_user",
        transaction_id=transaction_id,
        user_id=user_id,
        amount=amount,
    )
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.user_service_url}/purchase/prepare",
            json={
                "transaction_id": transaction_id,
                "user_id": user_id,
                "amount": amount,
            },
        )

        response.raise_for_status()

        return PrepareResponse.model_validate(response.json())


async def prepare_book(
    transaction_id: str, book_id: int, quantity: float
) -> PrepareResponse:
    logger.debug(
        "http_prepare_book",
        transaction_id=transaction_id,
        book_id=book_id,
        quantity=quantity,
    )
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.book_service_url}/purchase/prepare",
            json={
                "transaction_id": transaction_id,
                "book_id": book_id,
                "quantity": quantity,
            },
        )

        response.raise_for_status()

        return PrepareResponse.model_validate(response.json())


async def commit_user(transaction_id: str) -> UserCommitResponse:
    logger.debug("http_commit_user", transaction_id=transaction_id)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.user_service_url}/purchase/commit",
            json={"transaction_id": transaction_id},
        )

        response.raise_for_status()
        return UserCommitResponse.model_validate(response.json())


async def commit_book(transaction_id: str) -> BookCommitResponse:
    logger.debug("http_commit_book", transaction_id=transaction_id)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.book_service_url}/purchase/commit",
            json={"transaction_id": transaction_id},
        )

        response.raise_for_status()
        return BookCommitResponse.model_validate(response.json())


async def rollback_user(transaction_id: str) -> None:
    logger.debug("http_rollback_user", transaction_id=transaction_id)
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{settings.user_service_url}/purchase/rollback",
                json={"transaction_id": transaction_id},
            )
        except Exception as e:
            logger.error(
                "http_rollback_user_failed", transaction_id=transaction_id, error=str(e)
            )


async def rollback_book(transaction_id: str) -> None:
    logger.debug("http_rollback_book", transaction_id=transaction_id)
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{settings.book_service_url}/purchase/rollback",
                json={"transaction_id": transaction_id},
            )
        except Exception as e:
            logger.error(
                "http_rollback_book_failed", transaction_id=transaction_id, error=str(e)
            )
