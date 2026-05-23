from pathlib import Path
from app.services.llm import ask_llm


def ask_question(question, agent_path):
    memory_path = Path(agent_path) / "memory"

    content = ""

    for file in memory_path.rglob("*.md"):
        # FIX: encoding="utf-8" — Windows defaults to cp1252 which
        # crashes on unicode characters like the macron in "Koan"
        content += file.read_text(encoding="utf-8")
        content += "\n\n"

    prompt = f"""
You are Koan, an institutional memory agent.

Answer using ONLY the provided memory. For every claim:
- Cite the source file or PR
- Rate confidence: HIGH / MEDIUM / LOW
- Mention who on the team knows the most about this

If the memory doesn't contain relevant information, say "I don't have memory of that."

Question:
{question}

Memory:
{content}
"""

    answer = ask_llm(prompt)

    return {
        "answer": answer
    }