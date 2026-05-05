def classify_intent(query: str) -> str:
    q = query.lower()

    if any(w in q for w in ["fraud", "unauthorized", "hacked", "stolen", "identity theft",
                              "identity has been stolen"]):
        return "fraud"

    if any(w in q for w in ["payment", "charged", "refund", "invoice", "billing",
                              "cheque", "money", "dispute", "charge", "cash"]):
        return "billing"

    if any(w in q for w in ["login", "password", "delete my account", "sign in"]):
        return "account_access"

    if any(w in q for w in ["site is down", "pages are accessible", "not accessible",
                              "system down", "down completely", "is down", "been blocked",
                              "card blocked", "bloquée", "bloqueada", "blocked"]):
        return "bug"

    if any(w in q for w in ["error", "not working", "stopped working", "not responding",
                              "broken", "crash", "failed", "failing", "can't access",
                              "cannot access", "unable to", "can not", "cannot", "blocker"]):
        return "bug"

    if any(w in q for w in ["test", "assessment", "submission", "candidate", "invite",
                              "reinvite", "recruiter", "score", "variant", "resume builder",
                              "certificate", "mock interview"]):
        return "assessment"

    if any(w in q for w in ["would like to", "can you add", "suggestion", "improvement",
                              "please add", "feature request", "request a feature"]):
        return "feature_request"

    return "general"


def get_request_type(intent: str, query: str, company: str = "") -> str:
    q = query.lower().strip()

    known_products = ["hackerrank", "claude", "visa"]
    product_words = [
        "visa", "card", "transaction", "payment", "cheque", "atm", "merchant",
        "dispute", "charge", "cash", "travel",
        "hackerrank", "assessment", "test", "submission", "candidate", "recruiter",
        "invite", "reinvite", "certificate", "mock interview", "resume", "screen",
        "claude", "api", "anthropic", "conversation", "chat", "workspace", "team plan",
        "account", "login", "password", "billing", "refund", "invoice", "fraud",
        "unauthorized", "hacked", "stolen", "error", "bug", "not working",
        "stopped working", "not responding", "is down", "site is down",
        "access", "delete", "report", "review", "mock", "interview",
        "extra time", "score", "variant", "role", "community", "private",
        "security", "vulnerability", "data", "crawl", "identity", "blocker",
        "compatible", "subscription", "employee", "user", "workspace", "project"
    ]

    # If a known company/product is set, it's always a product question
    if company.lower() in known_products:
        if intent == "bug":
            return "bug"
        if intent == "feature_request":
            return "feature_request"
        return "product_issue"

    if not any(k in q for k in product_words):
        return "invalid"

    if intent == "bug":
        return "bug"
    if intent == "feature_request":
        return "feature_request"

    return "product_issue"
