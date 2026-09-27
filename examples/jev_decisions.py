#!/usr/bin/env python3
"""Minimal Python SDK example for the JEV Decisions API."""

from codestudio_jev import JevClient


def main() -> None:
    client = JevClient.from_env()
    result = client.decide(
        state={
            "service": "checkout",
            "impact": "Payment processing is unavailable for every customer.",
        },
        questions={
            "is_incident": {
                "type": "noul",
                "instructions": "Does this state describe a production incident?",
            },
            "owner": {
                "type": "choice",
                "instructions": "Which team should own the response?",
                "criteria": {
                    "payments": "Checkout, billing, or payment processing.",
                    "frontend": "Rendering, layout, or browser behavior.",
                },
            },
            "urgency": {
                "type": "score",
                "instructions": "How urgent is this incident?",
                "criteria": ["Low", "Medium", "Critical"],
            },
        },
    )
    print(result)


if __name__ == "__main__":
    main()