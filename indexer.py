# indexer.py

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def load_all_docs():
    docs = []
    for fname in ["notion_docs.json", "gdocs_docs.json"]:
        try:
            with open(fname, "r") as f:
                docs.extend(json.load(f))
        except:
            pass
    return docs

def split_text(text, chunk_size=300):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def build_index():
    docs = load_all_docs()
    if not docs:
        print("No documents found in notion_docs.json or gdocs_docs.json. Exiting.")
        return
    model = SentenceTransformer("all-MiniLM-L6-v2")

    vectors = []
    chunks = []

    for doc in docs:
        for chunk in split_text(doc["text"]):
            emb = model.encode(chunk)
            vectors.append(emb)
            chunks.append({"text": chunk, "source": doc["source"]})

    if not vectors:
        print("No text chunks found to index. Exiting.")
        return

    vectors_np = np.array(vectors).astype("float32")
    index = faiss.IndexFlatL2(vectors_np.shape[1])
    index.add(vectors_np)

    faiss.write_index(index, "docs.index")
    with open("doc_chunks.npy", "wb") as f:
        np.save(f, np.array(chunks, dtype=object))

if __name__ == "__main__":
    build_index()
