from fastapi import APIRouter

from .delete import router as delete_router
from .download import router as download_router
from .list import router as list_router
from .move import router as move_router
from .rename import router as rename_router
from .upload import router as upload_router

router = APIRouter(prefix="/files", tags=["Files"])

router.include_router(delete_router)
router.include_router(download_router)
router.include_router(list_router)
router.include_router(move_router)
router.include_router(rename_router)
router.include_router(upload_router)