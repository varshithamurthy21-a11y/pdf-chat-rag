"""
chat_page.py - Chat with your PDF (RAG project)

Start the whole app with:  streamlit run app.py
"""

import hashlib

import streamlit as st

import llm
from pdf_utils import load_pdf_chunks
from rag import answer_question
from retriever import TfidfRetriever
from theme import badge, feature_cards, hero

# ---------- session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "files_key" not in st.session_state:
    st.session_state.files_key = None
if "stats" not in st.session_state:
    st.session_state.stats = {}


def files_signature(files) -> str:
    """A fingerprint of the uploaded files, so we only rebuild when they change."""
    h = hashlib.md5()
    for f in files:
        h.update(f.name.encode())
        h.update(f.getvalue())
    return h.hexdigest()


# ---------- sidebar ----------
with st.sidebar:
    st.markdown("### 📄 Your documents")

    uploaded = st.file_uploader(
        "Upload PDF files", type=["pdf"], accept_multiple_files=True,
        key=f"pdf_upload_{st.session_state.get('upload_round', 0)}",
    )

    # Parsed PDFs are kept in session_state, so they stay loaded when you
    # visit other pages (the upload box itself resets when you switch pages).
    pdf_chunks = st.session_state.setdefault("pdf_chunks", {})
    for f in uploaded or []:
        sig = files_signature([f])
        if pdf_chunks.get(f.name, (None,))[0] != sig:
            with st.spinner(f"Reading {f.name}..."):
                pdf_chunks[f.name] = (sig, load_pdf_chunks(f, f.name))

    scanned = st.session_state.get("scanned_chunks", {})  # from Notes Scanner
    docs = {name: c for name, (_sig, c) in pdf_chunks.items()}
    docs.update({f"📸 {name}": c for name, c in scanned.items()})

    key = "|".join(f"{n}:{len(c)}:{pdf_chunks.get(n, ('',))[0]}" for n, c in sorted(docs.items()))
    if key != st.session_state.files_key:
        all_chunks = [chunk for c in docs.values() for chunk in c]
        st.session_state.files_key = key
        st.session_state.stats = {n: len(c) for n, c in docs.items()}
        st.session_state.messages = []
        try:
            st.session_state.retriever = TfidfRetriever(all_chunks) if all_chunks else None
        except ValueError as e:
            st.session_state.retriever = None
            st.error(str(e))

    if st.session_state.retriever is not None:
        st.success("Ready! Ask your questions.")
        for name, n in st.session_state.stats.items():
            st.write(f"• **{name}** — {n} chunks")
        if st.button("🗑️ Remove all documents"):
            st.session_state.pdf_chunks = {}
            st.session_state.scanned_chunks = {}
            st.session_state.upload_round = st.session_state.get("upload_round", 0) + 1
            st.rerun()

    st.divider()
    answer_mode = st.radio(
        "Answer mode",
        ["📄 PDF only", "📄 + 📚 PDF + general knowledge"],
        index=1,
        help=(
            "PDF only: answers strictly from your documents.\n\n"
            "PDF + general knowledge: also explains words, meanings and topics "
            "that aren't in the PDF, and labels those answers clearly."
        ),
    )
    allow_general = answer_mode.startswith("📄 +")
    language = st.selectbox("🗣️ Answer language", list(llm.LANGUAGES))
    read_aloud = st.toggle("🔊 Read answers aloud", value=False,
                           help="Needs internet. Uses Google text-to-speech.")

    if llm.is_configured():
        st.info(f"AI model: {llm.provider_label()}")
    else:
        st.warning(
            "No API key found → **offline mode** (shows best matching passage). "
            "Add a key in `.env` for full AI answers."
        )

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ---------- main chat ----------
hero(
    "Chat with your PDF",
    "Upload notes, textbooks or reports and ask anything. Answers come with page numbers.",
    "💬",
)

if st.session_state.retriever is None:
    feature_cards([
        ("📤", "1. Upload", "Add one or more PDFs from the sidebar."),
        ("❓", "2. Ask", "Type a question, or ask for a summary or key points."),
        ("📌", "3. Check sources", "Every answer shows the file and page it came from."),
        ("📚", "Beyond the PDF", "Turn on general knowledge to explain words and topics."),
    ])
    st.info("👈 Start by uploading a PDF in the sidebar. Tip: try the file in `sample_docs/`.")

def speak(text: str, language: str):
    """Turn the answer into speech (MP3 bytes) with gTTS. Returns None if it fails."""
    import io
    import re

    try:
        from gtts import gTTS
    except ImportError:
        st.caption("Install `gtts` for read-aloud: `pip install gtts`")
        return None
    clean = re.sub(r"\[\d+\]|[*#>`_|]", "", text)  # drop markdown and [1] citations
    clean = clean.replace("📚 Not in your PDF - general explanation:", "")[:3000]
    lang = "kn" if language.startswith("ಕನ್ನಡ") else "en"
    try:
        buf = io.BytesIO()
        gTTS(clean, lang=lang, tld="co.in").write_to_fp(buf)  # Indian accent
        return buf.getvalue()
    except Exception as e:
        st.caption(f"Couldn't create audio: {e}")
        return None


ORIGIN_BADGE = {
    "pdf": "📄 Answer from your PDF",
    "general": "📚 General knowledge (not from your PDF)",
    "both": "📄 + 📚 From your PDF and general knowledge",
}


def show_answer(content, sources, origin=None):
    if origin:
        badge(ORIGIN_BADGE.get(origin, ""))
    st.markdown(content)
    if sources:
        with st.expander("Sources used"):
            for i, (src, page, score, text) in enumerate(sources, 1):
                st.markdown(f"**[{i}] {src} — page {page}** (match {score:.2f})")
                st.caption(text[:400] + ("..." if len(text) > 400 else ""))


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            show_answer(msg["content"], msg.get("sources"), msg.get("origin"))
        else:
            st.markdown(msg["content"])

question = st.chat_input(
    "Ask something...", disabled=st.session_state.retriever is None
)

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                history = st.session_state.messages[:-1]
                result = answer_question(
                    st.session_state.retriever, question, history, allow_general, language
                )
                answer = result["answer"]
                result_ok = True
                origin = result.get("origin") if result["mode"] == "ai" else None
                sources = [
                    (c.source, c.page, score, c.text) for c, score in result["sources"]
                ]
            except Exception as e:  # show API errors nicely instead of crashing
                answer = f"⚠️ Something went wrong: {e}"
                result_ok = False
                origin = None
                sources = []

        show_answer(answer, sources, origin)
        if read_aloud and result_ok:
            audio = speak(answer, language)
            if audio:
                st.audio(audio, format="audio/mp3", autoplay=True)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources, "origin": origin}
    )
