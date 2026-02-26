import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

"""
MongoDB configuration and helper utilities
for persisting financial analysis reports.
"""

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("MONGODB_DB", "financial_analyzer")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in environment variables")

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
reports_collection = db["reports"]


def save_report(file_name: str, query: str, report: dict) -> str:
    """
    Persist a structured financial report to MongoDB.

    Args:
        file_name: Name of the uploaded PDF file.
        query: User query used for analysis.
        report: Final structured financial report JSON.

    Returns:
        Inserted MongoDB document ID as a string.
    """
    document = {
        "file_name": file_name,
        "query": query,
        "report": report,
        "created_at": datetime.utcnow()
    }

    result = reports_collection.insert_one(document)
    return str(result.inserted_id)