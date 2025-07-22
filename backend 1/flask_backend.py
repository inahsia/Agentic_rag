from flask import Flask, request, jsonify
from flask_cors import CORS
from qa_agent import generate_answer
import json
import os
from pymongo import MongoClient
from fetch_gdocs import extract_gdoc_id, get_doc_content

app = Flask(__name__)
CORS(app)

MONGO_URI = "mongodb+srv://singhaishani2003:ybvPlQqgwC46EeBf@cluster0.kdxu8dg.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["myappdb"]

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

@app.route("/docs", methods=["GET"])
def list_docs():
    sources = get_all_doc_sources()
    return jsonify({"docs": sources})

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question")
    role = data.get("role", "General")
    doc_source = data.get("doc_source")
    if not question or not doc_source:
        return jsonify({"error": "Missing question or doc_source"}), 400
    answer = generate_answer(question, role, doc_source=doc_source)
    return jsonify({"answer": answer})

@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "Backend is working!"})

@app.route("/mongo-test", methods=["GET"])
def mongo_test():
    try:
        # Try listing collections as a test
        collections = db.list_collection_names()
        return jsonify({"success": True, "collections": collections})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/create-db", methods=["GET"])
def create_db():
    try:
        db.users.insert_one({"username": "testuser", "email": "test@example.com"})
        return jsonify({"success": True, "message": "Database and collection created, sample user inserted."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/add_gdoc_link", methods=["POST"])
def add_gdoc_link():
    data = request.get_json()
    link = data.get("link")
    if not link:
        return {"success": False, "error": "No link provided"}, 400

    # Add link to gdocs_links.json
    links_file = "gdocs_links.json"
    try:
        if os.path.exists(links_file):
            with open(links_file, "r") as f:
                links = json.load(f)
        else:
            links = []
        if link not in links:
            links.append(link)
            with open(links_file, "w") as f:
                json.dump(links, f, indent=2)
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

    # Fetch and store the doc content in MongoDB
    doc_id = extract_gdoc_id(link)
    doc = get_doc_content(doc_id)
    from pymongo import MongoClient
    MONGO_URI = "mongodb+srv://singhaishani2003:ybvPlQqgwC46EeBf@cluster0.kdxu8dg.mongodb.net/"
    client = MongoClient(MONGO_URI)
    db = client["myappdb"]
    gdocs_collection = db["gdocs"]
    gdocs_collection.insert_one(doc)

    return {"success": True, "message": "Link added and doc fetched!"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) 