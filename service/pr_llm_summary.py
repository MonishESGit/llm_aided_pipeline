import os
import textwrap

from github import Github
from openai import OpenAI


def get_pr_diff(pr):
    """
    Build a compact diff string from the PR.
    We only include patches (not full files) and truncate if too long.
    """
    parts = []
    for f in pr.get_files():
        if f.patch:  # patch is the unified diff for that file
            parts.append(f"File: {f.filename}\n{f.patch}\n")

    diff = "\n\n".join(parts)

    # Avoid sending a huge diff to the API
    max_chars = 6000
    if len(diff) > max_chars:
        diff = diff[:max_chars] + "\n\n...[diff truncated]"

    return diff


def build_prompt(diff: str) -> str:
    prompt = f"""
You are helping review a pull request.

Summarize the following code changes in clear, simple language.
Focus on:
- What the main changes are
- Which parts of the codebase they affect
- Any potential readability or maintainability issues

If the diff is noisy or partial, just do your best.

Diff:
{diff}
"""
    # remove leading indentation
    return textwrap.dedent(prompt)


def main():
    # Read environment variables
    openai_api_key = os.environ["OPENAI_API_KEY"]
    github_token = os.environ["GITHUB_TOKEN"]
    repo_name = os.environ["GITHUB_REPOSITORY"]
    pr_number = int(os.environ["PR_NUMBER"])

    # Set up clients
    client = OpenAI(api_key=openai_api_key)
    gh = Github(github_token)

    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    diff = get_pr_diff(pr)
    if not diff.strip():
        pr.create_issue_comment("LLM summary: No diff found or PR is empty.")
        return

    prompt = build_prompt(diff)

    # Call OpenAI for a short summary
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_tokens=300,
    )

    summary = response.choices[0].message.content.strip()

    comment_body = (
        "### 🤖 LLM Code Summary\n"
        "Here’s an auto-generated summary of this PR:\n\n"
        f"{summary}\n\n"
        "_Note: This is a helper summary, not a replacement for a full review._"
    )

    pr.create_issue_comment(comment_body)


if __name__ == "__main__":
    main()
