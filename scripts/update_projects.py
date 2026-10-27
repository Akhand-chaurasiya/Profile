
import json
import urllib.request
from datetime import datetime

USERNAME = "Akhand-chaurasiya"
PROFILE_REPO = USERNAME

START_MARKER = "<!-- PROJECTS-START -->"
END_MARKER = "<!-- PROJECTS-END -->"


def get_repositories():
    url = (
        f"https://api.github.com/users/{USERNAME}/repos"
        "?per_page=100&sort=pushed&type=owner"
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-profile-updater",
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        repos = json.load(response)

    repos = [
        repo for repo in repos
        if not repo["fork"]
        and repo["name"].lower() != PROFILE_REPO.lower()
    ]

    return sorted(
        repos,
        key=lambda repo: repo.get("pushed_at") or "",
        reverse=True,
    )


def format_date(value):
    if not value:
        return "Unknown"

    date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return date.strftime("%d %b %Y")


def build_project_list(repos):
    if not repos:
        return "_No public projects found._"

    lines = [
        "| Project | Description | Language | Last pushed |",
        "|---|---|---|---|",
    ]

    for repo in repos[:8]:
        name = repo["name"]
        url = repo["html_url"]
        description = (
            repo.get("description") or "No description provided"
        ).replace("|", "\\|").replace("\n", " ")

        language = (repo.get("language") or "Not specified").replace("|", "\\|")

        lines.append(
            f"| [{name}]({url}) | {description} | "
            f"{language} | {format_date(repo.get('pushed_at'))} |"
        )

    lines.extend([
        "",
        "_Automatically updated by GitHub Actions. "
        "Last-pushed dates indicate activity, not completion._",
    ])

    return "\n".join(lines)


def update_readme(project_list):
    with open("README.md", encoding="utf-8") as file:
        readme = file.read()

    if START_MARKER not in readme or END_MARKER not in readme:
        raise ValueError(
            "Add PROJECTS-START and PROJECTS-END markers to README.md."
        )

    start = readme.index(START_MARKER) + len(START_MARKER)
    end = readme.index(END_MARKER)

    if end < start:
        raise ValueError("Project markers are in the wrong order.")

    updated = (
        readme[:start] + "\n" + project_list + "\n" + readme[end:]
    )

    with open("README.md", "w", encoding="utf-8") as file:
        file.write(updated)

    print("Project list updated successfully.")


if __name__ == "__main__":
    update_readme(build_project_list(get_repositories()))
