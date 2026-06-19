from __future__ import annotations


from pathlib import Path
from typing import Dict, List, Tuple

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from backend.config import (
    CHROMA_COLLECTION,
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    GROQ_API_KEY,
    LLM_MODEL,
    LLM_TEMPERATURE,
    NO_ANSWER_RESPONSE,
    PDF_PATH,
    RAG_PROMPT_TEMPLATE,
    TOP_K,
)

# Module level singletons

_embeddings : HuggingFaceEmbeddings | None = None
_vectorstore : Chroma | None = None
_llm : ChatGroq | None = None


# getter functions

def _get_embeddings() -> HuggingFaceEmbeddings:

    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
    return _embeddings

def _get_llm() -> ChatGroq:
    
    global _llm
    if _llm is None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set. Add it to your .env file.")

        _llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model_name=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
        )
    return _llm

def _get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        chroma_path = Path(CHROMA_DIR)
        if not chroma_path.exists() or not any(chroma_path.iterdir()):
            raise RuntimeError("Vector store not initialised. Call Post /ingest first.")

        _vectorstore = Chroma(
            collection_name= CHROMA_COLLECTION,
            embedding_function=_get_embeddings(),
            persist_directory=str(CHROMA_DIR)
        )
    
    return _vectorstore

def ingest_pdf(pdf_path: Path | None = None) -> Dict[str, str]:

    global _vectorstore

    path = pdf_path or PDF_PATH

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found at {path}. Place the file in the data/ directory."
        )

    existing_store = Chroma(
        collection_name=CHROMA_COLLECTION,
        embedding_function=_get_embeddings(),
        persist_directory=str(CHROMA_DIR),
    )

    if existing_store._collection.count() > 0:
        raise RuntimeError(
            "Document already ingested."
        )

    # load pdf
    loader = PyPDFLoader(str(path))
    pages: List[Document] = loader.load()

    # create chunk
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    chunks: List[Document] = splitter.split_documents(pages)

    # embed chunks
    _vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=_get_embeddings(),
        collection_name=CHROMA_COLLECTION,
        persist_directory=str(CHROMA_DIR),
    )

    return {
        "message": (
            f"Document ingested successfully. "
            f"{len(pages)} pages → {len(chunks)} chunks."
        )
    }

def ask_question(question: str) -> Tuple[str, List[str], bool]:

    vectorstore = _get_vectorstore()

    # retrieve top k relevant chunks
    retriever = vectorstore.as_retriever(
        search_type = "similarity",
        search_kwargs = {"k" : TOP_K}
    )
    docs: List[Document] = retriever.invoke(question)
    source_chunks: List[str] = [doc.page_content for doc in docs]

    # prompt
    context = "\n\n---\n\n".join(source_chunks)
    prompt = PromptTemplate(
        template=RAG_PROMPT_TEMPLATE,
        input_variables=["context", "question", "no_answer"],
    )
    formatted_prompt = prompt.format(
        context=context,
        question=question,
        no_answer=NO_ANSWER_RESPONSE,
    )

    llm = _get_llm()
    response = llm.invoke(formatted_prompt)
    answer: str = response.content.strip()

    answer_found = NO_ANSWER_RESPONSE.lower() not in answer.lower()

    return answer, source_chunks, answer_found