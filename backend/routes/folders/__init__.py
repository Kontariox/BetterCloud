from fastapi import APIRouter

from .create import router as create_router
from .list import router as list_router
from .delete import router as delete_router
from .move import router as move_router
from .rename import router as rename_router

router = APIRouter(prefix="/folders", tags=["Folders"])

router.include_router(create_router)
router.include_router(list_router)
router.include_router(delete_router)
router.include_router(move_router)
