Openconnect Pulse Launcher
==========================

## Usage

`./openconnect-pulse-launcher.py <hostname>`

## Installation

This python script should work on any distro with the following binaries installed:

```
awk
ifconfig
openconnect
pkill
route
```

## Nix

It can also be used on Nix using the included flake.nix file.

Add the following to the `inputs` section of your flake.nix:

```
    openconnect-pulse-launcher.url = "github:erahhal/openconnect-pulse-launcher";
```

And add the following package somewhere in your config:

```
    inputs.openconnect-pulse-launcher.packages."${pkgs.system}".openconnect-pulse-launcher
```
