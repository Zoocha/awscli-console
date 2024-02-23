{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
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
    packages = forAllSystems ({pkgs, ...}: rec {
      default = pkgs.python3Packages.buildPythonPackage {
        pname = "aws-console";
        version = self.lastModifiedDate;
        pyproject = true;
        src = ./.;
        nativeBuildInputs = with pkgs.python3Packages; [setuptools];
        propagatedBuildInputs = with pkgs.python3Packages; [requests boto3];
        doCheck = false;
      };
      # AWS CLI requires the full site-packages, but nix adds dependencies by
      # patching, so build an env with them
      plugin-env = pkgs.python3.withPackages (_: [default] ++ default.propagatedBuildInputs);
    });
    formatter = forAllSystems ({pkgs, ...}: pkgs.alejandra);
    hydraJobs = packages;
  };
}
