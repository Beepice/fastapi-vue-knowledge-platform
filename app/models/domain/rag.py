from pydantic import BaseModel
from typing import Any
from app.models.common import IDModelMixin

class EmbeddingResult(BaseModel):
    """单条 embedding 结果"""
    embedding: list[float]
    index: int


class EmbeddingResponse(BaseModel):
    """Qwen API 响应格式"""
    data: list[EmbeddingResult]
    model: str
    usage: dict[str, Any]


class PdfBase(BaseModel):
    page_start: int
    page_end: int
    context: str

class PdfResponse(PdfBase):
    table_mds: list
    image_refs: list

class ChunkModel(PdfBase):
    document_id: int
    chunk_idx: int
    embedding: list[float]
    figure_refs: list[str] | None

class ChunkDBModel(IDModelMixin,ChunkModel):
    """数据库模型，figure_refs冗余字段，但是建立figures关联需要"""
    pass

class QuestionDBModel(IDModelMixin,PdfBase):
    document_id: int
    chunk_idx: int
    cos_distance:float
    figure_refs: list[str] | None

class FigureModel(BaseModel):
    document_id: int
    img_path: str
    figure_content: str | None

class FigureDBModel(IDModelMixin,FigureModel):
    pass

class ChunkFigureModel(BaseModel):
    chunks_id: int
    figures_id: int

class ChunkFigureDBModel(IDModelMixin,ChunkFigureModel):
    pass

class UserQuestionModel(BaseModel):
    top_k: int
    question: str

class UserQuestionResponse(BaseModel):
    answer:str