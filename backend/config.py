import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chyroma_db"
PDF_PATH = DATA_DIR / "aws_customer_agreement.pdf"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.0

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 3

SQLITE_URL = f"sqlite:///{BASE_DIR / 'query_logs.db'}"

CHROMA_COLLECTION = "aws_customer_agreement" 

NO_ANSWER_RESPONSE = (
    "The requested information is not present in the AWS Customer Agreement."
)

RAG_PROMPT_TEMPLATE = """You are a helpful assistant that answers questions
based ONLY on the provided context from the AWS Customer Agreement.

Context:
{context}

Question:
{question}

Instructions:
- Answer the question using ONLY the information in the context above.
- If the context does not contain enough information to answer the question,
  respond EXACTLY with: "{no_answer}"
- Do NOT make up or hallucinate any information.
- Cite the relevant parts of the context in your answer.
- Be concise and precise.

Answer:"""