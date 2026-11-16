import logging
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.pdf_service import extract_text
from app.services.rag_service import add_document, chunk_text, search

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_SIZE_MB = 10


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    contents = await file.read()

    if len(contents) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413, detail=f"File is too large. Maximum is {MAX_SIZE_MB} MB."
        )

    try:
        text, page_count = extract_text(contents)
    except Exception:
        logger.exception("PDF extraction failed")
        raise HTTPException(status_code=400, detail="Could not read this PDF.")

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text found. Scanned PDFs are not supported yet.",
        )

    chunks = chunk_text(text)
    doc_id = str(uuid.uuid4())
    add_document(doc_id, file.filename, chunks)

    return {
        "document_id": doc_id,
        "filename": file.filename,
        "pages": page_count,
        "characters": len(text),
        "chunk_count": len(chunks),
    }


@router.get("/{doc_id}/search")
def search_document(doc_id: str, question: str, top_k: int = 3):
    results = search(doc_id, question, top_k)

    if results is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found. Upload it again (the server may have restarted).",
        )

    return {"question": question, "results": results}