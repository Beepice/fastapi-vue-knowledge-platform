-- name: create-document-chunks<!
INSERT INTO document_chunks
    (document_id,context,chunk_idx,page_start,page_end,figure_refs,embedding)
VALUES (
    :document_id,
    :context,
    :chunk_idx,
    :page_start,
    :page_end,
    :figure_refs::text[],
    :embedding::vector
    )
RETURNING id,context,document_id,chunk_idx,page_start,page_end,figure_refs::text[],embedding

-- name: delete-document-chunks-by-document!
DELETE FROM document_chunks
WHERE document_id = :document_id

-- name: create-figures<!
INSERT INTO figures
    (img_path, document_id , figure_content)
VALUES (:img_path, :document_id, :figure_content)
RETURNING id, img_path, document_id, figure_content

-- name: delete-figures!
DELETE FROM figures
WHERE id = :figure_id

-- name: delete-figures-by-documents!
DELETE FROM figures
WHERE document_id = :document_id

-- name: get-figures
SELECT
    id,
    img_path,
    figure_content
FROM figures
WHERE id = ANY(:figure_ids)

-- name: create-chunks-figures<!
INSERT INTO chunks_figures
    (chunks_id, figures_id)
VALUES (:chunks_id, :figures_id)
ON CONFLICT DO NOTHING

-- name: get-figures-by-chunks
SELECT
    id,
    img_path,
    figure_content
FROM figures
INNER JOIN chunks_figures cf ON id == cf.figures_id
WHERE cf.chunks_id = ANY(:chunks_id)

-- name: get-document-chunks-by-documents
SELECT
    id,
    document_id,
    context,
    chunk_idx,
    page_start,
    page_end,
    figure_refs::text[],
    embedding::vector
FROM document_chunks
WHERE document_id = ANY(:document_ids)
ORDER BY document_id,page_start,chunk_idx

-- name: search-chunks-by-embedding
SELECT
    id,
    document_id,
    context,
    chunk_idx,
    page_start,
    page_end,
    figure_refs::text[],
    embedding::vector <=> :query_embedding::vector AS cos_distance
FROM document_chunks
WHERE embedding::vector <=> :query_embedding::vector < 0.4
LIMIT :top_k
