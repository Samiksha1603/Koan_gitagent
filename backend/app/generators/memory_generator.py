from app.services.llm import ask_llm


def generate_memories(analysis):
    # Build a rich context from the analysis
    context_parts = []

    if analysis.get("readme"):
        context_parts.append(f"## README\n{analysis['readme'][:3000]}")

    if analysis.get("frameworks"):
        context_parts.append(f"## Frameworks Detected\n{', '.join(analysis['frameworks'])}")

    if analysis.get("dependencies"):
        context_parts.append(f"## Dependencies\n{', '.join(analysis['dependencies'][:30])}")

    if analysis.get("folders"):
        context_parts.append(f"## Project Structure\nTop-level folders: {', '.join(analysis['folders'])}")

    if analysis.get("important_files"):
        context_parts.append(f"## Key Files\n{chr(10).join(analysis['important_files'][:20])}")

    if analysis.get("git_history"):
        context_parts.append(f"## Git History (recent commits)\n{analysis['git_history'][:3000]}")

    if analysis.get("contributors"):
        contrib_lines = [f"- {c['name']}: {c['commits']} commits" for c in analysis['contributors']]
        context_parts.append(f"## Contributors (who knows what)\n{chr(10).join(contrib_lines)}")

    if analysis.get("merge_commits"):
        context_parts.append(f"## Merge Commits / PR History (engineering decisions)\n{analysis['merge_commits'][:2000]}")

    if analysis.get("recent_changes"):
        context_parts.append(f"## Recently Active Areas\n{analysis['recent_changes']}")

    full_context = "\n\n".join(context_parts)

    prompt = f"""
You are generating institutional memory for an engineering repository.
Your job is to capture what a senior engineer would tell a new hire on day one.
Focus on the WHY behind things, not just the WHAT.

Repository Analysis:
{full_context}

Generate the following sections as clean markdown:

## Onboarding Notes
What should a new engineer know on day 1? Setup gotchas, key concepts,
where to start reading code. Be specific based on the actual repo structure.

## Architecture Summary
How is the codebase organized? What are the main components and how do they connect?
Reference actual folders and files from the analysis.

## Engineering Decisions
What major decisions are visible in the git history? Look at merge commits,
refactors, migrations, dependency changes. Explain the likely WHY behind them.

## Key Contributors & Expertise Map
Who are the main contributors? Based on their commit patterns, what areas
does each person own or know best?

## Risks & Gotchas
What could go wrong? What areas have lots of recent churn (potential instability)?
What dependencies or patterns look risky? What tribal knowledge is critical?

## Systems Overview
What external systems, databases, APIs, or services does this project depend on?
What should you know about how they connect?

For each section include:
- Specific evidence (file names, commit messages, contributor names)
- Confidence level (HIGH if directly from code/commits, MEDIUM if inferred)
- Source attribution (which commit, file, or contributor the knowledge came from)
"""

    return ask_llm(prompt)