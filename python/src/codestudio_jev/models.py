"""Typed request and response models for the JEV Decisions API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping, Sequence, TypedDict

Guidance = str | Mapping[str, Any] | Sequence[Any]
State = str | Mapping[str, Any] | Sequence[Any]


class NoulCriteria(TypedDict):
    true: Guidance
    false: Guidance


class NoulQuestion(TypedDict, total=False):
    type: Literal["noul"]
    instructions: Guidance
    criteria: NoulCriteria


class ChoiceQuestion(TypedDict):
    type: Literal["choice"]
    instructions: Guidance
    criteria: Mapping[str, Guidance | None]


class ScoreQuestion(TypedDict):
    type: Literal["score"]
    instructions: Guidance
    criteria: Sequence[Guidance]


Question = NoulQuestion | ChoiceQuestion | ScoreQuestion


@dataclass(frozen=True, slots=True)
class DecisionResponse:
    model: str
    answers: Mapping[str, Mapping[str, Any]]
    usage: Mapping[str, int | float]
    id: str | None = None
    provider: str | None = None

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "DecisionResponse":
        model = value.get("model")
        answers = value.get("answers")
        usage = value.get("usage")
        if not isinstance(model, str) or not isinstance(answers, Mapping) or not isinstance(usage, Mapping):
            raise ValueError("JEV returned an invalid response")
        for field in ("input_tokens", "output_tokens", "cost"):
            if not isinstance(usage.get(field), (int, float)):
                raise ValueError("JEV returned invalid usage information")
        return cls(
            id=value.get("id") if isinstance(value.get("id"), str) else None,
            model=model,
            provider=value.get("provider") if isinstance(value.get("provider"), str) else None,
            answers=answers,
            usage=usage,
        )
