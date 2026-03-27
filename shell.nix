{ pkgs ? import (builtins.fetchTarball {
  url = "https://github.com/NixOS/nixpkgs/archive/nixos-23.11.tar.gz";
}) {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.git
    pkgs.ffmpeg
    pkgs.gpac
    pkgs.gcc
    pkgs.glibc.dev
    pkgs.go
    pkgs.wget
    pkgs.bento4
    pkgs.cmake
    pkgs.unzip
    (pkgs.python310.withPackages (ps: [ ps.flask ps.pyyaml ]))
  ];

  shellHook = ''
    export GEMINI_WRAPPED=1
    echo "Entering Nix shell (pinned nixpkgs: nixos-23.11)"
  '';
}
