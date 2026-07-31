"""
rag.py — Document Knowledge Base RAG Ingestion & Vector Retrieval Engine
======================================================================
Handles semantic text chunking, Chroma DB vector storage, document listing,
and knowledge retrieval for BOT-O-BRAIN.
"""

import os
import io
import time
import base64
from typing import List, Dict, Any, Optional

import pypdf
from langchain_core.documents import Document
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from app import make_embeddings

# Persistent Chroma collection for Document Knowledge Base RAG
_RAG_VECTOR_DB = None

def get_rag_vector_db() -> Chroma:
    """Returns persistent Chroma DB instance for RAG knowledge base."""
    global _RAG_VECTOR_DB
    if _RAG_VECTOR_DB is not None:
        return _RAG_VECTOR_DB

    embeddings = make_embeddings()
    _RAG_VECTOR_DB = Chroma(
        collection_name="chroma_knowledge_base",
        embedding_function=embeddings,
        persist_directory="./vector_db_rag",
    )
    return _RAG_VECTOR_DB


def extract_file_text(contents: bytes, filename: str, content_type: str = "") -> str:
    """Extracts raw text from PDF, CSV, TXT, MD, JSON, PY, or DOC files."""
    ext = filename.split(".")[-1].lower() if "." in filename else ""

    if ext == "pdf" or content_type == "application/pdf":
        try:
            reader = pypdf.PdfReader(io.BytesIO(contents))
            pages = [page.extract_text() for page in reader.pages if page.extract_text()]
            return "\n\n".join(pages).strip()
        except Exception as e:
            return f"(PDF text extraction error: {e})"
    else:
        try:
            return contents.decode("utf-8", errors="ignore").strip()
        except Exception:
            return "(Binary file content)"


def ingest_document(contents: bytes, filename: str, content_type: str, user_id: str) -> Dict[str, Any]:
    """
    Parses document, splits text into 800-character chunks with 150 overlap,
    and stores vector embeddings in Chroma DB.
    """
    raw_text = extract_file_text(contents, filename, content_type)
    if not raw_text or len(raw_text.strip()) < 10:
        return {
            "success": False,
            "filename": filename,
            "chunks_added": 0,
            "message": "File is empty or contains no extractable text."
        }

    # Split into 800-character semantic chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    text_chunks = splitter.split_text(raw_text)

    db = get_rag_vector_db()

    # Delete any previous chunks for this file to prevent duplicate indexing
    delete_user_document(filename, user_id)

    documents = []
    ids = []
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    for i, chunk in enumerate(text_chunks):
        doc_id = f"rag_{user_id}_{filename}_{i}_{int(time.time())}"
        doc = Document(
            page_content=chunk,
            metadata={
                "user_id": user_id,
                "filename": filename,
                "chunk_index": i,
                "total_chunks": len(text_chunks),
                "created_at": timestamp
            }
        )
        documents.append(doc)
        ids.append(doc_id)

    if documents:
        db.add_documents(documents=documents, ids=ids)

    return {
        "success": True,
        "filename": filename,
        "chunks_added": len(documents),
        "total_chars": len(raw_text),
        "message": f"Successfully ingested '{filename}' ({len(documents)} vector chunks indexed)."
    }


def retrieve_knowledge_chunks(query: str, user_id: str, top_k: int = 4) -> List[Dict[str, Any]]:
    """
    Performs similarity search over ingested knowledge chunks filtered by user_id.
    """
    if not query or not query.strip():
        return []

    db = get_rag_vector_db()
    try:
        results = db.similarity_search(query, k=top_k, filter={"user_id": user_id})
        chunks = []
        for doc in results:
            chunks.append({
                "content": doc.page_content,
                "filename": doc.metadata.get("filename", "Document"),
                "chunk_index": doc.metadata.get("chunk_index", 0),
            })
        return chunks
    except Exception as e:
        print(f"RAG retrieval error for user {user_id}: {e}")
        return []


def list_user_documents(user_id: str) -> List[Dict[str, Any]]:
    """Returns list of ingested documents for user with chunk count."""
    db = get_rag_vector_db()
    try:
        collection = db._collection.get(where={"user_id": user_id}, include=["metadatas"])
        if not collection or "metadatas" not in collection or not collection["metadatas"]:
            return []

        doc_summary = {}
        for meta in collection["metadatas"]:
            filename = meta.get("filename", "Unknown File")
            if filename not in doc_summary:
                doc_summary[filename] = {
                    "filename": filename,
                    "chunk_count": 0,
                    "created_at": meta.get("created_at", "Recently")
                }
            doc_summary[filename]["chunk_count"] += 1

        return list(doc_summary.values())
    except Exception as e:
        print(f"RAG document summary error for user {user_id}: {e}")
        return []


def delete_user_document(filename: str, user_id: str) -> bool:
    """Deletes all vector chunks matching user_id and filename from Chroma DB."""
    db = get_rag_vector_db()
    try:
        collection = db._collection.get(where={"$and": [{"user_id": user_id}, {"filename": filename}]}, include=["metadatas"])
        if collection and "ids" in collection and collection["ids"]:
            db._collection.delete(ids=collection["ids"])
            return True
        return False
    except Exception as e:
        print(f"RAG delete error for {filename}: {e}")
        return False
