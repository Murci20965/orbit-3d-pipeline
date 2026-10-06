import os

os.environ.setdefault("GROQ_API_KEY", "test-key-not-used")

from app.services.groq_ai import TEXT_MODEL, VISION_MODEL, _answer  # noqa: E402

RETIRED = {"llama-3.3-70b-versatile", "meta-llama/llama-4-scout-17b-16e-instruct"}


def test_no_retired_models():
    assert TEXT_MODEL not in RETIRED and VISION_MODEL not in RETIRED


def test_answer_strips_reasoning_blocks():
    raw = "<think>the user wants a telescope...</think>\nA refracting telescope bends light."
    assert _answer(raw) == "A refracting telescope bends light."


def test_answer_handles_none():
    assert _answer(None) == ""
