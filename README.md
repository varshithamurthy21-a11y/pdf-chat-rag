# 📄 Chat with Your PDF (RAG Project)

Upload any PDF — notes, a textbook, a report — and ask questions in plain English.
The app finds the right parts of the document and the AI answers **only from those parts**,
showing the page number it used.

This is a **RAG (Retrieval-Augmented Generation)** project, one of the most in-demand skills in AI jobs today.

---

## ✨ Features
- Upload one or many PDFs at once
- Ask questions in a chat window, with follow-up questions
- Every answer shows **sources** (file name + page number + match score)
- Says *"I couldn't find that"* instead of making things up
- Works with **Google Gemini** (free key) or **Anthropic Claude**
- **Offline mode**: with no API key, it still shows the best matching passage

## 🌟 What makes PDF Studio different
- **🎯 Exam Prep** — upload notes + past question papers → predicted important questions with marks,
  a "covered in your notes?" check, study gaps, 2/5/10-mark exam-style answers, and quizzes with scoring.
- **📸 Notes Scanner** — photos of handwritten notes (upload or camera) → AI reads them into editable
  text → chat with your own handwritten notes.
- **🗣️ Kannada mode** — answers in English, Kannada script, or Kannada + English mix.
- **🔊 Read aloud** — hear answers in an Indian-accent voice (English or Kannada).
- **📄/📚 Source labels** — every answer says whether it came from your PDF or general knowledge.

## 🧰 Extra tools (pages in the sidebar)
- **🧰 PDF Tools** — merge, extract/split pages, rotate, add/remove password (AES-256), PDF → HD images.
- **🖼️ Image to PDF** — many images → one PDF. JPEG photos are embedded with **zero re-compression**
  (100% original quality); PNG/WEBP/BMP/TIFF are stored losslessly. Page size: Original, A4, Letter or A3,
  with margins, auto landscape/portrait and custom page order.
- **🔄 JPEG Converter** — PNG, WEBP, BMP, TIFF, GIF (and iPhone HEIC) → JPEG at quality 100 with full
  4:4:4 colour, original resolution, colour profile kept. Batch convert and download as ZIP.

## 🎨 Themes
Pick a theme from **🎨 Theme** in the sidebar: Aurora, Ocean, Sunset, Forest, Candy or Midnight Gold.
To make your own, copy an entry in `THEMES` inside `theme.py` and change the colours.

## 🧠 How it works

```
PDF ──► extract text ──► split into chunks ──► TF-IDF index
                                                   │
Question ──────────────────────────► find top 4 matching chunks
                                                   │
                      chunks + question ──► LLM ──► answer with [citations]
```

| File | What it does |
|------|--------------|
| `pdf_utils.py` | Reads PDF pages and splits text into ~500-character chunks with overlap |
| `retriever.py` | TF-IDF + cosine similarity search to find the best chunks |
| `rag.py` | Builds the prompt with the chunks and asks the LLM |
| `llm.py` | Small wrapper for Gemini / Claude |
| `app.py` | Starting point: page menu + theme |
| `chat_page.py` | Streamlit chat interface |
| `theme.py` | 6 colour themes (picker in the sidebar) |
| `.streamlit/config.toml` | Base theme settings |

## 🚀 How to run

```bash
# 1. go into the folder
cd pdf-chat-rag

# 2. (recommended) create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac / Linux

# 3. install packages
pip install -r requirements.txt

# 4. add your API key
copy .env.example .env       # Windows   (cp .env.example .env on Mac/Linux)
# open .env and paste your key after GEMINI_API_KEY=

# 5. start the app
streamlit run app.py
```

The browser opens at `http://localhost:8501`. Upload `sample_docs/smart_irrigation_notes.pdf` and try:
- *What is hysteresis and why is it used?*
- *Which sensor is used and why?*
- *What are the limitations?*
- *Who invented the ESP32?* → it should say it couldn't find this (not in the PDF)

## 🔧 Ideas to improve it (your own additions)
1. Replace TF-IDF with **sentence embeddings** (`sentence-transformers`) + **FAISS / ChromaDB**
2. Add **OCR** (`pytesseract`) so scanned PDFs work
3. Save chat history and let users download it
4. Support Word (.docx) and text files
5. Deploy free on **Streamlit Community Cloud**

## 🎤 Interview talking points
- *Why chunking?* LLMs have a context limit; small chunks let us send only relevant text.
- *Why overlap?* So sentences cut at the edge of a chunk aren't lost.
- *How do you stop hallucination?* The system prompt allows only the given context, and low-match questions are rejected before reaching the LLM.
- *TF-IDF vs embeddings?* TF-IDF matches exact words; embeddings match meaning ("car" ≈ "vehicle").

## 🛠 Tech stack
Python · Streamlit · pypdf · scikit-learn · Gemini / Claude API
