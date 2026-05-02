from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException

from coordinator.schemas.purchase import PurchaseRequest, PurchaseResponse
from coordinator.core.logging import logger
from coordinator.services import purchases as purchase_service
from coordinator.core.exceptions import (
    InsufficientBalanceError,
    InsufficientStockError,
    CommitError,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/purchase", response_model=PurchaseResponse)
async def purchase(request: PurchaseRequest):
    logger.info(
        "route_purchase_start",
        user_id=request.user_id,
        book_id=request.book_id,
        quantity=request.quantity,
    )

    try:
        result = await purchase_service.purchase(request)
        logger.info(
            "route_purchase_success", user_id=request.user_id, book_id=request.book_id
        )
        return result
    except InsufficientStockError as e:
        logger.warning("route_purchase_insufficient_stock", detail=str(e))
        raise HTTPException(status_code=409, detail=str(e))
    except InsufficientBalanceError as e:
        logger.warning("route_purchase_insufficient_balance", detail=str(e))
        raise HTTPException(status_code=402, detail=str(e))
    except CommitError as e:
        logger.error("route_purchase_commit_error", detail=str(e))
        raise HTTPException(status_code=500, detail="Transaction failed during commit")
    except Exception as e:
        logger.error("route_purchase_unexpected_error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
