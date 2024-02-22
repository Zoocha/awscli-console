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
    packages = forAllSystems ({pkgs, ...}: let
      inherit (pkgs.python3Packages) buildPythonApplication setuptools requests boto3;
    in {
      default = buildPythonApplication {
        pname = "aws-console";
        version = self.lastModifiedDate;
        pyproject = true;
        src = ./.;
        nativeBuildInputs = [setuptools];
        propagatedBuildInputs = [requests boto3];
      };
    });
    formatter = forAllSystems ({pkgs, ...}: pkgs.alejandra);
    hydraJobs = packages;
  };
}
