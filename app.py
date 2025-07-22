# app.py


import streamlit as st
import os
import json
import time
from qa_agent import generate_answer
from googleapiclient.discovery import build
from google.oauth2 import service_account


st.set_page_config(page_title="Internal Docs Q&A Agent")
st.title("📄 Internal Docs Q&A Agent")

# --- Dynamic Document Upload Section ---
st.subheader("Add a new document to the knowledge base")
doc_type = st.selectbox("Document Type", ["Google Doc", "Notion Doc"])
doc_id_or_url = st.text_input("Enter the document ID or URL:")
add_doc_btn = st.button("Add Document")

def extract_gdoc_id(url_or_id):
    if "/d/" in url_or_id:
        # Extract ID from URL
        return url_or_id.split("/d/")[1].split("/")[0]
    return url_or_id.strip()

def fetch_and_append_gdoc(doc_id):
    from fetch_gdocs import get_doc_content
    doc = get_doc_content(doc_id)
    # Append to gdocs_docs.json
    gdocs_path = "gdocs_docs.json"
    docs = []
    if os.path.exists(gdocs_path):
        with open(gdocs_path, "r") as f:
            try:
                docs = json.load(f)
            except:
                docs = []
    docs.append(doc)
    with open(gdocs_path, "w") as f:
        json.dump(docs, f, indent=2)

def fetch_and_append_notion(doc_id):
    from fetch_notion import get_notion_content
    doc = get_notion_content(doc_id)
    # Append to notion_docs.json
    notion_path = "notion_docs.json"
    docs = []
    if os.path.exists(notion_path):
        with open(notion_path, "r") as f:
            try:
                docs = json.load(f)
            except:
                docs = []
    docs.append(doc)
    with open(notion_path, "w") as f:
        json.dump(docs, f, indent=2)

def rebuild_index():
    import subprocess
    subprocess.run(["python", "indexer.py"])

if add_doc_btn and doc_id_or_url:
    with st.spinner("Fetching and indexing document..."):
        if doc_type == "Google Doc":
            doc_id = extract_gdoc_id(doc_id_or_url)
            fetch_and_append_gdoc(doc_id)
        else:
            fetch_and_append_notion(doc_id_or_url.strip())
        rebuild_index()
        st.success("Document added and indexed! You can now ask questions about it.")
        time.sleep(1)


if "history" not in st.session_state:
    st.session_state.history = []


# --- Document Selection for Q&A ---

def get_all_doc_sources():
    sources = []
    for fname in ["gdocs_docs.json", "notion_docs.json"]:
        if os.path.exists(fname):
            with open(fname, "r") as f:
                try:
                    docs = json.load(f)
                    for doc in docs:
                        if doc.get("text") and doc.get("text").strip():
                            sources.append(doc["source"])
                except:
                    pass
    return sources

doc_sources = get_all_doc_sources()
selected_doc_source = None
if doc_sources:
    selected_doc_source = st.selectbox("Select a document to answer from:", doc_sources)


role = st.selectbox("Select your role:", ["Engineer", "PM", "HR", "General"])
query = st.text_input("Ask your question about internal docs:")


if st.button("Get Answer") and query:
    answer = generate_answer(query, role, doc_source=selected_doc_source)
    st.session_state.history.append({"q": query, "a": answer})
    if len(st.session_state.history) > 3:
        st.session_state.history.pop(0)


for entry in reversed(st.session_state.history):
    st.markdown(f"**You:** {entry['q']}")
    st.markdown(f"**Answer:** {entry['a']}")

def share_doc_with_service_account(doc_id, service_account_email):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'gdocs_credentials.json'
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)
    permission = {
        'type': 'user',
        'role': 'reader',
        'emailAddress': service_account_email
    }
    drive_service.permissions().create(
        fileId=doc_id,
        body=permission,
        sendNotificationEmail=False
    ).execute()
