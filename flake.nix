{
  description = "Application packaged using poetry2nix";

  nixConfig = {
    extra-substituters = [ "https://edea-test-cachix.cachix.org" ];
    extra-trusted-public-keys = [
      "edea-test-cachix.cachix.org-1:4cGBfU4APGmQPPMpyRZdr9g9wQiMGRcBr1hmFqG/wDw="
    ];
  };

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";

    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    # In nixos-unstable-small, kicad is broken
    # https://github.com/NixOS/nixpkgs/issues/327181
    nixpkgs-stable.url = "github:NixOS/nixpkgs/nixos-24.05";

    poetry2nix = {
      # url = "git+file:///home/roland/poetry2nix";
      url = "github:nix-community/poetry2nix";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      poetry2nix,
      nixpkgs-stable,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        pkgs = nixpkgs.legacyPackages.${system};
        kicad-small = nixpkgs-stable.legacyPackages.${system}.kicad-small;
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication defaultPoetryOverrides;

        customOverrides = self: super: {
          # Overrides go here
          pyright = super.pyright.overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ self.setuptools ];
          });

          pytest-only = super.pytest-only.overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ self.poetry ];
          });

          datamodel-code-generator = super.datamodel-code-generator.overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ self.poetry ];
          });

          sphinxawesome-theme = super.sphinxawesome-theme.overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ self.poetry ];
          });

          sphinxcontrib-asciinema = super.sphinxcontrib-asciinema.overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ self.setuptools ];
          });

          docstring-parser-fork = super.docstring-parser-fork.overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ self.poetry ];
          });

          docutils = super.docutils.overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ self.flit-core ];
          });

          pydoclint = super.pydoclint.overridePythonAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ self.setuptools ];
          });

        };
      in
      {

        packages = {
          edea = mkPoetryApplication {
            projectDir = self;
            preferWheels = true;
            overrides = [
              defaultPoetryOverrides
              customOverrides
            ];
            propagatedBuildInputs = [ kicad-small ];
          };
          default = self.packages.${system}.edea;
        };

        # Shell for app dependencies.
        #
        #     nix develop
        #
        # Use this shell for developing your app.
        devShells.default = pkgs.mkShell { inputsFrom = [ self.packages.${system}.myapp ]; };

        # Shell for poetry.
        #
        #     nix develop .#poetry
        #
        # Use this shell for changes to pyproject.toml and poetry.lock.
        devShells.poetry = pkgs.mkShell {
          packages = [
            pkgs.poetry
            pkgs.kicad-small
          ];
        };
      }
    );
}
