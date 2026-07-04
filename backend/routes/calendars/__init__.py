from fastapi import APIRouter

from .events import router as events_router
from .delete import router as delete_router

router = APIRouter(prefix="/calendar", tags=["Calendar"])

router.include_router(events_router)
router.include_router(delete_router)