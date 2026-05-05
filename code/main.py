import os
import csv
import glob

from classifier.intent import classify_intent, get_request_type
from classifier.product import classify_product
from safety.escalation import should_escalate
from retrieval.retriever import Retriever
from generator.response import generate_response
from utils.csv_handler import write_output
from utils.logger import init_log, log_step


def load_corpus(base_path):
    docs = []

    for root, _, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read().strip()

                    if len(text) > 50:
                        docs.append((text, file_path))

            except:
                continue

    return docs


def get_product_area(doc_path, base_path):
    try:
        rel = os.path.relpath(doc_path, base_path)
        parts = rel.replace("\\", "/").split("/")

        area_map = {
            "screen": "screen",
            "hackerrank_community": "community",
            "general-help": "general_help",
            "engage": "engage",
            "chakra": "chakra",
            "settings": "settings",
            "integrations": "integrations",
            "skillup": "skillup",
            "interviews": "interviews",
            "library": "library",
            "uncategorized": "uncategorized",
            "amazon-bedrock": "amazon_bedrock",
            "claude-api-and-console": "api",
            "claude-code": "claude_code",
            "claude-desktop": "claude_desktop",
            "claude-for-education": "education",
            "claude-for-government": "government",
            "claude-for-nonprofits": "nonprofits",
            "claude-in-chrome": "claude_chrome",
            "claude-mobile-apps": "mobile",
            "connectors": "connectors",
            "identity-management-sso-jit-scim": "identity_management",
            "privacy-and-legal": "privacy",
            "pro-and-max-plans": "pro_plans",
            "safeguards": "safeguards",
            "team-and-enterprise-plans": "team_plans",
            "travel-support": "travel_support",
            "small-business": "small_business",
            "consumer": "consumer_support",
            "support": "general_support",
            "conversation-management": "conversation_management",
            "account-management": "account_management",
            "features-and-capabilities": "features",
            "get-started-with-claude": "get_started",
            "personalization-and-settings": "personalization",
            "troubleshooting": "troubleshooting",
            "usage-and-limits": "usage_limits",
            "pricing-and-billing": "billing",
            "api-faq": "api",
        }

        # Walk parts from deepest to shallowest for best match
        for part in reversed(parts[:-1]):
            if part in area_map:
                return area_map[part]

        # Fallback: use the second path segment (category under product)
        if len(parts) >= 2:
            return parts[1].replace("-", "_").replace(" ", "_")

    except Exception:
        pass

    return ""


def main():

    corpus_path = "../data/"
    tickets_path = "../support_tickets/**/*.csv"

    # Clear log file at the start of each run
    init_log("../output/log.txt")

    corpus_docs = load_corpus(corpus_path)
    print(f"Loaded {len(corpus_docs)} documents")

    retriever = Retriever(corpus_docs)

    rows = []

    ticket_files = glob.glob(tickets_path, recursive=True)
    print(f"Found {len(ticket_files)} ticket files")

    for file in ticket_files:
        with open(file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:

                query = (
                    (row.get("Subject") or "") + " " +
                    (row.get("Issue") or "")
                ).strip()

                if not query:
                    continue

                intent = classify_intent(query)

                # Resolve company from CSV or auto-classify from query text
                company = row.get("Company", "").strip()
                if not company or company.lower() in ["none", "", "unknown"]:
                    company = classify_product(query)
                elif company.lower() == "unknown":
                    company = "None"
                company = company.strip()

                request_type = get_request_type(intent, query, company)

                docs = retriever.search(query)

                escalate = should_escalate(intent, docs, request_type, company)
                status = "escalated" if escalate else "replied"

                response = generate_response(query, docs, escalate, request_type)

                product_area = ""
                if docs:
                    product_area = get_product_area(docs[0].path, os.path.abspath(corpus_path))

                justification = f"intent={intent}; request_type={request_type}; escalate={escalate}"

                rows.append([
                    row.get("Issue", ""),
                    row.get("Subject", ""),
                    company,
                    response,
                    product_area,
                    status,
                    request_type,
                    justification
                ])

                log_step(
                    "../output/log.txt",
                    f"issue={row.get('Issue','')[:60]} | intent={intent} | company={company} | status={status} | request_type={request_type}"
                )

    write_output("../output/output.csv", rows)
    print(f"Wrote {len(rows)} rows to output.csv")


if __name__ == "__main__":
    main()
