"""Small smoke evaluation against the supplied sample kb.json, not a general benchmark."""
import json
import sys
from app import ask

CASES = [
    ("How do I reset my password?", "answer"),
    ("How do I enable 2FA?", "answer"),
    ("How long does withdrawal review take?", "answer"),
    ("How do I close my account?", "answer"),
    ("How do I update my residential address?", "answer"),
    ("Can you guarantee my withdrawal will finish in 2 hours?", "abstain"),
    ("What tax advice do you provide for closed accounts?", "abstain"),
    ("Can support change my email address for me?", "abstain"),
]


def main():
    rows = []
    answered = cited = correct = 0
    for question, expected in CASES:
        result = ask(question)
        correct += result["decision"] == expected
        if result["decision"] == "answer":
            answered += 1
            cited += bool(result["citations"])
        rows.append({"question": question, "expected": expected, "actual": result["decision"]})
    print(json.dumps({"cases": rows, "decision_accuracy": correct / len(CASES),
                      "citation_presence_rate": cited / answered if answered else 0.0,
                      "answered_count": answered, "total": len(CASES)}, indent=2))
    return 0 if correct == len(CASES) and answered == cited else 1


if __name__ == "__main__":
    sys.exit(main())
