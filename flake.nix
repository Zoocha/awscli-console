{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    systems.url = "github:nix-systems/default";
  };

  outputs = {
    self,
    systems,
    nixpkgs,
  }: let
    forAllSystems = f:
      nixpkgs.lib.genAttrs (import systems) (system:
        f {
          inherit system;
          pkgs = nixpkgs.legacyPackages.${system};
        });
  in rec {
    packages = forAllSystems ({pkgs, ...}: {
      default = pkgs.callPackage ./. {
        version = self.lastModifiedDate;
      };
    });
    formatter = forAllSystems ({pkgs, ...}: pkgs.alejandra);
    hydraJobs = packages;
  };
}
