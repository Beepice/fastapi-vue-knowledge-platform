-- name: get-tool-by-name^
SELECT id,
       tool_name
FROM tools
WHERE tool_name = :tool_name
LIMIT 1;

-- name: get-tool-by-id^
SELECT id,
       tool_name
FROM tools
WHERE id = :id
LIMIT 1;

-- name: get-all-tools
SELECT id,
       tool_name
FROM tools
ORDER BY tool_name;

-- name: create-new-tool<!
INSERT INTO tools (tool_name)
VALUES (:tool_name)
ON CONFLICT DO NOTHING
RETURNING id, tool_name;

-- name: get-version-id^
SELECT v.id,
       v.tool_version
FROM versions v
INNER JOIN tools t ON
    v.tool_id = t.id
WHERE tool_version = :tool_version AND
    t.tool_name = :tool_name
LIMIT 1;

-- name: get-versions-by-tool-id
SELECT v.id,
       v.tool_version
FROM versions v
INNER JOIN tools t ON
    v.tool_id = t.id
WHERE t.id = :tool_id

-- name: create-new-version<!
INSERT INTO versions (tool_version,tool_id)
SELECT :tool_version, t.id
FROM tools t
WHERE t.tool_name = :tool_name
ON CONFLICT DO NOTHING
RETURNING id, tool_version;

-- name: create-new-document<!
INSERT INTO documents
        (title,file_type,file_path,version_id,uploaded_by)
SELECT
    :title,
    :file_type,
    :file_path,
    :version_id,
    (SELECT id FROM users WHERE username = :uploaded_by) AS uploaded_by
ON CONFLICT DO NOTHING
RETURNING
    id,title,file_type,file_path,version_id,uploaded_by,created_at,updated_at;

-- name: get-document^
SELECT d.id,d.title,d.file_type,d.file_path,d.version_id,d.uploaded_by,d.updated_at
FROM documents d
INNER JOIN versions v ON d.version_id = v.id
INNER JOIN tools t ON v.tool_id = t.id
WHERE title = :title AND v.tool_version =:tool_version AND t.tool_name=:tool_name
LIMIT 1;

-- name: get-document-by-id^
SELECT id, title, file_type, file_path, version_id, uploaded_by, updated_at
FROM documents
WHERE  id = :document_id
LIMIT 1;

-- name: get-documents
SELECT d.id,d.title,d.file_type,d.file_path,d.version_id,d.uploaded_by,d.updated_at,created_at
FROM documents d
INNER JOIN versions v ON d.version_id = v.id
INNER JOIN tools t ON v.tool_id = t.id
WHERE d.version_id = :version_id::int
    AND (:document_id::int IS NULL OR d.id = :document_id::int)
ORDER BY d.updated_at DESC

-- name: get-dft-tag^
SELECT id,name
FROM dft_tags
WHERE name = :tag_name
LIMIT 1;

-- name: create-new-dft-tag<!
INSERT INTO dft_tags
        (name)
VALUES  (:tag_name)
ON CONFLICT DO NOTHING
RETURNING id,name

-- name: create-document-dft-tag<!
INSERT INTO document_tags
        (document_id,tag_id)
SELECT  :documents_id,
        (SELECT id FROM dft_tags WHERE name=:tag_name)
ON CONFLICT DO NOTHING
RETURNING document_id,tag_id
