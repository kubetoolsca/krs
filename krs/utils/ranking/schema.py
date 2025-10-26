"""JSON schema definitions for ranking artifacts."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from jsonschema import Draft202012Validator, ValidationError


ISO_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"

SNAPSHOT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["metadata", "tools"],
    "properties": {
        "metadata": {
            "type": "object",
            "required": ["generated_at", "source_repos", "version"],
            "properties": {
                "generated_at": {"type": "string", "pattern": ISO_PATTERN},
                "source_repos": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "version": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "tools": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": [
                    "name",
                    "repo",
                    "category",
                    "stars",
                    "forks",
                    "open_issues",
                    "last_commit_at",
                    "issue_velocity_30d",
                    "trend_30d_stars",
                    "cncf_status",
                    "mcp_support",
                    "capabilities",
                    "score_inputs",
                ],
                "properties": {
                    "name": {"type": "string"},
                    "repo": {"type": "string", "pattern": r"^[\w\-]+/[\w\.-]+$"},
                    "category": {"type": "string"},
                    "stars": {"type": "integer", "minimum": 0},
                    "forks": {"type": "integer", "minimum": 0},
                    "open_issues": {"type": "integer", "minimum": 0},
                    "last_commit_at": {"type": "string", "pattern": ISO_PATTERN},
                    "issue_velocity_30d": {"type": "number", "minimum": 0.0},
                    "trend_30d_stars": {"type": "integer", "minimum": 0},
                    "cncf_status": {"type": "string"},
                    "mcp_support": {"type": "boolean"},
                    "capabilities": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "score_inputs": {
                        "type": "object",
                        "required": ["popularity", "recency", "growth"],
                        "properties": {
                            "popularity": {"type": "number"},
                            "recency": {"type": "number"},
                            "growth": {"type": "number"},
                            "issue_velocity": {"type": "number"},
                            "cncf": {"type": "number"},
                        },
                        "additionalProperties": True,
                    },
                },
                "additionalProperties": True,
            },
        },
    },
    "additionalProperties": False,
}

CANONICAL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["metadata", "categories"],
    "properties": {
        "metadata": SNAPSHOT_SCHEMA["properties"]["metadata"],
        "categories": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "tools"],
                "properties": {
                    "name": {"type": "string"},
                    "tools": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "name",
                                "rank",
                                "repo",
                                "score",
                                "score_inputs",
                                "cncf_status",
                            ],
                            "properties": {
                                "name": {"type": "string"},
                                "rank": {"type": "integer", "minimum": 1},
                                "repo": {"type": "string"},
                                "score": {"type": "number"},
                                "score_inputs": {"type": "object"},
                                "cncf_status": {"type": "string"},
                                "reason": {"type": "string"},
                            },
                            "additionalProperties": True,
                        },
                    },
                },
                "additionalProperties": False,
            },
        },
        "legacy": {
            "type": "object",
            "required": ["kubetools_data", "category_rank"],
            "properties": {
                "kubetools_data": {"type": "array"},
                "category_rank": {"type": "object"},
            },
            "additionalProperties": False,
        },
        "weights": {
            "type": "object",
            "patternProperties": {
                "^[a-z_]+$": {"type": "number"},
            },
            "additionalProperties": True,
        },
    },
    "additionalProperties": False,
}

_SNAPSHOT_VALIDATOR = Draft202012Validator(SNAPSHOT_SCHEMA)
_CANONICAL_VALIDATOR = Draft202012Validator(CANONICAL_SCHEMA)


def validate_snapshot(payload: Dict[str, Any]) -> None:
    _SNAPSHOT_VALIDATOR.validate(payload)


def validate_canonical(payload: Dict[str, Any]) -> None:
    _CANONICAL_VALIDATOR.validate(payload)


def normalise_timestamp(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


__all__ = [
    "ValidationError",
    "SNAPSHOT_SCHEMA",
    "CANONICAL_SCHEMA",
    "validate_snapshot",
    "validate_canonical",
    "normalise_timestamp",
]
