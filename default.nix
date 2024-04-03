{ lib, python3Packages, python3, version ? "0.1", ... }:
python3Packages.buildPythonApplication rec {
  pname = "aws-console";
  inherit version;

  src = ./.;
  pyproject = true;

  nativeBuildInputs = with python3Packages; [setuptools];
  propagatedBuildInputs = with python3Packages; [requests botocore];
  doCheck = false;

  pluginEnv = python3.withPackages (_: propagatedBuildInputs);
  postInstall = ''
    mkdir -p $out/share/aws_plugin_path
    ln -st $out/share/aws_plugin_path/ {$out,$pluginEnv}/lib/python${python3.pythonVersion}/site-packages/*
  '';
}
