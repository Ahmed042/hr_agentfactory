"""Webhook management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user
from app.models.user import User
from app.api.webhooks.webhook_handler import (
    register_webhook, unregister_webhook, list_webhooks, WEBHOOK_EVENTS
)
from pydantic import BaseModel

router = APIRouter()


class WebhookRegister(BaseModel):
    event: str
    url: str


@router.get("/events")
def get_webhook_events():
    """List all supported webhook event types"""
    return {"events": WEBHOOK_EVENTS}


@router.get("/")
def get_webhooks(current_user: User = Depends(get_current_user)):
    """List all registered webhooks (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return list_webhooks()


@router.post("/register")
def register_webhook_endpoint(
    data: WebhookRegister,
    current_user: User = Depends(get_current_user),
):
    """Register a webhook URL for an event"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    if data.event not in WEBHOOK_EVENTS:
        raise HTTPException(status_code=400, detail=f"Unknown event. Supported: {', '.join(WEBHOOK_EVENTS)}")

    register_webhook(data.event, data.url)
    return {"message": f"Webhook registered for {data.event}", "url": data.url}


@router.post("/unregister")
def unregister_webhook_endpoint(
    data: WebhookRegister,
    current_user: User = Depends(get_current_user),
):
    """Unregister a webhook URL"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    unregister_webhook(data.event, data.url)
    return {"message": f"Webhook unregistered for {data.event}"}
