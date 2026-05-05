ALWAYS_ESCALATE_INTENTS = ["fraud", "bug"]
FINANCIAL_ESCALATE_INTENTS = ["billing"]
FINANCIAL_PRODUCTS = ["visa"]


def should_escalate(intent: str, retrieved_docs: list, request_type: str, company: str = "") -> bool:

    # Never escalate invalid/out-of-scope — just reply with out-of-scope message
    if request_type == "invalid":
        return False

    # Always escalate fraud and system bugs
    if intent in ALWAYS_ESCALATE_INTENTS:
        return True

    # Escalate billing issues for financial products (Visa)
    if intent in FINANCIAL_ESCALATE_INTENTS and company.lower() in FINANCIAL_PRODUCTS:
        return True

    # If no relevant docs found → escalate rather than hallucinate
    if not retrieved_docs:
        return True

    return False
