from app.models.domain.rag import QuestionDBModel
from app.db.repositories.documents import DocumentsRepository

PROMPT_TEMPLATE = """
你是一个专业的知识库助手。请严格基于下面的资料使用中文回答用户问题。
【回答规则】
1. 基于参考文档,使用中文回答
2. 必须给出参考文档的来源，需要文档名和页码:
3. 没找到相关资料必须指明"信息不足"
4. 简洁明了，步骤尽量清晰

【参考资料】
{references}

【用户问题】
{question}

"""

async def build_prompt_text(
        question: str,
        querys:list[QuestionDBModel],
        document_repo:DocumentsRepository
)->str:
    record_documents = []
    for i,query in enumerate(querys):
        document_id = query.document_id
        document =await document_repo.get_document_by_id(document_id=document_id)
        document_name = document.title

        text = query.context
        page_number = f"{query.page_start}-{query.page_end}"
        record_document = (f"[{i+1}]"
                           f"文档名:{document_name}"
                           f"页码:{page_number}"
                           f"内容：\n{text}")
        record_documents.append(record_document)
    return PROMPT_TEMPLATE.format(references="\n".join(record_documents),question=question)