from crewai import Task
from app.agents import financial_analyst, verifier, risk_assessor, report_compiler
from app.tools import FinancialDocumentTool

financial_document_tool = FinancialDocumentTool()


# =========================
# Document Verification Task
# =========================
verification = Task(
    description=(
        "You are given a document located at {path}.\n\n"
        "Determine whether this document contains structured financial reporting "
        "data such as income statements, balance sheets, cash flow statements, "
        "or earnings commentary.\n\n"
        "Return your answer strictly as JSON in the following format:\n"
        "{\n"
        "  \"is_financial_document\": true/false,\n"
        "  \"detected_sections\": [\"section1\", \"section2\"],\n"
        "  \"reason\": \"short explanation\"\n"
        "}\n\n"
        "Do not use tools.\n"
        "Do not fabricate information.\n"
        "Base your answer strictly on document content."
    ),
    expected_output="Strictly valid JSON.",
    agent=verifier,
    tools=[],
    async_execution=False,
)


# =========================
# Financial Analysis Task (RAG + Strict Trend Discipline)
# =========================
analyze_financial_document = Task(
    description=(
        "You are given a financial PDF located at {path}.\n\n"
        "User query:\n"
        "{query}\n\n"
        "You MUST call the tool `financial_document_reader` exactly once with:\n"
        "- path: {path}\n"
        "- query: {query}\n\n"
        "The tool will return relevant document sections. "
        "You must analyze ONLY the returned content.\n\n"

        "STRICT ANALYTICAL RULES:\n"
        "- Do NOT call the tool more than once.\n"
        "- Do NOT fabricate financial values.\n"
        "- Do NOT use external knowledge.\n"
        "- Base ALL conclusions strictly on retrieved document content.\n"
        "- If a metric includes a YoY or sequential percentage change, you MUST explicitly "
        "state whether it increased or decreased.\n"
        "- If revenue decreased, you MUST clearly state that revenue declined or decreased.\n"
        "- Do NOT describe declining metrics as strong, robust, or growing.\n"
        "- Do NOT assume trends unless explicitly supported by numbers.\n"
        "- If a value is not present in the retrieved content, return \"Not stated in document\".\n"
        "- If the user query is unrelated to financial data in the document, "
        "state that the document does not contain relevant information.\n\n"

        "Return strictly valid JSON in the following format:\n"
        "{\n"
        "  \"executive_summary\": \"string\",\n"
        "  \"key_financial_metrics\": {\n"
        "    \"revenue\": \"string or number\",\n"
        "    \"net_income\": \"string or number\",\n"
        "    \"other_metrics\": {}\n"
        "  },\n"
        "  \"observed_trends\": \"string\",\n"
        "  \"direct_answer\": \"string\",\n"
        "  \"conclusion\": \"string\"\n"
        "}\n\n"
        "No markdown.\n"
        "No explanations.\n"
        "No text outside JSON."
    ),
    expected_output="Strictly valid JSON.",
    agent=financial_analyst,
    tools=[financial_document_tool],
    async_execution=False,
)


# =========================
# Risk Assessment Task (Grounded, No Hallucinated Risks)
# =========================
risk_assessment = Task(
    description=(
        "You are given the financial analysis JSON from the previous task.\n\n"
        "Assess financial risks strictly based on that information.\n\n"

        "Rules:\n"
        "- Do NOT call tools.\n"
        "- Do NOT introduce new financial data.\n"
        "- Do NOT assume risks that are not supported by the analysis.\n"
        "- If financial metrics are missing, clearly state that the risk "
        "cannot be determined from the available information.\n"
        "- Do NOT fabricate explanations.\n\n"

        "Return strictly valid JSON in the following format:\n"
        "{\n"
        "  \"liquidity_risk\": \"string\",\n"
        "  \"leverage_risk\": \"string\",\n"
        "  \"operational_risk\": \"string\",\n"
        "  \"market_exposure_risk\": \"string\",\n"
        "  \"overall_risk_summary\": \"string\"\n"
        "}\n\n"
        "JSON only. No markdown."
    ),
    expected_output="Strictly valid JSON.",
    agent=risk_assessor,
    tools=[],
    async_execution=False,
)


# =========================
# Final Report Compilation Task
# =========================
final_report = Task(
    description=(
        "You are given:\n"
        "- Financial analysis JSON\n"
        "- Risk assessment JSON\n\n"
        "Combine them into a single structured investment report.\n\n"

        "Requirements:\n"
        "- Preserve all numerical accuracy.\n"
        "- Do NOT introduce new data.\n"
        "- Do NOT fabricate new insights.\n"
        "- Do NOT contradict earlier analysis.\n"
        "- No markdown.\n"
        "- No explanations.\n"
        "- Must be valid parsable JSON.\n"
        "- Do NOT call tools.\n\n"

        "Return strictly valid JSON in the following format:\n"
        "{\n"
        "  \"executive_summary\": \"string\",\n"
        "  \"financial_overview\": {\n"
        "    \"key_metrics\": {},\n"
        "    \"observed_trends\": \"string\"\n"
        "  },\n"
        "  \"risk_assessment\": {\n"
        "    \"liquidity_risk\": \"string\",\n"
        "    \"leverage_risk\": \"string\",\n"
        "    \"operational_risk\": \"string\",\n"
        "    \"market_exposure_risk\": \"string\",\n"
        "    \"overall_risk_summary\": \"string\"\n"
        "  },\n"
        "  \"investment_conclusion\": \"string\"\n"
        "}\n"
    ),
    expected_output="Strictly valid JSON.",
    agent=report_compiler,
    tools=[],
    async_execution=False,
)