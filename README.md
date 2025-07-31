# OpenConnect Pulse Launcher

## Usage

`./openconnect-pulse-launcher.py <vpn_url>` where `<vpn_url>` is something like `https://hostname/emp`.

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

It can also be used on Nix using the included `flake.nix` file.

Add the following to the `inputs` section of your flake.nix:

```nix
    openconnect-pulse-launcher = {
      url = "github:erahhal/openconnect-pulse-launcher";
      ## Only add this if you want openconnect-pulse-launcher to use the same version of
      ## chrmomium as the one installed on your system.
      inputs.nixpkgs.follows = "nixpkgs";
    };
```

And add the following package somewhere in your config:

```nix
    inputs.openconnect-pulse-launcher.packages."${pkgs.system}".openconnect-pulse-launcher
```

## Adding a password manager (e.g. Bitwarden)

* Launch chromium manually (`--user-data-dir` must be full path, no `~/`)

```shell
    chromium --user-data-dir=/home/<username>/.config/chromedriver/pulsevpn
```

* Install the Bitwarden extension and setup
* WARNING: make sure to use "inputs.nixpkgs.follows" as shown above, or else different chromium versions could be used, corrupting the user-data-dir.
