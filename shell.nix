{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.git
    pkgs.ffmpeg
    pkgs.gpac
    pkgs.go
    pkgs.wget
    pkgs.bento4
    pkgs.cmake
    pkgs.unzip
    (pkgs.python3.withPackages (ps: [
      ps.flask
      ps.pyyaml
    ]))
  ];
  
  shellHook = ''
    export GEMINI_WRAPPED=1
  '';
}
