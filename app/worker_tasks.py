import os
import json
from app.celery_app import celery_app
from crewai import Crew, Process
from app.agents import financial_analyst, verifier, risk_assessor, report_compiler
from app.task import (
    analyze_financial_document,
    verification,
    risk_assessment,
    final_report
)
from app.database import save_report


@celery_app.task(bind=True)
def run_financial_analysis(self, query: str, file_path: str, file_name: str):
    """
    Background task that executes the full financial analysis pipeline:
    1. Document verification
    2. Financial analysis (RAG)
    3. Risk assessment
    4. Final report compilation

    Persists the structured report in MongoDB and returns it.
    """

    try:
        crew = Crew(
            agents=[
                verifier,
                financial_analyst,
                risk_assessor,
                report_compiler
            ],
            tasks=[
                verification,
                analyze_financial_document,
                risk_assessment,
                final_report
            ],
            process=Process.sequential,
        )

        result = crew.kickoff(
            inputs={
                "query": query,
                "path": file_path
            }
        )

        # Ensure expected output structure
        if not hasattr(result, "raw"):
            raise ValueError("Unexpected Crew output format.")

        # Parse final structured JSON report
        try:
            parsed_report = json.loads(result.raw)
        except json.JSONDecodeError:
            raise ValueError("Final report is not valid JSON.")

        # Save report to MongoDB
        report_id = save_report(
            file_name=file_name,
            query=query,
            report=parsed_report
        )

        return {
            "status": "completed",
            "report_id": report_id,
            "report": parsed_report
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }

    finally:
        # Clean up temporary uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass