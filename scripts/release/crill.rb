# typed: false
# frozen_string_literal: true

# This file is rendered by scripts/release/publish_release.py in the
# corca-ai/crill-cli repo. Do not edit the tap copy directly; edit the
# public-repo template in corca-ai/crill and cut a new release tag.
class Crill < Formula
  desc "Mobile app UX exploration and competitive change detection CLI"
  homepage "https://github.com/corca-ai/crill-cli"
  version "__VERSION__"
  depends_on arch: :arm64

  on_macos do
    url "https://github.com/corca-ai/crill-cli/releases/download/v__VERSION__/crill___VERSION___darwin_arm64.tar.gz"
    sha256 "__ARM64_SHA__"

    def install
      bin.install "crill"
    end
  end

  test do
    system bin/"crill", "--version"
  end
end
