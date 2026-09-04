"""
Stripe integration. Two rules this module follows on purpose:

1. The checkout endpoint ONLY creates a Stripe Checkout Session and returns
   its URL -- it never marks a user as subscribed. A user can close the tab
   before paying, so "session created" is not "payment succeeded."
2. The Subscription row is only ever written from the webhook handler,
   which is the one source of truth Stripe itself calls back into. This is
   the standard, safe pattern for any real billing integration.
"""

import uuid

import stripe
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.subscription import PlanTier, Subscription, SubscriptionStatus
from app.models.user import User

PLAN_TO_PRICE_ID = {
    "professional": lambda: settings.stripe_price_id_professional,
    "enterprise": lambda: settings.stripe_price_id_enterprise,
}

PLAN_NAME_TO_TIER = {
    "professional": PlanTier.PROFESSIONAL,
    "enterprise": PlanTier.ENTERPRISE,
}


def _require_stripe_configured():
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=503,
            detail="Billing is not configured on this server yet (missing STRIPE_SECRET_KEY).",
        )
    stripe.api_key = settings.stripe_secret_key


def get_or_create_subscription_row(db: Session, user: User) -> Subscription:
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub:
        sub = Subscription(user_id=user.id, plan=PlanTier.FREE, status=SubscriptionStatus.NONE)
        db.add(sub)
        db.commit()
        db.refresh(sub)
    return sub


def create_checkout_session(db: Session, user: User, plan: str) -> str:
    _require_stripe_configured()

    plan = plan.lower()
    if plan not in PLAN_TO_PRICE_ID:
        raise HTTPException(status_code=400, detail=f"Unknown plan {plan}. Use professional or enterprise.")

    price_id = PLAN_TO_PRICE_ID[plan]()
    if not price_id:
        raise HTTPException(status_code=503, detail=f"No Stripe price configured for plan {plan}.")

    sub_row = get_or_create_subscription_row(db, user)

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer_email=user.email if not sub_row.stripe_customer_id else None,
        customer=sub_row.stripe_customer_id or None,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{settings.frontend_url}/?checkout=success",
        cancel_url=f"{settings.frontend_url}/?checkout=canceled",
        client_reference_id=str(user.id),
        metadata={"user_id": str(user.id), "plan": plan},
    )
    return session.url


def handle_webhook_event(db: Session, payload: bytes, sig_header: str) -> None:
    _require_stripe_configured()

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        user_id = data.get("client_reference_id") or data.get("metadata", {}).get("user_id")
        plan_name = data.get("metadata", {}).get("plan", "professional")
        if user_id:
            sub = db.query(Subscription).filter(Subscription.user_id == uuid.UUID(user_id)).first()
            if sub:
                sub.plan = PLAN_NAME_TO_TIER.get(plan_name, PlanTier.PROFESSIONAL)
                sub.status = SubscriptionStatus.ACTIVE
                sub.stripe_customer_id = data.get("customer")
                sub.stripe_subscription_id = data.get("subscription")
                db.commit()

    elif event_type in ("customer.subscription.updated", "customer.subscription.deleted"):
        stripe_sub_id = data.get("id")
        sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_sub_id).first()
        if sub:
            status = data.get("status")
            if status == "active":
                sub.status = SubscriptionStatus.ACTIVE
            elif status == "past_due":
                sub.status = SubscriptionStatus.PAST_DUE
            elif status in ("canceled", "unpaid", "incomplete_expired"):
                sub.status = SubscriptionStatus.CANCELED
                sub.plan = PlanTier.FREE
            db.commit()
