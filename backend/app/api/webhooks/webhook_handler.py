"""Webhook system for external integrations"""
import logging
import httpx
from typing import Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Webhook registry - configure via API or database
WEBHOOK_REGISTRY: dict = {}


async def trigger_webhook(event: str, payload: dict):
    """Fire webhook for a given event type"""
    webhooks = WEBHOOK_REGISTRY.get(event, [])
    if not webhooks:
        return

    async with httpx.AsyncClient(timeout=10.0) as client:
        for webhook_url in webhooks:
            try:
                response = await client.post(
                    webhook_url,
                    json={"event": event, "data": payload},
                    headers={"Content-Type": "application/json", "X-Webhook-Source": "HR-AgentFactory"},
                )
                logger.info(f"Webhook fired: {event} -> {webhook_url} (status: {response.status_code})")
            except Exception as e:
                logger.error(f"Webhook failed: {event} -> {webhook_url}: {e}")


def register_webhook(event: str, url: str):
    """Register a webhook URL for an event type"""
    if event not in WEBHOOK_REGISTRY:
        WEBHOOK_REGISTRY[event] = []
    if url not in WEBHOOK_REGISTRY[event]:
        WEBHOOK_REGISTRY[event].append(url)
        logger.info(f"Webhook registered: {event} -> {url}")


def unregister_webhook(event: str, url: str):
    """Remove a webhook URL for an event type"""
    if event in WEBHOOK_REGISTRY and url in WEBHOOK_REGISTRY[event]:
        WEBHOOK_REGISTRY[event].remove(url)


def list_webhooks() -> dict:
    """List all registered webhooks"""
    return WEBHOOK_REGISTRY.copy()


# Supported webhook events
WEBHOOK_EVENTS = [
    "candidate.created",
    "candidate.status_changed",
    "candidate.hired",
    "candidate.rejected",
    "interview.scheduled",
    "interview.completed",
    "employee.created",
    "payroll.generated",
    "leave.requested",
    "leave.approved",
    "leave.rejected",
]
