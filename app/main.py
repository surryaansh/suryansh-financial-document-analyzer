from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid

from celery.result import AsyncResult
from app.worker_tasks import run_financial_analysis
from app.celery_app import celery_app

app = FastAPI(title="Financial Document Analyzer")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Financial Document Analyzer API is running"}


@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """
    Accepts a financial PDF and user query.
    Pushes the analysis task to Celery and returns a task_id.
    """
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        os.makedirs("data", exist_ok=True)

        # Save uploaded file locally
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        if not query or not query.strip():
            query = "Analyze this financial document for investment insights"

        # Push task to Celery worker
        task = run_financial_analysis.delay(
            query.strip(),
            file_path,
            file.filename
        )

        return {
            "status": "queued",
            "task_id": task.id
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue analysis task: {str(e)}"
        )


@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Check status of background financial analysis task.
    """
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.state == "PENDING":
        return {"status": "queued"}

    elif task_result.state == "STARTED":
        return {"status": "processing"}

    elif task_result.state == "SUCCESS":
        return task_result.result

    elif task_result.state == "FAILURE":
        return {
            "status": "failed",
            "error": str(task_result.result)
        }

    return {"status": task_result.state}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)