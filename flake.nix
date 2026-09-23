{
  description = "";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    pyproject-nix = {
      url = "github:nix-community/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils,pyproject-nix, ... }:
      let
        system = "x86_64-linux";
        pkgs = import nixpkgs {
          inherit system;
        };

        python = pkgs.python312;

        pythonEnv = python.withPackages (ps: with ps; [
          pygame
          ffmpeg-python
          dbus-next
        ]);

      project = pyproject-nix.lib.project.loadPyproject {
        # Read & unmarshal pyproject.toml relative to this project root.
        # projectRoot is also used to set `src` for renderers such as buildPythonPackage.
        projectRoot = ./.;
      };
      in
      {
    packages.${system}.default =
        let
          # Returns an attribute set that can be passed to `buildPythonPackage`.
          attrs = project.renderers.buildPythonPackage { inherit python; };
        in
        # Pass attributes to buildPythonPackage.
        # Here is a good spot to add on any missing or custom attributes.
        python.pkgs.buildPythonPackage (attrs // {
          env.CUSTOM_ENVVAR = "hello";
        });
        devShells.default = pkgs.mkShell {
          packages = [
            pythonEnv
          ];

          shellHook = ''
            echo "Python development environment"
            python --version
          '';
        };

      };

}

