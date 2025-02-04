{
  description = "Script for connecting to PulseVPN using openconnect and chromedriver";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  };

  outputs = { self, nixpkgs }: {
    packages.x86_64-linux = let
      pkgs = import "${nixpkgs}" {
        system = "x86_64-linux";
      };

    in with pkgs; {
      openconnect-pulse-launcher = callPackage ./default.nix {
        inherit builtins;
      };
    };

    defaultPackage.x86_64-linux = self.packages.x86_64-linux.openconnect-pulse-launcher;
  };
}
