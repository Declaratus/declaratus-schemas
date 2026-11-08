"""Contract tests for the published v0.1.0 changeset schema.

These pin behavior consumers already rely on. A failure here means the
published contract moved, which v0.1.0 does not allow; ship the change under a
new version instead (see docs/SCHEMA-VERSIONING.md).

Run from the repo root: python -m pytest tests
Needs: pytest, jsonschema>=4.18, PyYAML.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schemas" / "v0" / "changeset.schema.json"
EXAMPLES = sorted((ROOT / "examples").glob("*.example.yaml"))
PINNED_ID = (
    "https://raw.githubusercontent.com/Declaratus/declaratus-schemas/"
    "v0.1.0/schemas/v0/changeset.schema.json"
)
BASE = {"schema_version": "0.1.0", "platform": "github_projects", "changeset_id": "demo"}


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def validator(schema: dict) -> Draft202012Validator:
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _errors(validator: Draft202012Validator, doc: dict) -> list[str]:
    return [e.message for e in validator.iter_errors(doc)]


def test_schema_id_is_tag_pinned(schema: dict) -> None:
    assert schema["$id"] == PINNED_ID


def test_five_examples_present() -> None:
    assert len(EXAMPLES) == 5


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_example_is_valid(path: Path, validator: Draft202012Validator) -> None:
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert _errors(validator, doc) == []


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_example_board_target_is_github_web_url(path: Path) -> None:
    """Examples spell GitHub.com as its https web URL. Consumers must accept
    that spelling as GitHub.com, not only the bare host or API host."""
    target = yaml.safe_load(path.read_text(encoding="utf-8"))["board"]["target"]
    assert target == "https://github.com"
    parts = urlsplit(target)
    assert (parts.scheme, parts.netloc) == ("https", "github.com")


def test_resolved_decision_accepts_empty_resolution(validator: Draft202012Validator) -> None:
    """`required` is a presence check. An empty string satisfies it in v0.1."""
    doc = dict(BASE, decisions=[{"id": "d1", "title": "x", "state": "resolved", "resolution": ""}])
    assert _errors(validator, doc) == []


@pytest.mark.parametrize(
    "decision",
    [
        {"id": "d1", "title": "x", "state": "resolved"},
        {"id": "d1", "title": "x", "state": "resolved", "resolution": None},
    ],
    ids=["absent", "null"],
)
def test_resolved_decision_needs_resolution_string(
    decision: dict, validator: Draft202012Validator
) -> None:
    assert _errors(validator, dict(BASE, decisions=[decision]))


def test_changeset_id_pattern_is_unchanged(schema: dict) -> None:
    prop = schema["properties"]["changeset_id"]
    assert prop["pattern"] == "^[a-z0-9][a-z0-9-]*$"
    assert (prop["minLength"], prop["maxLength"]) == (1, 64)


def test_python_jsonschema_accepts_one_trailing_newline(validator: Draft202012Validator) -> None:
    """Records an engine difference, not a contract rule. The Python
    `jsonschema` package uses `re.search`, where `$` also matches before one
    final newline. Default, non-multiline ECMA-262 regex semantics reject it;
    multiline mode differs. This is not an all-validator or Ajv integration
    claim. Authors should avoid trailing newlines."""
    assert _errors(validator, dict(BASE, changeset_id="demo\n")) == []
    assert _errors(validator, dict(BASE, changeset_id="demo\n\n"))


@pytest.mark.parametrize("bad", ["Demo", "-demo", "demo_1", "", "a" * 65])
def test_invalid_changeset_ids_rejected(bad: str, validator: Draft202012Validator) -> None:
    assert _errors(validator, dict(BASE, changeset_id=bad))
