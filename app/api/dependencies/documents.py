import uuid
from pathlib import Path
from os import remove
from fastapi import UploadFile
from app.core.config import get_app_settings
from app.db.repositories.documents import DocumentsRepository
from app.models.domain.documents import VersionModel,DocumentsModel
from app.models.domain.users import User


HEADER_KEY = "Authorization"
UPLOAD_DIR = get_app_settings().upload_dir



async def _save_document_file(
        file: UploadFile
)-> str:
    ext = Path(file.filename).suffix  # .pdf
    unique_name = f"{uuid.uuid4()}{ext}"

    root_dir:Path = Path(__file__).resolve().parent.parent.parent.parent
    file_path:str =  f"{UPLOAD_DIR}/{unique_name}"
    real_file_dir:Path = root_dir / UPLOAD_DIR
    real_file_dir.mkdir(parents=True, exist_ok=True)

    with open(root_dir / file_path, "wb") as file_temp:
        content = await file.read()
        file_temp.write(content)

    return str(file_path)

async def _delete_document_file(
        *,
        file_path: str,
)->bool:
    remove(file_path)
    return True

async def _save_document_info(
        *,
        title: str,
        tool_name: str,
        tool_version: str,
        tags: list[str],
        documents_repo,
        user: User,
        file_path: str #文件存储完毕后录入信息
)->DocumentsModel:
    """接收数据模型参数，录入文件信息到数据库"""
    await documents_repo.get_or_create_tool_id(
        tool_name=tool_name
    )
    tool_version_id: VersionModel = await documents_repo.get_or_create_version_id(
        tool_name=tool_name,
        tool_version=tool_version
    )
    new_document = await documents_repo.create_new_document(
        title=title,
        file_path=file_path,
        version_id=tool_version_id.id_,
        uploaded_by=user.username
    )
    if new_document:
        await documents_repo.create_document_dft_tags(
            document_id=new_document.id_,
            tag_names=tags
        )
    return new_document

async def save_document(
    *,
    file: UploadFile,
    title: str,
    tool_name: str,
    tool_version: str,
    tags: list[str],
    documents_repo: DocumentsRepository,
    user: User,
)->DocumentsModel:
    file_path = await _save_document_file(file=file)
    document_info = await _save_document_info(
        file_path=file_path,
        title=title,
        tool_name=tool_name,
        tool_version=tool_version,
        tags=tags,
        documents_repo=documents_repo,
        user=user,
    )
    if not document_info:
        await _delete_document_file(file_path=file_path)
    return document_info

