{ lib, makeWrapper, pkgs, ... }:
let
  openconnect-patched = pkgs.openconnect.overrideAttrs (old: {
    patches = (old.patches or [ ]) ++ [
      ./patched/pulse.patch
    ];
  });
  runtime-paths = with pkgs; lib.makeBinPath [
    chromedriver
    chromium
    gawk
    inetutils
    nettools
    openconnect-patched
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
      netifaces
      psutil
      pycookiecheat
      selenium
      xdg-base-dirs
    ]))
  ];

  installPhase = ''
    install -Dm755 ${./openconnect-pulse-launcher.py} $out/bin/openconnect-pulse-launcher

    wrapProgram $out/bin/openconnect-pulse-launcher \
      --prefix PATH : ${runtime-paths}
  '';
}
