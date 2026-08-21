from app.db.repositories.base import BaseRepository
from app.db.queries.queries import queries
from app.models.domain.rag import ChunkModel,ChunkDBModel,FigureModel,FigureDBModel,QuestionDBModel
from typing import Sequence, Optional
from os.path import basename,splitext


class EmbeddingRepository(BaseRepository):
    async def create_document_chunks(
        self,
        *,
        document_id: int,
        context: str,
        chunk_idx: int,
        page_start: int,
        page_end: int,
        figure_refs: list[str],
        embedding: list[float]
    ):
        """创建单个 document chunk"""
        return await queries.create_document_chunks(
            self.connection,
            document_id=document_id,
            context=context,
            chunk_idx=chunk_idx,
            page_start=page_start,
            page_end=page_end,
            figure_refs=figure_refs,
            embedding=embedding
        )

    async def create_document_chunks_batch(
        self,
        *,
        chunks: list[dict]
    ) -> list[ChunkDBModel]:
        """批量创建 document chunks"""
        results = []
        for chunk in chunks:
            result = await self.create_document_chunks(
                document_id=chunk["document_id"],
                context=chunk["context"],
                chunk_idx=chunk["chunk_idx"],
                page_start=chunk["page_start"],
                page_end=chunk["page_end"],
                figure_refs=chunk["figure_refs"],
                embedding=chunk["embedding"]
            )
            results.append(
                ChunkDBModel(
                    id=result["id"],
                    document_id=result["document_id"],
                    context=result["context"],
                    chunk_idx=result["chunk_idx"],
                    page_start=chunk["page_start"],
                    page_end=chunk["page_end"],
                    figure_refs=chunk["figure_refs"],
                    embedding=result["embedding"].to_list()
                ))
        return results

    async def delete_document_chunks_by_document(
        self,
        *,
        document_id: int
    ) -> None:
        """删除某文档的所有 chunks"""
        await queries.delete_document_chunks_by_document(
            self.connection,
            document_id=document_id
        )

    async def create_figure(
        self,
        *,
        img_path: str,
        document_id: int,
        figure_content: Optional[str] = None
    ):
        """创建单个 figure"""
        return await queries.create_figures(
            self.connection,
            img_path=img_path,
            document_id=document_id,
            figure_content=figure_content
        )

    async def create_figures_batch(
        self,
        *,
        figures: list[dict]
    ) -> list[FigureDBModel]:
        """批量创建 figures"""
        results = []
        for figure in figures:
            result = await self.create_figure(
                img_path=figure["img_path"],
                document_id=figure["document_id"],
                figure_content=figure.get("figure_content")
            )
            results.append(FigureDBModel(**result))
        return results

    async def delete_figure(
        self,
        *,
        figure_id: int
    ) -> None:
        """删除单个 figure"""
        await queries.delete_figures(
            self.connection,
            figure_id=figure_id
        )

    async def delete_figures_by_documents(
        self,
        *,
        document_id: int
    ) -> None:
        """批量删除某文档的所有 figures"""
        await queries.delete_figures_by_documents(
            self.connection,
            document_id=document_id
        )

    async def get_figures(
        self,
        *,
        figure_ids: Sequence[int]
    ) -> Sequence[dict]:
        """批量获取 figures"""
        return await queries.get_figures(
            self.connection,
            figure_ids=figure_ids
        )

    async def create_chunks_figures(
        self,
        *,
        chunks_id: int,
        figures_id: int
    ) -> None:
        """创建 chunk 和 figure 的关联"""
        await queries.create_chunks_figures(
            self.connection,
            chunks_id=chunks_id,
            figures_id=figures_id
        )

    async def create_chunks_figures_batch(
        self,
        *,
        created_chunks:list[dict],
        created_figures: list[dict]
    ) -> None:
        """批量创建 chunk-figure 关联"""
        for chunk in created_chunks:
            figures_ref = chunk["figure_refs"]
            for figure in created_figures:
                figure_name = splitext(basename(figure["img_path"]))[0]
                if figure_name in figures_ref:
                    await self.create_chunks_figures(
                        chunks_id=chunk["id_"],
                        figures_id=figure["id_"]
                    )


    async def get_figures_by_chunks(
        self,
        *,
        chunk_ids: Sequence[int]
    ) -> Sequence[dict]:
        """通过 chunks 获取关联的 figures"""
        return await queries.get_figures_by_chunks(
            self.connection,
            chunks_id=chunk_ids
        )

    async def get_document_chunks_by_documents(
        self,
        *,
        document_ids: Sequence[int]
    ) -> Sequence[dict]:
        """批量获取文档的 chunks"""
        return await queries.get_document_chunks_by_documents(
            self.connection,
            document_ids=document_ids
        )

    async def search_chunks_by_embedding(
        self,
        *,
        query_embedding: list[float],
        top_k: int = 5
    ) -> list[QuestionDBModel]:
        """向量搜索最相似的 chunks"""
        results = await queries.search_chunks_by_embedding(
            self.connection,
            query_embedding=query_embedding,
            top_k=top_k
        )
        return [QuestionDBModel(**result) for result in results]

    async def upsert_document_embedding(
        self,
        *,
        document_id: int,
        chunks: list[ChunkModel],
        figures: list[FigureModel] | None,
    ) -> dict:
        # 1. 删除旧的 chunks（ON DELETE CASCADE 会自动清理 chunks_figures）
        await self.delete_document_chunks_by_document(
            document_id=document_id
        )

        # 2. 删除旧的 figures
        await self.delete_figures_by_documents(
            document_id=document_id
        )

        # 3. 插入新的 chunks
        created_chunks = await self.create_document_chunks_batch(
            chunks=[chunk.model_dump() for chunk in chunks],
        )

        # 4. 插入新的 figures
        created_figures = await self.create_figures_batch(
            figures=[figure.model_dump() for figure in figures],
        )

        # 5. 插入新的 chunk-figure 关联
        await self.create_chunks_figures_batch(
            created_chunks=[chunk.model_dump() for chunk in created_chunks],
            created_figures=[figure.model_dump() for figure in created_figures if figure]
        )

        return {
            "document_id": document_id,
            "chunks_count": len(created_chunks),
            "figures_count": len(created_figures),
        }
