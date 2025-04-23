{ lib, makeWrapper, pkgs, ... }:
let
  runtime-paths = with pkgs; lib.makeBinPath [
    chromedriver
    chromium
    gawk
    inetutils
    nettools
    openconnect
    procps
  ];
in
pkgs.stdenv.mkDerivation {
  name = "openconnect-pulse-launcher";

  dontUnpack = true;

  nativeBuildInputs = [
    makeWrapper
  ];

  propagatedBuildInputs = with pkgs; [
    # Python dependencies
    (pkgs.python3.withPackages (pythonPackages: with pythonPackages; [
      selenium
      psutil
      xdg-base-dirs
    ]))
  ];

  installPhase = ''
    install -Dm755 ${./openconnect-pulse-launcher.py} $out/bin/openconnect-pulse-launcher

    wrapProgram $out/bin/openconnect-pulse-launcher \
      --prefix PATH : ${runtime-paths}
  '';
}
