## Managing Multiple Google Docs

To add multiple Google Docs for ingestion, create a file named `gdocs_ids.json` in the project root with the following format:

```
[
  "your_google_doc_id_1",
  "your_google_doc_id_2",
  "your_google_doc_id_3"
]
```

- Each entry should be a Google Doc ID (the part after `/d/` in the document URL).
- You can add as many IDs as you want.
- When you run `fetch_gdocs.py`, it will fetch and index all docs listed in this file.

**Note:** Make sure each Google Doc is shared with your service account email (see `gdocs_credentials.json`). 