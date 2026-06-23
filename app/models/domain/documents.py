from app.models.domain.rwmodel import RWModel
from app.models.common import DateTimeModelMixin, IDModelMixin
from app.models.domain.users import User
from typing import Optional

class ToolModel(RWModel,IDModelMixin):
    tool_name: str

class VersionModel(RWModel,IDModelMixin):
    tool_version: str

class DocumentsModel(RWModel,IDModelMixin,DateTimeModelMixin,):
    title:str
    file_path:str
    version_id:int
    uploaded_by:int

class TagsModel(RWModel,IDModelMixin):
    name:str

class DocumentTagsModel(RWModel,IDModelMixin):
    document_id:int
    tag_id:int
