import httpx
from loguru import logger
from openai import AsyncOpenAI
from app.models.domain.rag import EmbeddingResponse, ChunkModel


class EmbeddingService:
    DEFAULT_MODEL = "text-embedding-v4"
    BATCH_SIZE = 10

    def __init__(
            self,
            api_url: str,
            api_key: str,
            model: str | None = None
    ) -> None:
        self.api_key = api_key
        self.api_url = api_url
        self.model = model or self.DEFAULT_MODEL

    async def embed_texts(
            self,
            texts: list[str]
    ) -> list[list[float]]:
        if not texts:
            return []

        results: list[list[float]] = [()] * len(texts)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            for i in range(0, len(texts), self.BATCH_SIZE):
                batch = texts[i : i + self.BATCH_SIZE]
                payload = {
                    "model": self.model,
                    "input": batch,
                }
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = EmbeddingResponse.model_validate(response.json())

                for item in data.data:
                    results[item.index + i] = item.embedding

                logger.debug(
                    f"[Embedding] 批次 {i//self.BATCH_SIZE + 1} 完成，"
                    f"嵌入 {len(batch)} 条文本"
                )
        return results

    async def embed_chunks(
        self,
        document_id:int,
        chunks: list[dict],
    ) ->list[ChunkModel]:
        texts = []
        for chunk in chunks:
            texts.append(chunk["context"])

        vectors = await self.embed_texts(texts)

        indexed_chunks = []
        for idx, chunk,vector in zip(range(len(chunks)),chunks,vectors):
            index_chunk = {**chunk,"document_id":document_id,"chunk_idx":idx,"embedding":vector}
            indexed_chunks.append(ChunkModel(**index_chunk))

        logger.debug(
            f"[Embedding] 完成 {len(chunks)} 个 chunk 的向量化"
        )
        return indexed_chunks

    async def ueser_question(
            self,
            question_content:str
    )->list[float]:
        wrap_text = [question_content]
        results = await self.embed_texts(wrap_text)
        return results[0]


class OpenAiService:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
    ):
        self.api_key = api_key
        self.base_url:str = base_url
        self.model = model

    async def openai_api(
        self,
        content:str,
        debug=False
    )->str:
        client = AsyncOpenAI(
            # 如果没有配置环境变量，请用阿里云百炼API Key替换：api_key="sk-xxx"
            api_key=self.api_key,
            base_url=self.base_url,
        )

        messages = [{"role": "user", "content": f"{content}"}]
        completion = client.chat.completions.create(
            model="qwen3.5-plus",  # 您可以按需更换为其它深度思考模型
            messages=messages,
            extra_body={"enable_thinking": False},
            stream=True
        )
        async for chunk in await completion:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if debug:
                if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
                    print("\n" + "=" * 20 + "思考过程" + "=" * 20)
                    print(delta.reasoning_content, end="", flush=True)
                    yield delta.reasoning_content
            if hasattr(delta, "content") and delta.content:
                yield delta.content