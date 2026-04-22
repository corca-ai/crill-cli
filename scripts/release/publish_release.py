#!/usr/bin/env python3
"""Update the Homebrew tap from an existing public crill release."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ReleaseAsset:
    name: str
    digest: str | None


@dataclass(frozen=True)
class ReleaseMetadata:
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


def fetch_public_release_metadata(
    public_repo: str,
    version: str,
) -> ReleaseMetadata:
    tag = f"v{version}"
    result = run(
        [
            "gh",
            "release",
            "view",
            tag,
            "--repo",
            public_repo,
            "--json",
            "tagName,url,assets",
        ],
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"public release {tag} is not available in {public_repo} yet")
    payload = json.loads(result.stdout)
    raw_assets = payload["assets"]
    if not isinstance(raw_assets, list):
        raise SystemExit(f"invalid asset payload for {tag}")
    assets = tuple(
        ReleaseAsset(
            name=asset["name"],
            digest=asset.get("digest"),
        )
        for asset in raw_assets
    )
    names = {asset.name for asset in assets}
    missing = [name for name in expected_asset_names(version) if name not in names]
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(f"missing source release assets for {tag}: {joined}")
    release_url = payload.get("url")
    if not isinstance(release_url, str):
        raise SystemExit(f"missing release url for public release {tag}")
    return ReleaseMetadata(
        public_repo=public_repo,
        tag=tag,
        version=version,
        release_url=release_url,
        assets=assets,
    )


def wait_for_public_release(
    public_repo: str,
    version: str,
    *,
    timeout_seconds: int,
    interval_seconds: int,
) -> ReleaseMetadata:
    deadline = time.monotonic() + timeout_seconds
    last_error: str | None = None
    while time.monotonic() < deadline:
        try:
            return fetch_public_release_metadata(public_repo, version)
        except SystemExit as exc:
            last_error = str(exc)
        time.sleep(interval_seconds)
    detail = last_error or f"timed out waiting for public release v{version}"
    raise SystemExit(detail)


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


def ensure_git_identity(repo_dir: Path) -> None:
    name = run(
        ["git", "config", "--local", "--get", "user.name"],
        cwd=repo_dir,
        check=False,
    ).stdout.strip()
    email = run(
        ["git", "config", "--local", "--get", "user.email"],
        cwd=repo_dir,
        check=False,
    ).stdout.strip()
    if name and email:
        return
    run(
        ["git", "config", "--local", "user.name", "github-actions[bot]"],
        cwd=repo_dir,
        capture=False,
    )
    run(
        [
            "git",
            "config",
            "--local",
            "user.email",
            "41898282+github-actions[bot]@users.noreply.github.com",
        ],
        cwd=repo_dir,
        capture=False,
    )


def update_homebrew_tap(
    meta: ReleaseMetadata,
    *,
    tap_repo_dir: Path,
    template_path: Path,
) -> None:
    ensure_clean_repo(tap_repo_dir)
    ensure_git_identity(tap_repo_dir)
    formula = render_homebrew_formula(meta, template_path.read_text(encoding="utf-8"))
    formula_path = tap_repo_dir / "Formula" / "crill.rb"
    formula_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_formula_path = tap_repo_dir / "crill.rb"
    if not formula_path.exists() or formula_path.read_text(encoding="utf-8") != formula:
        formula_path.write_text(formula, encoding="utf-8")
    if legacy_formula_path.exists():
        legacy_formula_path.unlink()
    run(["git", "add", "Formula/crill.rb", "crill.rb"], cwd=tap_repo_dir)
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
        "--public-repo",
        default=os.environ.get("GITHUB_REPOSITORY", "corca-ai/crill-cli"),
        help="Public repo that owns this workflow",
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
        default=ROOT / "scripts" / "release" / "crill.rb",
        help="Homebrew formula template path inside the public repo checkout",
    )
    parser.add_argument(
        "--wait-timeout",
        type=int,
        default=180,
        help="Maximum seconds to wait for the public release assets to exist",
    )
    parser.add_argument(
        "--wait-interval",
        type=int,
        default=5,
        help="Polling interval while waiting for the public release",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    meta = wait_for_public_release(
        args.public_repo,
        args.version,
        timeout_seconds=args.wait_timeout,
        interval_seconds=args.wait_interval,
    )
    update_homebrew_tap(
        meta,
        tap_repo_dir=args.tap_repo_dir.resolve(),
        template_path=args.template_path.resolve(),
    )
    sys.stdout.write(f"Updated corca-ai/homebrew-tap from public release {meta.tag}\n")


if __name__ == "__main__":
    main()
