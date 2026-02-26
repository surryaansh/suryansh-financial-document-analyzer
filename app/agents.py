import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from app.tools import FinancialDocumentTool

load_dotenv()

# Initialize language model
llm = LLM(
    model="gpt-4o-mini",
    temperature=0.2
)

# Shared RAG tool (used only by financial analyst)
financial_document_tool = FinancialDocumentTool()


# Financial Analyst Agent (uses RAG)
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal=(
        "Analyze the uploaded financial document and provide structured, "
        "data-backed insights based strictly on the user's query: {query}. "
        "Use retrieved document content only and do not fabricate information."
    ),
    verbose=False,
    memory=False,
    backstory=(
        "You are a CFA-certified financial analyst with over 15 years of experience "
        "in equity research, valuation modeling, and institutional advisory. "
        "All conclusions must be based strictly on retrieved financial data."
    ),
    tools=[financial_document_tool],
    llm=llm,
    max_iter=3,
    allow_delegation=False
)


# Document Verifier Agent (no tools)
verifier = Agent(
    role="Financial Document Validator",
    goal=(
        "Determine whether the uploaded file contains structured financial "
        "reporting data such as income statements, balance sheets, cash flow "
        "statements, or earnings commentary."
    ),
    verbose=False,
    memory=False,
    backstory=(
        "You are a financial reporting and compliance specialist responsible for "
        "identifying whether a document contains valid financial reporting content."
    ),
    tools=[],
    llm=llm,
    max_iter=1,
    allow_delegation=False
)


# Risk Assessment Agent (no tools)
risk_assessor = Agent(
    role="Financial Risk Assessment Specialist",
    goal=(
        "Based on the financial analysis provided, identify financial, operational, "
        "liquidity, leverage, and market risks."
    ),
    verbose=False,
    memory=False,
    backstory=(
        "You are a financial risk analyst experienced in evaluating liquidity, "
        "debt exposure, operational stability, and market sensitivity."
    ),
    tools=[],
    llm=llm,
    max_iter=1,
    allow_delegation=False
)


# Report Compiler Agent (no tools)
report_compiler = Agent(
    role="Financial Report Compiler",
    goal=(
        "Combine the financial analysis and risk assessment into a final, "
        "clear, and structured investment report."
    ),
    verbose=False,
    memory=False,
    backstory=(
        "You are responsible for consolidating analytical outputs into a cohesive, "
        "executive-ready financial report."
    ),
    tools=[],
    llm=llm,
    max_iter=1,
    allow_delegation=False
)