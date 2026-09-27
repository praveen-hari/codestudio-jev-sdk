# syncfusion-codestudio-jev

Dependency-free Python SDK for the SyncfusionCodeStudio JEV Decisions API.

## Install locally

```bash
python3 -m pip install ./sdk/python
```

## Usage

```python
from codestudio_jev import JevClient

jev = JevClient.from_env()
result = jev.decide(
    state={"incident": "Payments are unavailable"},
    questions={
        "urgency": {
            "type": "score",
            "instructions": "How urgent is this incident?",
            "criteria": ["Low", "Medium", "Critical"],
        }
    },
)

print(result.answers["urgency"])
```

Environment variables:

- `CODESTUDIO_BASE_URL`
- `CODESTUDIO_API_KEY_ID`
- `CODESTUDIO_API_KEY_SECRET`

Requires Python 3.11 or newer. The client calls only `POST /v1/decisions` and performs HMAC signing automatically.
