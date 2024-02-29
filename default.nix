{ lib, python3Packages, python3, version ? "0.1", ... }:
python3Packages.buildPythonApplication {
  pname = "aws-console";
  inherit version;

  src = ./.;
  pyproject = true;

  nativeBuildInputs = with python3Packages; [setuptools];
  propagatedBuildInputs = with python3Packages; [requests boto3];
  doCheck = false;
}
