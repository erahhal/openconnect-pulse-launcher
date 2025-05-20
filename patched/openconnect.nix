{ ... }:
{
  nixpkgs = {
    config = {
      packageOverrides = pkgs: {
        openconnect = pkgs.openconnect.overrideAttrs (o: {
          patches = (o.patches or [ ]) ++ [
            ./pulse.patch
          ];
        });
      };
    };
  };
}
