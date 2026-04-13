#!/usr/bin/env python3
"""Publish the public crill release and update the Homebrew tap."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_API_ROOT = "https://api.github.com"


@dataclass(frozen=True)
class ReleaseAsset:
    name: str
    api_url: str
    digest: str | None


@dataclass(frozen=True)
class ReleaseMetadata:
    source_repo: str
    public_repo: str
    tag: str
    version: str
    release_url: str
    assets: tuple[ReleaseAsset, ...]


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    capture: bool = True,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603,S607
        cmd,
        cwd=str(cwd) if cwd else None,
        check=check,
        text=True,
        capture_output=capture,
    )


def expected_asset_names(version: str) -> tuple[str, str]:
    return (
        f"crill_{version}_darwin_arm64.tar.gz",
        "checksums.txt",
    )


def github_request(url: str, token: str, *, accept: str) -> urllib.request.Request:
    return urllib.request.Request(
        url,
        headers={
            "Accept": accept,
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "crill-cli-release",
        },
    )


def github_json(url: str, token: str) -> dict[str, object]:
    request = github_request(url, token, accept="application/vnd.github+json")
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def fetch_source_release_metadata(
    source_repo: str,
    public_repo: str,
    version: str,
    *,
    token: str,
) -> ReleaseMetadata:
    tag = f"v{version}"
    payload = github_json(
        f"{SOURCE_API_ROOT}/repos/{source_repo}/releases/tags/{tag}",
        token,
    )
    raw_assets = payload["assets"]
    if not isinstance(raw_assets, list):
        raise SystemExit(f"invalid asset payload for {tag}")
    assets = tuple(
        ReleaseAsset(
            name=asset["name"],
            api_url=asset["url"],
            digest=asset.get("digest"),
        )
        for asset in raw_assets
    )
    names = {asset.name for asset in assets}
    missing = [name for name in expected_asset_names(version) if name not in names]
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(f"missing source release assets for {tag}: {joined}")
    release_url = payload.get("html_url")
    if not isinstance(release_url, str):
        raise SystemExit(f"missing html_url for source release {tag}")
    return ReleaseMetadata(
        source_repo=source_repo,
        public_repo=public_repo,
        tag=tag,
        version=version,
        release_url=release_url,
        assets=assets,
    )


def download_asset(asset: ReleaseAsset, destination: Path, *, token: str) -> Path:
    request = github_request(asset.api_url, token, accept="application/octet-stream")
    target = destination / asset.name
    with urllib.request.urlopen(request) as response, target.open("wb") as handle:
        handle.write(response.read())
    return target


def download_assets(meta: ReleaseMetadata, destination: Path, *, token: str) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    return [download_asset(asset, destination, token=token) for asset in meta.assets]


def release_exists(public_repo: str, tag: str) -> bool:
    result = run(
        ["gh", "release", "view", tag, "--repo", public_repo],
        capture=True,
        check=False,
    )
    return result.returncode == 0


def publish_release(public_repo: str, meta: ReleaseMetadata, notes_path: Path, asset_dir: Path) -> None:
    asset_files = [str(asset_dir / asset.name) for asset in meta.assets]
    if release_exists(public_repo, meta.tag):
        run(
            [
                "gh",
                "release",
                "edit",
                meta.tag,
                "--repo",
                public_repo,
                "--notes-file",
                str(notes_path),
                "--title",
                meta.tag,
            ],
            capture=False,
        )
        run(
            ["gh", "release", "upload", meta.tag, "--repo", public_repo, "--clobber", *asset_files],
            capture=False,
        )
        return

    run(
        [
            "gh",
            "release",
            "create",
            meta.tag,
            "--repo",
            public_repo,
            "--title",
            meta.tag,
            "--notes-file",
            str(notes_path),
            *asset_files,
        ],
        capture=False,
    )


def sha256_by_asset_name(meta: ReleaseMetadata) -> dict[str, str]:
    shas: dict[str, str] = {}
    for asset in meta.assets:
        if not asset.digest or not asset.digest.startswith("sha256:"):
            continue
        shas[asset.name] = asset.digest.removeprefix("sha256:")
    return shas


def render_homebrew_formula(meta: ReleaseMetadata, template_text: str) -> str:
    shas = sha256_by_asset_name(meta)
    arm64_name = f"crill_{meta.version}_darwin_arm64.tar.gz"
    missing = [name for name in (arm64_name,) if name not in shas]
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(f"missing sha256 digests for tap update: {joined}")
    return template_text.replace("__VERSION__", meta.version).replace(
        "__ARM64_SHA__", shas[arm64_name]
    )


def ensure_clean_repo(repo_dir: Path) -> None:
    status = run(["git", "status", "--short"], cwd=repo_dir)
    if status.stdout.strip():
        raise SystemExit(f"tap repo has uncommitted changes: {repo_dir}")


def update_homebrew_tap(
    meta: ReleaseMetadata,
    *,
    tap_repo_dir: Path,
    template_path: Path,
) -> None:
    ensure_clean_repo(tap_repo_dir)
    formula = render_homebrew_formula(meta, template_path.read_text(encoding="utf-8"))
    formula_path = tap_repo_dir / "crill.rb"
    if not formula_path.exists() or formula_path.read_text(encoding="utf-8") != formula:
        formula_path.write_text(formula, encoding="utf-8")
    run(["git", "add", "crill.rb"], cwd=tap_repo_dir)
    status = run(["git", "status", "--short"], cwd=tap_repo_dir)
    if status.stdout.strip():
        run(
            ["git", "commit", "-m", f"Bump crill to {meta.version}"],
            cwd=tap_repo_dir,
            capture=False,
        )
        run(["git", "push", "origin", "HEAD"], cwd=tap_repo_dir, capture=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="Release version without leading v")
    parser.add_argument(
        "--source-repo",
        default="corca-ai/crill",
        help="Private source repo that already contains the release assets",
    )
    parser.add_argument(
        "--public-repo",
        default=os.environ.get("GITHUB_REPOSITORY", "corca-ai/crill-cli"),
        help="Public repo that owns this workflow",
    )
    parser.add_argument(
        "--notes-path",
        type=Path,
        default=None,
        help="Release notes path inside the public repo checkout",
    )
    parser.add_argument(
        "--tap-repo-dir",
        type=Path,
        default=Path("../homebrew-tap"),
        help="Local checkout path for corca-ai/homebrew-tap",
    )
    parser.add_argument(
        "--template-path",
        type=Path,
        default=ROOT / "scripts" / "release" / "crill.rb.template",
        help="Homebrew formula template path inside the public repo checkout",
    )
    parser.add_argument(
        "--source-token-env",
        default="SOURCE_RELEASE_TOKEN",
        help="Environment variable name that stores the private-source token",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_token = os.environ.get(args.source_token_env)
    if not source_token:
        raise SystemExit(f"missing required token env: {args.source_token_env}")
    notes_path = args.notes_path or ROOT / ".release-notes" / f"v{args.version}.md"
    if not notes_path.exists():
        raise SystemExit(f"missing release notes: {notes_path}")
    meta = fetch_source_release_metadata(
        args.source_repo,
        args.public_repo,
        args.version,
        token=source_token,
    )
    with tempfile.TemporaryDirectory(prefix="crill-cli-release-") as tmp:
        asset_dir = Path(tmp)
        download_assets(meta, asset_dir, token=source_token)
        publish_release(args.public_repo, meta, notes_path, asset_dir)
    update_homebrew_tap(
        meta,
        tap_repo_dir=args.tap_repo_dir.resolve(),
        template_path=args.template_path.resolve(),
    )
    print(f"Published public release {meta.tag} to {args.public_repo}")


if __name__ == "__main__":
    main()
