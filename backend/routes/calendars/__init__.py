from fastapi import APIRouter

from .list import router as list_router
from .delete import router as delete_router
from .create import router as create_router

router = APIRouter(prefix="/calendar", tags=["Calendar"])

router.include_router(list_router)
router.include_router(create_router)
router.include_router(delete_router)