"""Banking API endpoints."""
from fastapi import APIRouter

from .banks import router as banks_router
from .connect import router as connect_router

router = APIRouter()
router.include_router(banks_router)
router.include_router(connect_router)
