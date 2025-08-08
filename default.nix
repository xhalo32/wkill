{
  sources ? import ./npins,
  system ? builtins.currentSystem,
  pkgs ? import sources.nixpkgs {
    inherit system;
    config = { };
  },
}:
rec {
  packages.wkill = pkgs.python3.pkgs.callPackage ./wkill.nix { };
  default = packages.wkill;

  shell = pkgs.mkShellNoCC {
    buildInputs = [ pkgs.uv ];
    inputsFrom = [ packages.wkill ];
  };
}
