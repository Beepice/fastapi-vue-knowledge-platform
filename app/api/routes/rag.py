from fastapi import Body,APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.db.repositories.rag import EmbeddingRepository
from app.db.repositories.documents import DocumentsRepository
from app.api.dependencies.database import get_repository
from app.api.dependencies.rag import user_question,parse_pdf,user_question_to_api
from app.models.domain.rag import UserQuestionModel, UserQuestionResponse

router = APIRouter()

@router.get("/versions/{version_id}/documents/{document_id}/test")
async def pasre_pdf(
    version_id: int,
    document_id: int,
    docu_repo: DocumentsRepository = Depends(get_repository(DocumentsRepository)),
    emb_repo: EmbeddingRepository = Depends(get_repository(EmbeddingRepository)),
):
    documents = await docu_repo.get_documents(version_id=version_id,document_id=document_id)
    if documents:
        await parse_pdf(document_id,documents[0].file_path,emb_repo)

@router.get("/embeddings/question/test")
async def search_question_embeddings(
        question:str,
        top_k:int = 5,
        emb_repo: EmbeddingRepository = Depends(get_repository(EmbeddingRepository))
):
    await user_question(question,top_k,emb_repo)

@router.post("/embeddings/question/ask")
async def user_question(
        user_q:UserQuestionModel = Body(..., embed=True, alias="params"),
        emb_repo: EmbeddingRepository = Depends(get_repository(EmbeddingRepository)),
        docu_repo: DocumentsRepository = Depends(get_repository(DocumentsRepository))
)->StreamingResponse:
    question = user_q.question
    top_k = user_q.top_k
    async def generate():
        async for chunk in user_question_to_api(
            question= question,
            top_k= top_k,
            embedding_repo= emb_repo,
            docu_repo= docu_repo
        ):
            # 每个 chunk 包装成 SSE 格式
            yield f"{chunk}\n\n"
            # 结束标记,最后一次yield借出
        yield "[DONE]\n\n"
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )