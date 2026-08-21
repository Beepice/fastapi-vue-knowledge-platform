from fastapi import APIRouter

from app.api.routes import authentication, users,documents,rag

router = APIRouter()
router.include_router(authentication.router, tags=["authentication"], prefix="/users")
router.include_router(users.router, tags=["users"], prefix="/user")
router.include_router(documents.router, tags=["documents"], prefix="/documents")
router.include_router(rag.router, tags=["rag"], prefix="/rag")
