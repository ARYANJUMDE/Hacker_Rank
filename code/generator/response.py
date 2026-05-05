import re


def extract_body(text):
    lines = text.split("\n")

    frontmatter_done = False
    fence_count = 0
    body_lines = []

    for line in lines:
        stripped = line.strip()

        if not frontmatter_done:
            if stripped == "---":
                fence_count += 1
                if fence_count >= 2:
                    frontmatter_done = True
                continue
            elif fence_count == 0 and stripped:
                frontmatter_done = True
            else:
                continue

        # Skip markdown headings
        if stripped.startswith("#"):
            continue

        # Skip _Last updated / _Last modified lines
        if stripped.startswith("_Last updated") or stripped.startswith("_Last modified"):
            continue

        # Stop at Related Articles section
        if stripped.lower().startswith("## related") or stripped.lower() == "related articles":
            break

        # Skip image lines  ![...](...) 
        if stripped.startswith("!["):
            continue

        # Skip lines that are only a backslash (markdown line continuation)
        if stripped == "\\":
            continue

        body_lines.append(line)

    body = "\n".join(body_lines).strip()

    # Remove inline images from body text
    body = re.sub(r'!\[.*?\]\(.*?\)', '', body)

    # Remove excessive blank lines
    body = re.sub(r'\n{3,}', '\n\n', body)

    return body.strip()


def generate_response(query, docs, escalate, request_type="product_issue"):
    if escalate:
        return "Escalate to a human"

    if request_type == "invalid":
        q = query.lower().strip()
        greetings = ["thank", "thanks", "hi", "hello", "bye", "good morning",
                     "good afternoon", "good evening", "great", "awesome", "perfect"]
        if any(q.startswith(w) or q == w for w in greetings) and len(q.split()) < 8:
            return "Happy to help"
        return "I am sorry, this is out of scope from my capabilities"

    if not docs:
        return "No relevant support information found."

    body = extract_body(docs[0].text)
    if not body or len(body) < 20:
        return "No relevant support information found."

    return body
