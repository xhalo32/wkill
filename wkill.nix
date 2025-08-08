{
  lib,
  pkgs,
  buildPythonApplication,
  python,
  makeWrapper,
  i3ipc,
  setuptools,
}:

buildPythonApplication {
  pname = "wkill";
  version = "0.1.0";

  src = ./.;

  propagatedBuildInputs = [
    i3ipc
  ];

  build-system = [ setuptools ];

  nativeBuildInputs = [ makeWrapper ];

  pyproject = true;

  pythonImportsCheck = "wkill";

  preFixup = ''
    wrapProgram $out/bin/wkill --prefix PATH : "${pkgs.slurp}/bin"
  '';

  meta = with lib; {
    description = "Sway kill window";
    homepage = "https://github.com/xhalo32/wkill";
    license = licenses.mit;
  };
}
