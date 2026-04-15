import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db, settings
from app.models import User
from app.models.tenant import Tenant, PlanTier
from app.auth import get_current_user, require_admin

router = APIRouter(prefix="/billing", tags=["Billing"], redirect_slashes=False)

# Plan limits applied when subscription activates
PLAN_LIMITS = {
    PlanTier.FREE:     {"email_limit": 1_000,  "sms_limit": 500},
    PlanTier.PRO:      {"email_limit": 50_000,  "sms_limit": 10_000},
    PlanTier.BUSINESS: {"email_limit": None,    "sms_limit": None},   # unlimited
}

PRICE_TO_PLAN = {}  # populated lazily from settings


def _price_to_plan_map():
    return {
        settings.stripe_price_pro: PlanTier.PRO,
        settings.stripe_price_business: PlanTier.BUSINESS,
    }


@router.get("/status")
async def billing_status(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Return the current plan and usage for the caller's tenant."""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    email_remaining = None
    sms_remaining = None
    if tenant.email_limit is not None:
        email_remaining = max(0, tenant.email_limit - tenant.email_sent)
    if tenant.sms_limit is not None:
        sms_remaining = max(0, tenant.sms_limit - tenant.sms_sent)

    return {
        "plan": tenant.plan.value,
        "email_limit": tenant.email_limit,
        "sms_limit": tenant.sms_limit,
        "email_sent": tenant.email_sent,
        "sms_sent": tenant.sms_sent,
        "email_remaining": email_remaining,
        "sms_remaining": sms_remaining,
        "has_stripe": bool(tenant.stripe_customer_id),
    }


@router.post("/create-checkout")
async def create_checkout_session(
    body: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Create a Stripe Checkout session for upgrading to PRO or BUSINESS.
    Returns a redirect URL the frontend should navigate to.
    """
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Billing not configured")

    plan_str = body.get("plan", "").upper()
    price_id_map = {
        "PRO": settings.stripe_price_pro,
        "BUSINESS": settings.stripe_price_business,
    }
    price_id = price_id_map.get(plan_str)
    if not price_id:
        raise HTTPException(status_code=400, detail="plan must be PRO or BUSINESS")

    success_url = body.get("success_url", "http://localhost:3000/billing?success=1")
    cancel_url = body.get("cancel_url", "http://localhost:3000/billing?cancelled=1")

    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    stripe.api_key = settings.stripe_secret_key

    # Create or reuse Stripe customer
    if not tenant.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=tenant.display_name or tenant.name,
            metadata={"tenant_id": str(tenant.id)},
        )
        tenant.stripe_customer_id = customer.id
        db.commit()

    session = stripe.checkout.Session.create(
        customer=tenant.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"tenant_id": str(tenant.id), "plan": plan_str},
    )

    return {"checkout_url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhook events.
    Activates plan on checkout.session.completed.
    Downgrades to FREE on subscription deletion/expiry.
    """
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Billing not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    price_plan_map = _price_to_plan_map()

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        tenant_id = session.get("metadata", {}).get("tenant_id")
        subscription_id = session.get("subscription")
        plan_str = session.get("metadata", {}).get("plan", "")
        new_plan = PlanTier[plan_str] if plan_str in PlanTier.__members__ else None

        if tenant_id and new_plan:
            tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if tenant:
                tenant.plan = new_plan
                tenant.stripe_subscription_id = subscription_id
                limits = PLAN_LIMITS[new_plan]
                tenant.email_limit = limits["email_limit"]
                tenant.sms_limit = limits["sms_limit"]
                db.commit()

    elif event["type"] in ("customer.subscription.deleted", "customer.subscription.paused"):
        subscription = event["data"]["object"]
        tenant = db.query(Tenant).filter(
            Tenant.stripe_subscription_id == subscription["id"]
        ).first()
        if tenant:
            tenant.plan = PlanTier.FREE
            tenant.stripe_subscription_id = None
            limits = PLAN_LIMITS[PlanTier.FREE]
            tenant.email_limit = limits["email_limit"]
            tenant.sms_limit = limits["sms_limit"]
            db.commit()

    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        tenant = db.query(Tenant).filter(
            Tenant.stripe_subscription_id == subscription["id"]
        ).first()
        if tenant:
            # Detect plan change via price ID
            items = subscription.get("items", {}).get("data", [])
            for item in items:
                price_id = item.get("price", {}).get("id")
                new_plan = price_plan_map.get(price_id)
                if new_plan:
                    tenant.plan = new_plan
                    limits = PLAN_LIMITS[new_plan]
                    tenant.email_limit = limits["email_limit"]
                    tenant.sms_limit = limits["sms_limit"]
                    db.commit()
                    break

    return {"status": "ok"}
