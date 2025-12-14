{ lib, makeWrapper, pkgs, ... }:
let
  openconnect-updated = pkgs.openconnect.overrideAttrs (old: {
    src = pkgs.fetchgit {
      url = "https://gitlab.com/openconnect/openconnect.git";
      rev = "0dcdff87db65daf692dc323732831391d595d98d";
      sha256 = "sha256-AvowUEDkXvR+QkhJbZU759fZjIqj/mO8HjP2Ka3lH1U=";
    };
  });

  # Package selenium-stealth
  selenium-stealth = pkgs.python3.pkgs.buildPythonPackage rec {
    pname = "selenium-stealth";
    version = "1.0.6";
    format = "wheel";

    src = pkgs.fetchurl {
      url = "https://files.pythonhosted.org/packages/cb/ac/7877df8b819d54a4e317a093a0a9e0a38d21d884a7250aa713f2f0869442/selenium_stealth-1.0.6-py3-none-any.whl";
      hash = "sha256-ti2lRSqkqE8ppN+yGpaWr/IHiKfFcN0LgbwEqUCEi5c=";
    };

    propagatedBuildInputs = with pkgs.python3.pkgs; [
      selenium
      setuptools
    ];

    doCheck = false; # Skip tests for simplicity
  };

  runtime-paths = with pkgs; lib.makeBinPath [
    chromedriver
    chromium
    gawk
    inetutils
    nettools
    openconnect-updated
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
      selenium
      selenium-stealth
      xdg-base-dirs
    ]))
  ];

  installPhase = ''
    install -Dm755 ${./openconnect-pulse-launcher.py} $out/bin/openconnect-pulse-launcher

    wrapProgram $out/bin/openconnect-pulse-launcher \
      --prefix PATH : ${runtime-paths}
  '';
}
