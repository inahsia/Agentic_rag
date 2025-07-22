# fetch_notion.py

import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv("NOTION_API_KEY"))

def fetch_notion_pages(database_id):
    response = notion.databases.query(database_id=database_id)
    pages = []
    for page in response["results"]:
        page_id = page["id"]
        content = notion.blocks.children.list(page_id)
        text = ""
        for block in content["results"]:
            if block["type"] == "paragraph":
                text += block["paragraph"].get("text", [{}])[0].get("plain_text", "") + "\n"
        pages.append({"source": f"Notion:{page_id}", "text": text})
    return pages

if __name__ == "__main__":
    notion_db_id = os.getenv("NOTION_DB_ID")
    data = fetch_notion_pages(notion_db_id)
    import json
    with open("notion_docs.json", "w") as f:
        json.dump(data, f, indent=2)
