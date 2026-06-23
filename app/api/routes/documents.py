from typing import List
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile,File,Form,HTTPException
from starlette.responses import FileResponse
from starlette.status import HTTP_201_CREATED,  HTTP_404_NOT_FOUND,HTTP_404_NOT_FOUND
from app.api.dependencies.documents import save_document
from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.db.repositories.documents import DocumentsRepository
from app.models.domain.users import User
from app.models.domain.documents import DocumentsModel,ToolModel,VersionModel

router = APIRouter()

@router.post("/upload_documents", response_model=DocumentsModel,status_code=HTTP_201_CREATED, name="documents:receive-document-pdf")
async def receive_document_pdf(
    user: User = Depends(get_current_user_authorizer()),  # jwt校验用户，避免非法侵入
    documents_repo: DocumentsRepository = Depends(get_repository(DocumentsRepository)),
    file: UploadFile = File(...),
    title: str = Form(...),
    tool_name: str = Form(...),
    tool_version: str = Form(...),
    tags: str = Form(...),
)->DocumentsModel:
    real_tags = tags.split(',')
    file_info: DocumentsModel = await save_document(
        file=file,
        title=title,
        tool_name=tool_name,
        tool_version=tool_version,
        tags=real_tags,
        user=user,
        documents_repo=documents_repo
    )
    return file_info

@router.get("/tools", response_model=List[ToolModel])
async def get_tools(
    repo: DocumentsRepository = Depends(get_repository(DocumentsRepository)),
)->List[ToolModel]:
    tools = await repo.get_all_tools()
    if not tools:
        raise HTTPException(status_code= HTTP_404_NOT_FOUND, detail="No tools found")
    return tools

@router.get("/tools/{tool_id}/versions", response_model=List[VersionModel])
async def get_tool_versions(
    tool_id: int,
    repo: DocumentsRepository = Depends(get_repository(DocumentsRepository)),
)->List[VersionModel]:
    versions = await repo.get_versions_by_tool_id(tool_id=tool_id)
    if not versions:
        raise HTTPException(status_code= HTTP_404_NOT_FOUND, detail="No versions found")
    return versions

@router.get("/versions/{version_id}/documents", response_model=List[DocumentsModel])
async def get_version_documents(
    version_id: int,
    repo: DocumentsRepository = Depends(get_repository(DocumentsRepository)),
)->List[DocumentsModel]:
    documents = await repo.get_documents(version_id=version_id)
    if not documents:
        raise HTTPException(status_code= HTTP_404_NOT_FOUND, detail="No documents found")
    return documents

@router.get("/versions/{version_id}/documents/{document_id}", response_model=DocumentsModel)
async def get_document(
    version_id: int,
    document_id: int,
    repo: DocumentsRepository = Depends(get_repository(DocumentsRepository)),
):
    document = await repo.get_documents(version_id=version_id,document_id=document_id)
    if not document:
        raise HTTPException(status_code= HTTP_404_NOT_FOUND, detail="No documents found")
    return document[0]

@router.get("/versions/{version_id}/documents/{document_id}/file")
async def get_document_file(
    version_id: int,
    document_id: int,
    repo: DocumentsRepository = Depends(get_repository(DocumentsRepository)),
):
    document = await repo.get_documents(version_id=version_id,document_id=document_id)
    if not document:
        raise HTTPException(status_code= HTTP_404_NOT_FOUND, detail="No documents found")
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    file_path = root_dir / Path(document[0].file_path)
    if not file_path.exists():
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(file_path, media_type="application/pdf")

