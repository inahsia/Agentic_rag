# test_apis.py

import os
from dotenv import load_dotenv

# Gemini (Google Generative AI)
import google.generativeai as genai

# Notion
from notion_client import Client as NotionClient

# Google Docs
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

def test_gemini():
    try:
        genai.configure(api_key=os.getenv("AIzaSyAU_InRR7UaOhPV48xjqMVnC9TB-4KeqPM"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Say hello from Gemini!")
        print("✅ Gemini Response:", response.text.strip())
    except Exception as e:
        print("❌ Gemini API Error:", e)

def test_notion():
    try:
        notion = NotionClient(auth=os.getenv("NOTION_API_KEY"))
        print('hello')
        db_id = os.getenv("NOTION_DB_ID")
        print('hello')
        res = notion.databases.query(database_id=db_id)
        print("✅ Notion DB Query Returned", len(res["results"]), "results")
    except Exception as e:
        print("❌ Notion API Error:", e)

def test_google_docs():
    try:
        creds = service_account.Credentials.from_service_account_file(
            "gdocs_credentials.json",
            scopes=["https://www.googleapis.com/auth/documents.readonly"]
        )
        service = build("docs", "v1", credentials=creds)

        doc_ids = os.getenv("GOOGLE_DOC_IDS", "").split(",")
        for doc_id in doc_ids:
            doc_id = doc_id.strip()
            if not doc_id:
                continue
            doc = service.documents().get(documentId=doc_id).execute()
            title = doc.get("title", "Untitled")
            print(f"✅ Google Doc '{title}' ({doc_id}) is accessible")
    except Exception as e:
        print("❌ Google Docs API Error:", e)
        
if __name__ == "__main__":
    print("🔍 Testing APIs...\n")
    test_gemini()
    test_notion()
    test_google_docs()
# import os
# from dotenv import load_dotenv

# # Load variables from .env
# load_dotenv()

# # Access variables
# gemini_key = os.getenv("GEMINI_API_KEY")
# notion_key = os.getenv("NOTION_API_KEY")
# notion_db_id = os.getenv("NOTION_DB_ID")
# gdoc_ids = os.getenv("GOOGLE_DOC_IDS")

# # Print for verification (mask sensitive parts)
# print("Gemini Key:", gemini_key[:10] + "..." if gemini_key else "Missing")
# print("Notion Key:", notion_key[:10] + "..." if notion_key else "Missing")
# print("Notion DB ID:", notion_db_id or "Missing")
# print("Google Doc IDs:", gdoc_ids or "Missing")

