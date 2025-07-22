# qa_agent.py

import faiss
import numpy as np
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Use Gemini Flash 1.5 model
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index and document chunks
index = faiss.read_index("docs.index")
doc_chunks = np.load("doc_chunks.npy", allow_pickle=True).tolist()

# Function to get relevant document chunks, optionally filtered by source
def get_relevant_chunks(query, k=5, doc_source=None):
    if doc_source:
        filtered_chunks = [c for c in doc_chunks if c['source'] == doc_source]
        if not filtered_chunks:
            return []
        # Build a temporary FAISS index for just these chunks
        vectors = [embedder.encode(c['text']) for c in filtered_chunks]
        if not vectors:
            return []
        temp_index = faiss.IndexFlatL2(len(vectors[0]))
        temp_index.add(np.array(vectors).astype('float32'))
        query_vector = embedder.encode([query])
        _, indices = temp_index.search(np.array(query_vector).astype('float32'), min(k, len(filtered_chunks)))
        return [filtered_chunks[i] for i in indices[0]]
    else:
        query_vector = embedder.encode([query])
        _, indices = index.search(np.array(query_vector).astype("float32"), k)
        return [doc_chunks[i] for i in indices[0]]

# Generate an answer using Gemini Flash 1.5
def generate_answer(query, role="General", doc_source=None):
    chunks = get_relevant_chunks(query, doc_source=doc_source)
    if not chunks:
        return "No relevant information found in the selected document."
    context = "\n\n".join(f"{c['text']} (Source: {c['source']})" for c in chunks)

    prompt = f"""You are a helpful assistant answering questions about company documents.\nUser Role: {role}\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"""

    response = model.generate_content(prompt)
    return response.text
