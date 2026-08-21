from typing import List,Optional
from app.db.errors import EntityDoesNotExist
from app.db.queries.queries import queries
from app.db.repositories.base import BaseRepository
from app.models.domain.documents import ToolModel, VersionModel, DocumentsModel, TagsModel, DocumentTagsModel

class DocumentsRepository(BaseRepository):
    async def get_or_create_tool_id(
        self,
        *,
        tool_name: str,
    ) -> ToolModel:
        tool_id = await queries.get_tool_by_name(
            self.connection,
            tool_name=tool_name
        )
        if not tool_id:
            tool_id = await queries.create_new_tool(
                self.connection,
                tool_name=tool_name
            )
        return ToolModel(**tool_id)

    async def get_or_create_version_id(
        self,
        *,
        tool_name: str,
        tool_version: str,
    ) -> VersionModel:
        tool_version_id = await queries.get_version_id(
            self.connection,
            tool_name=tool_name,
            tool_version=tool_version
        )
        if not tool_version_id:
            tool_version_id = await queries.create_new_version(
                self.connection,
                tool_name=tool_name,
                tool_version=tool_version
            )
        return VersionModel(**tool_version_id)

    async def create_new_document(
        self,
        *,
        title: str,
        file_path: str,        # 前端传的工具名
        version_id: int,     # 前端传的版本号
        uploaded_by: str,         # 用户 ID
    ) -> DocumentsModel:
        document_row = await queries.create_new_document(
            self.connection,
            title=title,
            file_type='pdf',
            file_path=file_path,
            version_id=version_id,
            uploaded_by=uploaded_by
        )
        if document_row:
            return DocumentsModel(
                **document_row
            )
        raise EntityDoesNotExist(
            "Documents {0} can not be created".format(title),
        )
    async def get_document(
        self,
        *,
        title: str,
        tool_name: str,
        tool_version:str,     # 前端传的版本号

    ) -> DocumentsModel:
        document_row = await queries.get_document(
            self.connection,
            title=title,
            tool_name=tool_name,
            tool_version=tool_version,
        )
        if document_row:
            return DocumentsModel(
                **document_row
            )
        raise EntityDoesNotExist(
            "Can not get Documents {0} ".format(title),
        )

    async def create_new_dft_tag(
        self,
        *,
        tag_name:str
    )->TagsModel:
        tag = await queries.get_dft_tag(self.connection,tag_name=tag_name)
        if not tag:
            tag = await queries.create_new_dft_tag(self.connection,tag_name=tag_name)
        return TagsModel(**tag)

    async def create_document_dft_tags(
        self,
        *,
        tag_names:List[str],
        document_id:int,
    )->List[DocumentTagsModel]:
        results = []
        for tag_name in tag_names:
            await self.create_new_dft_tag(tag_name=tag_name)
            document_tags = await queries.create_document_dft_tag(
                self.connection,
                documents_id=document_id,
                tag_name=tag_name
            )
            results.append(document_tags)
        return results

    """文档筛选查询部分"""
    async def get_all_tools(
        self,
    )->List[ToolModel]:
        all_tools_row = await queries.get_all_tools(
            self.connection
        )
        return [ToolModel(**row) for row in all_tools_row]
    async def get_tool_by_id(
        self,
        *,
        tool_id: int
    )->ToolModel:
        tools_row = await queries.get_tool_by_id(
            self.connection,
            tool_id=tool_id
        )
        return ToolModel(**tools_row)

    async def get_versions_by_tool_id(
        self,
        *,
        tool_id: int
    )->List[VersionModel]:
        tool_versions = []
        tool_versions_row = await queries.get_versions_by_tool_id(
            self.connection,
            tool_id=tool_id)
        return [VersionModel(**dict(row)) for row in tool_versions_row]

    async def get_documents(
        self,
        *,
        version_id: int,
        document_id: Optional[int] = None
    )->List[DocumentsModel]:
        documents_row = await queries.get_documents(
            self.connection,
            version_id=version_id,
            document_id=document_id
        )
        return [DocumentsModel(**dict(row)) for row in documents_row]

    async def get_document_by_id(
        self,
        *,
        document_id: int
    )->DocumentsModel:
        document_row = await queries.get_document_by_id(
            self.connection,
            document_id=document_id
        )
        return DocumentsModel(**dict(document_row))