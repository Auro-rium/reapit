from __future__ import annotations
import io, os, re, zipfile
from pathlib import PurePosixPath
import httpx

IGNORE = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}
MAJOR = {"readme.md", "contributing.md", "license", "pyproject.toml", "package.json", "cargo.toml", "go.mod", "dockerfile", "docker-compose.yml", "makefile"}

def parse_url(url: str) -> tuple[str, str]:
    m = re.match(r"https?://github\.com/([^/]+)/([^/#]+)", url.strip())
    if not m: raise ValueError("Expected a GitHub URL like https://github.com/owner/repository")
    return m.group(1), m.group(2).removesuffix(".git")

def fetch_contributors(info: dict) -> list[dict]:
    url = info.get("contributors_url")
    if not url: return []
    try:
        with httpx.Client(timeout=15, headers={"User-Agent": "reapit"}) as client:
            response = client.get(url, params={"per_page": 10})
            response.raise_for_status()
            return [{"login": x.get("login"), "contributions": x.get("contributions"), "url": x.get("html_url")} for x in response.json()]
    except httpx.HTTPError:
        return []

def fetch_repo(url: str) -> tuple[dict, dict[str, str]]:
    owner, name = parse_url(url)
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "reapit"}
    token = os.getenv("GITHUB_TOKEN")
    if token: headers["Authorization"] = f"Bearer {token}"
    with httpx.Client(timeout=30, follow_redirects=True, headers=headers) as client:
        meta = client.get(f"https://api.github.com/repos/{owner}/{name}")
        meta.raise_for_status(); info = meta.json()
        archive_url = info.get("zipball_url") or f"https://codeload.github.com/{owner}/{name}/zip/refs/heads/{info.get('default_branch', 'main')}"
        archive = client.get(archive_url); archive.raise_for_status()
    max_bytes = int(os.getenv("MAX_REPO_BYTES", "50000000"))
    if len(archive.content) > max_bytes:
        actual = len(archive.content) / 1_000_000
        limit = max_bytes / 1_000_000
        raise ValueError(f"Repository archive is {actual:.1f} MB; configured limit is {limit:.1f} MB. Increase MAX_REPO_BYTES or exclude large generated/assets files.")
    files: dict[str, str] = {}
    limit = int(os.getenv("MAX_FILE_CHARS", "30000"))
    with zipfile.ZipFile(io.BytesIO(archive.content)) as z:
        for member in z.infolist():
            parts = PurePosixPath(member.filename).parts[1:]
            if not parts or any(p in IGNORE for p in parts) or member.is_dir(): continue
            name = "/".join(parts)
            if member.file_size > 500_000: continue
            try: text = z.read(member).decode("utf-8", errors="replace")
            except Exception: continue
            if "\x00" in text: continue
            files[name] = text[:limit]
    info["source_url"] = url
    return info, files
