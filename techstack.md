✅ GOAL

    A full offline RAG-based research assistant for literature review, papers, and reference material — fast, scalable, private.

⚙️ STEPWISE TECH STACK
🧱 STEP 1: LLM Backend — Ollama
| Component       | Choice                        | Notes                                           |
| --------------- | ----------------------------- | ----------------------------------------------- |
| **LLM runtime** | [Ollama](https://ollama.com/) | Local models with 1-command interface           |
| **Model #1**    | `llama3:8b`                   | General research Q\&A (best all-rounder)        |
| **Model #2**    | `mistral` or `codellama:7b`   | Optionally for faster loads or code-heavy tasks |


💡 Use --gpu option in Ollama if it's not using your GPU by default.
🧠 STEP 2: Embedding Model — Ollama or HuggingFace
| Component           | Choice                                                                   | Notes                              |
| ------------------- | ------------------------------------------------------------------------ | ---------------------------------- |
| **Embedding Model** | `nomic-embed-text` (via Ollama)                                          | Fast and good; local               |
| Alternative         | `bge-small-en`, `all-MiniLM` (via HuggingFace + `sentence-transformers`) | Lightweight fallback               |
| Max chunk size      | \~512–1024 tokens per chunk                                              | Avoid degradation or slow indexing |


💡 Keep embedding model light so you don't waste GPU/CPU cycles.
📚 STEP 3: Document Loader / Chunker — LangChain or LlamaIndex
| Task            | Tool                                         | Notes                            |
| --------------- | -------------------------------------------- | -------------------------------- |
| **PDF Reading** | `PyMuPDF`, `pdfplumber`                      | Handles research papers robustly |
| **Chunking**    | `RecursiveCharacterTextSplitter` (LangChain) | Adjustable chunk sizes           |
| Alternative     | `LlamaIndex` node parser                     | More academic chunking support   |


📌 Start with LangChain unless you need LlamaIndex's source tracking.
🧊 STEP 4: Vector DB — FAISS
| Component     | Choice             | Notes                               |
| ------------- | ------------------ | ----------------------------------- |
| **Vector DB** | FAISS              | Lightweight, fast, offline          |
| Alternative   | ChromaDB           | Easier metadata queries, but slower |
| Persistence   | Save index to disk | No need to rebuild every time       |


💡 Stick with FAISS until you need fancy querying or metadata search.
🧾 STEP 5: Retrieval + RAG Chain — LangChain
| Component     | Tool                            | Notes                                    |
| ------------- | ------------------------------- | ---------------------------------------- |
| **Retriever** | `vectordb.as_retriever()`       | Retrieves top-k relevant chunks          |
| **LLM Chain** | `RetrievalQA.from_chain_type()` | Combines retriever + LLM                 |
| Chunk config  | 500 tokens w/ 50 overlap        | Good for dense info like research papers |


📌 Keep chunk metadata if you want source citation later.
🧪 STEP 6: Interface — CLI First, UI Later
| Interface         | Tool                 | Notes                          |
| ----------------- | -------------------- | ------------------------------ |
| **CLI**           | Native Python        | Faster to build/test/debug     |
| **UI (Optional)** | Streamlit or Textual | GUI version once CLI is stable |


🧼 Don’t rush into UI until logic is stable.
🛠️ STEP 7: Optional Extras (Future Enhancements)
| Feature              | Tool                    | Notes                                 |
| -------------------- | ----------------------- | ------------------------------------- |
| PDF highlighting     | LlamaIndex + Streamlit  | Show exact chunk sources              |
| Feedback loop        | Save Q\&A sessions      | For tuning or retrying queries        |
| Citation generation  | Embed doc metadata      | Show which doc/chunk supported answer |
| Whisper integration  | Ollama or local whisper | Transcribe lecture audio if needed    |
| Markdown/HTML ingest | Python + BeautifulSoup  | Expand sources beyond PDFs            |

🧑‍💻 Final Dev Environment Summary
| Stack Layer   | Tool                           |
| ------------- | ------------------------------ |
| LLM           | `llama3:8b` via Ollama         |
| Embedding     | `nomic-embed-text` via Ollama  |
| Vector DB     | FAISS                          |
| Loader        | `PyMuPDF` + LangChain Loaders  |
| Chunking      | LangChain RecursiveChunker     |
| Framework     | LangChain                      |
| Interface     | CLI (initial), Streamlit later |
| Code language | Python 3.10+                   |
