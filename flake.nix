{
  description = "";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        python = pkgs.python312;

        pythonEnv = python.withPackages (ps: with ps; [
          pygame
          ffmpeg-python
          dbus-next
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pythonEnv
          ];

          shellHook = ''
            echo "Python development environment"
            python --version
          '';
        };
      });
}

