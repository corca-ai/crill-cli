#!/bin/sh
# crill installer — Apple Silicon macOS binary distribution.
#
# Mirrors the pattern in ../craken-spaces-cli/install.sh (public-trust
# installer script for the GitHub Releases tarball flow) but rejects
# non-Darwin platforms with a clear pointer to the source-install path.
#
# Environment overrides:
#   VERSION     — pin a specific tag like "v0.2.0" instead of latest
#   INSTALL_DIR — target directory (default $HOME/.local/bin)
set -eu

REPO="corca-ai/crill-cli"
BINARY="crill"
DEFAULT_INSTALL_DIR="$HOME/.local/bin"

path_contains_dir() {
  case ":${PATH:-}:" in
    *":$1:"*) return 0 ;;
  esac
  return 1
}

detect_shell_name() {
  if [ -n "${SHELL:-}" ]; then
    basename "$SHELL"
    return 0
  fi
  if [ -n "${ZSH_VERSION:-}" ]; then
    printf 'zsh\n'
    return 0
  fi
  if [ -n "${BASH_VERSION:-}" ]; then
    printf 'bash\n'
    return 0
  fi
  printf 'sh\n'
}

current_session_path_command() {
  case "$1" in
    fish)
      printf 'set -gx PATH "$HOME/.local/bin" $PATH\n'
      ;;
    *)
      printf 'export PATH="$HOME/.local/bin:$PATH"\n'
      ;;
  esac
}

shell_init_file() {
  case "$1" in
    zsh)
      printf '%s/.zprofile\n' "$HOME"
      ;;
    bash)
      if [ -f "$HOME/.bash_profile" ] || [ ! -f "$HOME/.bashrc" ]; then
        printf '%s/.bash_profile\n' "$HOME"
      else
        printf '%s/.bashrc\n' "$HOME"
      fi
      ;;
    fish)
      printf '%s/.config/fish/config.fish\n' "$HOME"
      ;;
    *)
      return 1
      ;;
  esac
}

shell_init_snippet() {
  case "$1" in
    fish)
      printf 'fish_add_path -m ~/.local/bin\n'
      ;;
    zsh|bash|sh)
      printf 'export PATH="$HOME/.local/bin:$PATH"\n'
      ;;
    *)
      return 1
      ;;
  esac
}

ensure_path_reachability() {
  install_dir="$1"
  shell_name="$2"

  if path_contains_dir "$install_dir"; then
    return 0
  fi

  if [ "$install_dir" != "$DEFAULT_INSTALL_DIR" ]; then
    echo "Install directory is not on PATH: $install_dir" >&2
    echo "Add it to PATH before using $BINARY. For this shell session, run:" >&2
    printf '    export PATH="%s:$PATH"\n' "$install_dir" >&2
    return 0
  fi

  init_file="$(shell_init_file "$shell_name" 2>/dev/null || true)"
  init_snippet="$(shell_init_snippet "$shell_name" 2>/dev/null || true)"

  echo "PATH does not include $install_dir yet."
  if [ -n "$init_file" ] && [ -n "$init_snippet" ]; then
    init_parent=$(dirname "$init_file")
    mkdir -p "$init_parent"
    touch "$init_file"
    if grep -F "$install_dir" "$init_file" >/dev/null 2>&1; then
      echo "PATH already references $install_dir in $init_file"
    else
      printf '\n%s\n' "$init_snippet" >> "$init_file"
      echo "Added PATH update to $init_file"
    fi
  else
    echo "Could not determine a shell init file automatically for shell: $shell_name" >&2
  fi

  echo "For this shell session, run:"
  printf '    %s' "$(current_session_path_command "$shell_name")"
}

OS=$(uname -s | tr '[:upper:]' '[:lower:]')
if [ "$OS" != "darwin" ]; then
  cat >&2 <<'EOF'
crill does not ship a prebuilt binary for this operating system.

The public binary distribution supports Apple Silicon macOS via
install.sh. Linux, Windows, and Intel macOS are not part of the
current public binary surface. See
https://github.com/corca-ai/crill-cli for supported install paths.
EOF
  exit 1
fi

ARCH=$(uname -m)
case "$ARCH" in
  aarch64|arm64) ARCH="arm64" ;;
  x86_64|amd64)
    cat >&2 <<'EOF'
crill does not ship a prebuilt binary for Intel macOS.

