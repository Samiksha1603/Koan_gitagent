"""
LLM service with multi-provider support.

Priority order:
1. Google Gemini (free tier - 15 RPM, 1500/day)
2. Groq (free tier - 30 RPM) 
3. OpenAI (if you have credits)
4. Rule-based fallback (no API needed)

Set ONE of these in your .env:
  GEMINI_API_KEY=your-key      (get from https://aistudio.google.com/apikey)
  GROQ_API_KEY=your-key        (get from https://console.groq.com/keys)
  OPENAI_API_KEY=your-key      (requires billing)
"""

import os
import json
import requests


def ask_llm(prompt: str, system: str = None) -> str:
    """Try each provider in order, fall back to rule-based if all fail."""

    # 1. Try Gemini (free)
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_key:
        try:
            return _call_gemini(prompt, system, gemini_key)
        except Exception as e:
            print(f"[LLM] Gemini failed: {e}")

    # 2. Try Groq (free)
    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key:
        try:
            return _call_groq(prompt, system, groq_key)
        except Exception as e:
            print(f"[LLM] Groq failed: {e}")

    # 3. Try OpenAI (paid)
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key:
        try:
            return _call_openai(prompt, system, openai_key)
        except Exception as e:
            print(f"[LLM] OpenAI failed: {e}")

    # 4. Fallback - no API needed
    print("[LLM] All providers failed or no API key set. Using rule-based fallback.")
    return _fallback(prompt)


def _call_gemini(prompt: str, system: str, api_key: str) -> str:
    """Google Gemini API (free tier: 15 RPM, 1500 req/day)."""
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    contents = []
    if system:
        contents.append({"role": "user", "parts": [{"text": system}]})
        contents.append({"role": "model", "parts": [{"text": "Understood. I will follow these instructions."}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    resp = requests.post(url, json={
        "contents": contents,
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 4096,
        }
    }, timeout=60)

    if resp.status_code != 200:
        raise Exception(f"Gemini API error {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _call_groq(prompt: str, system: str, api_key: str) -> str:
    """Groq API (free tier: 30 RPM, 14400 req/day)."""
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 4096,
        },
        timeout=60,
    )

    if resp.status_code != 200:
        raise Exception(f"Groq API error {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _call_openai(prompt: str, system: str, api_key: str) -> str:
    """OpenAI API (requires billing/credits)."""
    model = os.getenv("MODEL", "gpt-4o-mini")
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 4096,
        },
        timeout=60,
    )

    if resp.status_code == 429:
        raise Exception("OpenAI rate limit / quota exceeded")
    if resp.status_code != 200:
        raise Exception(f"OpenAI API error {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _fallback(prompt: str) -> str:
    """Rule-based extraction when no LLM is available."""
    import re

    sections = {
        "onboarding": "# Onboarding Notes\n\nThis repository was analyzed using rule-based extraction (no LLM API key configured).\n\n",
        "architecture": "# Architecture Summary\n\n",
        "systems": "# Systems Overview\n\n",
        "risks": "# Risks and Gotchas\n\n",
        "decisions": "# Engineering Decisions\n\n",
    }

    # Try to extract useful info from the prompt/analysis
    lines = prompt.split("\n")
    file_mentions = [l for l in lines if any(ext in l for ext in [".py", ".js", ".ts", ".go", ".rs", ".java", ".yaml", ".json", ".md"])]
    tech_keywords = set()
    tech_map = {
        "flask": "Flask (Python web framework)",
        "django": "Django (Python web framework)",
        "fastapi": "FastAPI (Python async web framework)",
        "react": "React (JavaScript UI library)",
        "next": "Next.js (React framework)",
        "express": "Express.js (Node.js web framework)",
        "docker": "Docker (containerization)",
        "kubernetes": "Kubernetes (container orchestration)",
        "redis": "Redis (in-memory data store)",
        "postgres": "PostgreSQL (relational database)",
        "mongodb": "MongoDB (document database)",
        "kafka": "Apache Kafka (event streaming)",
        "celery": "Celery (task queue)",
        "pytest": "pytest (testing framework)",
        "jest": "Jest (JavaScript testing)",
        "webpack": "Webpack (module bundler)",
        "vite": "Vite (build tool)",
    }

    lower_prompt = prompt.lower()
    for keyword, description in tech_map.items():
        if keyword in lower_prompt:
            tech_keywords.add(description)

    result = "# Institutional Memory (Auto-Generated)\n\n"
    result += "---\n"
    result += "confidence: MEDIUM\n"
    result += "source: automated-analysis\n"
    result += "---\n\n"

    result += "## Onboarding Notes\n\n"
    if tech_keywords:
        result += "This repository uses the following technologies:\n"
        for tech in sorted(tech_keywords):
            result += f"- {tech}\n"
    else:
        result += "- Review the repository README for setup instructions\n"
        result += "- Check for a Makefile, docker-compose.yml, or package.json for build steps\n"
    result += "\n"

    result += "## Architecture Summary\n\n"
    result += "Architecture details extracted from repository structure. Review source code for detailed understanding.\n\n"

    if file_mentions:
        result += "Key files identified:\n"
        for f in file_mentions[:15]:
            result += f"- {f.strip()}\n"
    result += "\n"

    result += "## Systems Overview\n\n"
    if tech_keywords:
        result += "Detected technology stack:\n"
        for tech in sorted(tech_keywords):
            result += f"- {tech}\n"
    result += "\n"

    result += "## Risks and Gotchas\n\n"
    result += "- Ensure all environment variables are configured before running\n"
    result += "- Check for any hardcoded paths or credentials in the codebase\n"
    result += "- Review test coverage before making changes\n\n"

    result += "## Engineering Decisions\n\n"
    result += "- Detailed decision records require LLM analysis. Configure a free API key (Gemini or Groq) for richer output.\n"

    return result