def priority_agent(requests: list[dict]) -> list[dict]:
    """Assign a simple priority based on request urgency words."""
    urgent_words = {"urgent", "medical", "elderly", "flood", "injury"}
    output = []

    for request in requests:
        text = f"{request.get('category', '')} {request.get('details', '')}".lower()
        score = 1
        if any(word in text for word in urgent_words):
            score = 3
        elif request.get("category", "").lower() in {"transport", "food"}:
            score = 2

        enriched = dict(request)
        enriched["priority_score"] = score
        output.append(enriched)

    return output