The public prebuilt distribution currently supports Apple Silicon macOS
only. On Intel Macs, see https://github.com/corca-ai/crill-cli for
supported install paths.
EOF
    exit 1
    ;;
  *)
    echo "crill: unsupported macOS architecture: $ARCH" >&2
    exit 1
    ;;
esac

INSTALL_DIR="${INSTALL_DIR:-$DEFAULT_INSTALL_DIR}"
mkdir -p "$INSTALL_DIR"
if [ ! -w "$INSTALL_DIR" ] 2>/dev/null; then
  echo "crill: install directory is not writable: $INSTALL_DIR" >&2
  exit 1
fi

VERSION="${VERSION:-$(curl -sSf "https://api.github.com/repos/$REPO/releases/latest" | grep '"tag_name"' | cut -d'"' -f4)}"
if [ -z "$VERSION" ]; then
  echo "crill: failed to determine latest version" >&2
  exit 1
fi
VERSION_NUM="${VERSION#v}"

ARCHIVE="${BINARY}_${VERSION_NUM}_darwin_${ARCH}.tar.gz"
URL="https://github.com/$REPO/releases/download/$VERSION/$ARCHIVE"
CHECKSUMS_URL="https://github.com/$REPO/releases/download/$VERSION/checksums.txt"

verify_checksum() {
  archive_path="$1"
  checksums_path="$2"
  expected="$(awk -v file="$ARCHIVE" '$2 == file { print $1 }' "$checksums_path")"
  if [ -z "$expected" ]; then
    echo "crill: missing checksum for $ARCHIVE" >&2
    exit 1
  fi
  if command -v sha256sum >/dev/null 2>&1; then
    actual="$(sha256sum "$archive_path" | awk '{print $1}')"
  elif command -v shasum >/dev/null 2>&1; then
    actual="$(shasum -a 256 "$archive_path" | awk '{print $1}')"
  else
    echo "crill: missing required command (sha256sum or shasum)" >&2
    exit 1
  fi
  if [ "$actual" != "$expected" ]; then
    echo "crill: checksum verification failed for $ARCHIVE" >&2
    exit 1
  fi
}

echo "Installing $BINARY $VERSION (darwin/$ARCH) to $INSTALL_DIR"
SHELL_NAME="$(detect_shell_name)"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

curl -sSfL "$URL" -o "$TMP/$ARCHIVE"
curl -sSfL "$CHECKSUMS_URL" -o "$TMP/checksums.txt"
verify_checksum "$TMP/$ARCHIVE" "$TMP/checksums.txt"
tar xzf "$TMP/$ARCHIVE" -C "$TMP"

if [ ! -f "$TMP/$BINARY" ] || [ ! -d "$TMP/_internal" ]; then
  echo "crill: archive missing one-dir bundle contents" >&2
  exit 1
fi
if [ ! -d "$TMP/runtime/current" ] || [ ! -f "$TMP/runtime/version.txt" ]; then
  echo "crill: archive missing owned runtime payload" >&2
  exit 1
fi
if [ ! -x "$TMP/runtime/current/bin/node" ] || [ ! -x "$TMP/runtime/current/bin/agent-device" ]; then
  echo "crill: archive owned runtime payload is incomplete" >&2
  exit 1
fi
if [ ! -d "$TMP/runtime/current/lib/node_modules/agent-device" ]; then
  echo "crill: archive owned runtime agent-device package is missing" >&2
  exit 1
fi
if [ ! -d "$TMP/runtime/current/lib/node_modules/agent-device/ios-runner" ]; then
  echo "crill: archive owned runtime agent-device iOS runner is missing" >&2
  exit 1
fi

BUNDLE_DIR="$INSTALL_DIR/$BINARY.bundle"
rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR"
install "$TMP/$BINARY" "$BUNDLE_DIR/$BINARY"
cp -R "$TMP/_internal" "$BUNDLE_DIR/_internal"
ln -sf "$BUNDLE_DIR/$BINARY" "$INSTALL_DIR/$BINARY"
echo "Installed launcher $INSTALL_DIR/$BINARY"
echo "Installed runtime bundle $BUNDLE_DIR"

