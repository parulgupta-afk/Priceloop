from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.billing import CheckoutRequest, CheckoutResponse, SubscriptionOut
from app.services import billing_service

router = APIRouter()


@router.post("/create-checkout-session", response_model=CheckoutResponse)
def create_checkout_session(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    url = billing_service.create_checkout_session(db, current_user, payload.plan)
    return CheckoutResponse(checkout_url=url)


@router.get("/subscription", response_model=SubscriptionOut)
def get_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return billing_service.get_or_create_subscription_row(db, current_user)


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    billing_service.handle_webhook_event(db, payload, sig_header)
    return {"received": True}
