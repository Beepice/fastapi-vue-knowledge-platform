from pathlib import Path

from app.db.repositories.documents import DocumentsRepository
from app.models.domain.rag import FigureModel, QuestionDBModel
from app.services.rag import EmbeddingService,OpenAiService
from app.core.config import get_app_settings
from app.services.pdf_extract import PDFParser
from app.db.repositories.rag import EmbeddingRepository
from app.services.build_prompt import build_prompt_text

QWEN_3_5_PLUS_URL = get_app_settings().qwen_3_5_plus_url
QWEN_QUESTION_MODEL = get_app_settings().qwen_question_model
QWEN_API_URL = get_app_settings().qwen_api_url
QWEN_API_KEY = get_app_settings().qwen_api_key.get_secret_value()
QWEN_EMBEDDING_MODEL = get_app_settings().qwen_embedding_model
FIG_SAVE_PATH = get_app_settings().fig_save_dir

async def parse_pdf(
        document_id:int,
        pdf_path:str,
        embedding_repo: EmbeddingRepository,
):
    root_dir: Path = Path(__file__).resolve().parent.parent.parent.parent
    file_path = root_dir / pdf_path
    parsed_chunks:list[dict] | None = None
    parsed_figures:list[FigureModel] | None = None
    with PDFParser() as parser:
        parser.run_parse(document_id,file_path,FIG_SAVE_PATH)
        parsed_chunks = [chunk for chunk in parser.extract_chunks() if len(chunk["context"]) <10000]
        parsed_figures = parser.extract_figures()

    if parsed_chunks:
        embedding_service =  EmbeddingService(QWEN_API_URL, QWEN_API_KEY, QWEN_EMBEDDING_MODEL)
        all_chunks = await embedding_service.embed_chunks(document_id,parsed_chunks)
        await embedding_repo.upsert_document_embedding(
            document_id=document_id,
            chunks=all_chunks,
            figures=parsed_figures)

async def user_question(
        question:str,
        top_k:int,
        embedding_repo: EmbeddingRepository
)->list[QuestionDBModel]:
    embedding_service = EmbeddingService(QWEN_API_URL, QWEN_API_KEY, QWEN_EMBEDDING_MODEL)
    question_response = await embedding_service.ueser_question(question)
    search_response = await embedding_repo.search_chunks_by_embedding(query_embedding=question_response,top_k=top_k)
    return search_response


async def user_question_to_api(
        embedding_repo: EmbeddingRepository,
        docu_repo: DocumentsRepository,
        question: str,
        top_k: int = 5
)->str:
    search_response = await user_question(
        question,
        top_k,
        embedding_repo
    )
    to_api_content = await build_prompt_text(
        question=question,
        querys=search_response,
        document_repo=docu_repo
    )
    openai_service = OpenAiService(api_key=QWEN_API_KEY,base_url=QWEN_3_5_PLUS_URL,model=QWEN_QUESTION_MODEL)
    async for chunk in openai_service.openai_api(to_api_content):
        yield chunk