# Record the install method so `crill doctor` can report the channel
# without having to guess from sys.executable heuristics. The manifest
# schema is owned by the crill binary and consumed by `crill doctor`.
# World-readable (0o644) because it contains no secrets.
MANIFEST_DIR="$HOME/.crill"
MANIFEST_PATH="$MANIFEST_DIR/install.json"
RUNTIME_MANIFEST_PATH="$MANIFEST_DIR/runtime.json"
RUNTIME_DIR="$MANIFEST_DIR/runtime"
RUNTIME_STAGE_DIR="$MANIFEST_DIR/runtime.installing.$$"
mkdir -p "$MANIFEST_DIR"
chmod 0700 "$MANIFEST_DIR" 2>/dev/null || true
INSTALLED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
GATE_URL_DEFAULT="https://crill-gate.donghun.workers.dev"
RUNTIME_VERSION=$(tr -d '\n' < "$TMP/runtime/version.txt")
if [ -z "$RUNTIME_VERSION" ]; then
  echo "crill: owned runtime version is missing from the archive" >&2
  exit 1
fi
# Sweep stale artifacts an earlier installer may have left behind so
# `~/.crill/runtime/` keeps only `current/` (and optionally a future
# `previous/`), matching the runtime cache policy that `crill doctor`
# asserts via `install.runtime.cache`. Runs before staging so the
# current PID's stage dir is never included.
rm -rf "$RUNTIME_STAGE_DIR"
find "$MANIFEST_DIR" -mindepth 1 -maxdepth 1 -type d -name 'runtime.installing.*' -exec rm -rf {} + 2>/dev/null || true
if [ -d "$RUNTIME_DIR" ]; then
  for entry in "$RUNTIME_DIR"/*; do
    # `[ -e ]` is false for broken symlinks; keep them sweepable.
    [ -e "$entry" ] || [ -L "$entry" ] || continue
    case "$(basename "$entry")" in
      current|previous) ;;
      *) rm -rf "$entry" ;;
    esac
  done
fi
mkdir -p "$RUNTIME_STAGE_DIR"
ditto "$TMP/runtime/current" "$RUNTIME_STAGE_DIR/current"
mkdir -p "$RUNTIME_DIR"
rm -rf "$RUNTIME_DIR/current"
mv "$RUNTIME_STAGE_DIR/current" "$RUNTIME_DIR/current"
rmdir "$RUNTIME_STAGE_DIR" 2>/dev/null || true
echo "Installed owned iOS runtime $RUNTIME_VERSION into $RUNTIME_DIR/current"
cat > "$RUNTIME_MANIFEST_PATH" <<JSON
{
  "schema_version": 1,
  "root_path": "$RUNTIME_DIR/current",
  "version": "$RUNTIME_VERSION",
  "installed_at": "$INSTALLED_AT",
  "node_path": "$RUNTIME_DIR/current/bin/node",
  "agent_device_path": "$RUNTIME_DIR/current/bin/agent-device"
}
JSON
chmod 0644 "$RUNTIME_MANIFEST_PATH"
echo "Recorded runtime manifest at $RUNTIME_MANIFEST_PATH"
cat > "$MANIFEST_PATH" <<JSON
{
  "schema_version": 1,
  "method": "install.sh",
  "version": "$VERSION_NUM",
  "installed_at": "$INSTALLED_AT",
  "binary_path": "$INSTALL_DIR/$BINARY",
  "gate_url": "${CRILL_GATE_URL:-$GATE_URL_DEFAULT}"
}
JSON
chmod 0644 "$MANIFEST_PATH"
echo "Recorded install manifest at $MANIFEST_PATH"
ensure_path_reachability "$INSTALL_DIR" "$SHELL_NAME"

# Best-effort warm-up so a successful first boot happens during install
# rather than during the operator's first explicit command. Keep the
# install successful even if Gatekeeper or host policy blocks execution.
if "$INSTALL_DIR/$BINARY" --version >/dev/null 2>&1; then
  echo "Warm-up succeeded for $INSTALL_DIR/$BINARY"
else
  echo "Warm-up skipped or blocked; the first manual launch may still be slow." >&2
fi

cat <<EOF

Gatekeeper note: crill is not Apple-notarized yet, so the
first launch will be blocked by macOS. Right-click the binary in
Finder, choose "Open", and confirm once to add it to the Gatekeeper
exception list. For install.sh, approve:

    $BUNDLE_DIR/$BINARY

brew install corca-ai/tap/crill followed by crill --version walks through the
same gate.

Then log in to the access gate with your invitation key:

    crill auth login <your-email>

See https://github.com/corca-ai/crill-cli#for-internal-trial-operators
for the full first-run walkthrough.
EOF
