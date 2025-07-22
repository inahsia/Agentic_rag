# fetch_gdocs.py

import os
import json
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pymongo import MongoClient

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
SERVICE_ACCOUNT_FILE = 'gdocs_credentials.json'

DOC_IDS_FILE = 'gdocs_ids.json'
DOC_LINKS_FILE = 'gdocs_links.json'

MONGO_URI = "mongodb+srv://singhaishani2003:ybvPlQqgwC46EeBf@cluster0.kdxu8dg.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["myappdb"]
gdocs_collection = db["gdocs"]

def extract_gdoc_id(url_or_id):
    if "/d/" in url_or_id:
        return url_or_id.split("/d/")[1].split("/")[0]
    return url_or_id.strip()

def get_doc_ids():
    if os.path.exists(DOC_LINKS_FILE):
        with open(DOC_LINKS_FILE, 'r') as f:
            try:
                links = json.load(f)
                return [extract_gdoc_id(link) for link in links]
            except Exception:
                return []
    elif os.path.exists(DOC_IDS_FILE):
        with open(DOC_IDS_FILE, 'r') as f:
            try:
                return [extract_gdoc_id(doc_id) for doc_id in json.load(f)]
            except Exception:
                return []
    return []

def get_doc_content(doc_id):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('docs', 'v1', credentials=creds)
    try:
        doc = service.documents().get(documentId=doc_id).execute()
    except Exception as e:
        print(f"[ERROR] Could not fetch doc with ID {doc_id}: {e}")
        return {"source": f"GDoc:{doc_id}", "text": "", "error": str(e)}
    # Check if it's a Google Doc
    if doc.get('mimeType', None) and doc['mimeType'] != 'application/vnd.google-apps.document':
        print(f"[ERROR] Document {doc_id} is not a Google Doc. MIME type: {doc.get('mimeType')}")
        return {"source": f"GDoc:{doc_id}", "text": "", "error": "Not a Google Doc"}
    text = ""
    for el in doc.get("body", {}).get("content", []):
        text_run = el.get("paragraph", {}).get("elements", [{}])[0].get("textRun", {})
        if text_run:
            text += text_run.get("content", "")
    return {"source": f"GDoc:{doc_id}", "text": text.strip()}

if __name__ == "__main__":
    load_dotenv()
    doc_ids = get_doc_ids()
    docs = []
    for doc_id in doc_ids:
        doc_id = doc_id.strip()
        if not doc_id:
            continue
        print(f"Fetching Google Doc: {doc_id}")
        doc = get_doc_content(doc_id)
        if doc.get("error"):
            print(f"[ERROR] Skipping doc {doc_id} due to error: {doc['error']}")
        docs.append(doc)
    # Store docs in MongoDB instead of JSON file
    if docs:
        gdocs_collection.delete_many({})  # Clear old docs
        gdocs_collection.insert_many(docs)
    print(f"Done. {len(docs)} docs processed. See MongoDB collection 'gdocs' for results.")
