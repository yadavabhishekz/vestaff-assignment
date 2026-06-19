## Setup Instructions

### 1. Clone the Repository

```bash
git clone <>
cd assignement
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:

```
GROQ_API_KEY=gsk_your_actual_key_here
```

### 5. Add the PDF

Place the **AWS Customer Agreement** PDF in the `data/` directory:

```
data/aws_customer_agreement.pdf
```

---

## How to Run

### Start the Backend (FastAPI)

From the **project root**:

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

### Start the Frontend (Streamlit)

In a **separate terminal**, from the **project root**:

```bash
streamlit run frontend/streamlit.py
```


### First-Time Usage

1. Start both the backend and frontend.
2. In the Streamlit sidebar, click **Ingest PDF**.
3. Wait for the success message.
4. Start asking questions in the Chat tab.

---