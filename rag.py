"""
rag.py - Step 3 of RAG: give the matching chunks to the LLM and get an answer.

RAG = Retrieval-Augmented Generation
    Retrieval  -> retriever.py finds the right chunks
    Augmented  -> we add those chunks to the prompt
    Generation -> the LLM writes the answer using only those chunks
"""

import re

import llm
from retriever import TfidfRetriever

MIN_SCORE = 0.05  # below this, the PDF probably doesn't talk about the question
OVERVIEW_CHUNKS = 10  # how many chunks to send for "summarize / key points" questions

# Questions about the WHOLE document don't share words with any one chunk,
# so word-matching search can't find them. We detect them separately.
OVERVIEW_PATTERN = re.compile(
    r"summar|key points?|main points?|overview|highlights|important points|"
    r"what is (this|the) (pdf|document|file|project|notes?|book) about|"
    r"explain (this|the) (pdf|document|file|project|notes?|book)|"
    r"tell me about (this|the) (pdf|document|file|project|notes?|book)",
    re.IGNORECASE,
)


def is_overview_question(question: str) -> bool:
    return bool(OVERVIEW_PATTERN.search(question))


def overview_chunks(retriever: TfidfRetriever, n: int = OVERVIEW_CHUNKS):
    """Pick chunks spread evenly across the whole document (start, middle, end)."""
    chunks = retriever.chunks
    if len(chunks) <= n:
        picked = chunks
    else:
        step = len(chunks) / n
        picked = [chunks[int(i * step)] for i in range(n)]
    return [(c, 0.0) for c in picked]

SYSTEM_PROMPT = (
    "You answer questions using ONLY the context passages given to you. "
    "If the answer is not in the context, say: "
    "\"I couldn't find that in the uploaded documents.\" "
    "Do not use outside knowledge. Keep answers clear and simple. "
    "After each fact, cite the passage number like [1] or [2]."
)

# Hybrid mode: PDF first, then the AI's own knowledge - always clearly labelled.
SYSTEM_PROMPT_HYBRID = (
    "You are a friendly study assistant. Context passages from the user's PDF are given.\n"
    "1. If the answer IS in the context, answer from it and cite passages like [1] or [2].\n"
    "2. If the answer is NOT in the context (for example the meaning of a word, a "
    "definition, or a topic the PDF doesn't explain), answer from your general "
    "knowledge. Start that part with the line: **📚 Not in your PDF - general explanation:**\n"
    "3. If both apply, first give the PDF part with citations, then the general part "
    "with that label.\n"
    "For word meanings, give: a simple meaning, a short example sentence, and how it "
    "relates to the PDF topic if it does.\n"
    "Use simple English. Never pretend general knowledge came from the PDF.\n"
    "On the very last line write exactly one tag: [[SOURCE: pdf]] or "
    "[[SOURCE: general]] or [[SOURCE: both]]"
)

SOURCE_TAG = re.compile(r"\[\[\s*SOURCE:\s*(pdf|general|both)\s*\]\]", re.IGNORECASE)


def split_source_tag(answer: str) -> tuple[str, str]:
    """Remove the [[SOURCE: ...]] tag from the answer and return (clean_answer, source)."""
    match = SOURCE_TAG.search(answer)
    source = match.group(1).lower() if match else "pdf"
    return SOURCE_TAG.sub("", answer).strip(), source


def build_prompt(question: str, results, history: list[dict]) -> str:
    context = "\n\n".join(
        f"[{i}] (from {chunk.source}, page {chunk.page})\n{chunk.text}"
        for i, (chunk, _score) in enumerate(results, start=1)
    )
    past = ""
    if history:
        last_turns = history[-4:]  # short memory so follow-up questions work
        past = "\n".join(f"{m['role']}: {m['content']}" for m in last_turns)
        past = f"Recent conversation:\n{past}\n\n"
    return f"{past}Context passages:\n{context}\n\nQuestion: {question}\nAnswer:"


def answer_question(
    retriever: TfidfRetriever,
    question: str,
    history: list[dict] | None = None,
    allow_general: bool = False,
    language: str = "English",
) -> dict:
    """
    allow_general=False -> "PDF only" mode (strict, never uses outside knowledge)
    allow_general=True  -> "PDF + general knowledge" mode (hybrid RAG)

    Returns a dict:
        answer  - text to show the user
        sources - list of (chunk, score) used (empty if the answer is general only)
        mode    - "ai", "offline" or "none"
        origin  - "pdf", "general" or "both"
    """
    if is_overview_question(question):
        # "summarize / key points / explain the project" -> look at the whole document
        results = overview_chunks(retriever)
    else:
        results = retriever.search(question, top_k=4)
        weak_match = not results or results[0][1] < MIN_SCORE
        if weak_match and llm.is_configured():
            # No exact word match (e.g. a follow-up like "explain more").
            # Let the AI read a spread of the document and decide; the system
            # prompt still makes it say "couldn't find" if it's really not there.
            results = overview_chunks(retriever)

    if not results or (results[0][1] < MIN_SCORE and not llm.is_configured()
                       and not is_overview_question(question)):
        return {
            "answer": "I couldn't find that in the uploaded documents. "
            "Try different words or check that the right PDF is uploaded.",
            "sources": [],
            "mode": "none",
            "origin": "pdf",
        }

    if not llm.is_configured():
        best_chunk, _ = results[0]
        return {
            "answer": (
                "**Offline mode** (no API key set) - here is the most relevant "
                f"passage from *{best_chunk.source}*, page {best_chunk.page}:\n\n"
                f"> {best_chunk.text}"
            ),
            "sources": results,
            "mode": "offline",
            "origin": "pdf",
        }

    prompt = build_prompt(question, results, history or [])
    if is_overview_question(question):
        prompt += (
            "\n(The passages above are spread across the whole document. "
            "Give a clear summary with the main points as bullet points.)"
        )

    lang_rule = llm.LANGUAGES.get(language, "") + " Keep the [[SOURCE]] tag and citations in English."
    if not allow_general:
        answer = llm.generate(prompt, system=SYSTEM_PROMPT + " " + lang_rule)
        return {"answer": answer, "sources": results, "mode": "ai", "origin": "pdf"}

    raw = llm.generate(prompt, system=SYSTEM_PROMPT_HYBRID + "\n" + lang_rule, temperature=0.4)
    answer, origin = split_source_tag(raw)
    sources = [] if origin == "general" else results  # don't show PDF pages it didn't use
    return {"answer": answer, "sources": sources, "mode": "ai", "origin": origin}
