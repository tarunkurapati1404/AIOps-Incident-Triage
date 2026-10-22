"""AI Incident Triage Bot — reads pytest JUnit XML and asks an LLM to diagnose failures.

Usage:
    python triage/analyzer.py                     # local Ollama (default, free)
    LLM_PROVIDER=openai python triage/analyzer.py # cloud OpenAI (uses your credit)
"""

import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

PROVIDER = os.getenv("LLM_PROVIDER", "ollama")   # "ollama" or "openai"
OLLAMA_URL = "http://localhost:11434/api/generate"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
MODEL = "llama3.1:8b" if PROVIDER == "ollama" else "gpt-4o-mini"
REPORT_PATH = Path("triage-report.md")


def extract_failures(xml_path: str = "test-results.xml") -> list[dict]:
    """Pull each failing test's name and message out of the JUnit XML."""
    tree = ET.parse(xml_path)
    failures = []
    for case in tree.iter("testcase"):
        failure = case.find("failure")
        if failure is not None:
            failures.append({
                "test": f"{case.get('classname')}::{case.get('name')}",
                "error": (failure.get("message") or "").strip(),
            })
    return failures


def build_prompt(failures: list[dict]) -> str:
    lines = "\n".join(f"- {f['test']}: {f['error']}" for f in failures)
    return f"""You are an expert AIOps incident triage bot.
The CI pipeline failed. Here are the failing tests:

{lines}

Respond in EXACTLY this format:
SEVERITY: (one of CRITICAL / HIGH / MEDIUM / LOW, with one line why)
ROOT CAUSE: (one or two sentences naming the most likely code-level cause)
SUGGESTED FIX: (one or two sentences)
CONFIDENCE: (percentage)"""


def ask_ollama(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=300,
    )
    response.raise_for_status()
    return response.json()["response"]


def ask_openai(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.exit("❌ Set OPENAI_API_KEY first: export OPENAI_API_KEY='sk-...'")
    response = requests.post(
        OPENAI_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def main() -> None:
    failures = extract_failures()
    if not failures:
        print("✅ No failures found in test-results.xml — nothing to triage.")
        return

    print(f"🚨 {len(failures)} failure(s) detected. Provider: {PROVIDER} ({MODEL})\n")
    prompt = build_prompt(failures)
    report = ask_ollama(prompt) if PROVIDER == "ollama" else ask_openai(prompt)

    REPORT_PATH.write_text(f"# AI Triage Report\n\n{report}\n")
    print(report)
    print(f"\n📄 Full report saved to {REPORT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except requests.ConnectionError:
        sys.exit("❌ Cannot reach Ollama at localhost:11434 — is it running? ('ollama serve')")