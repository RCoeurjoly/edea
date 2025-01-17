{
  description = "Application packaged using poetry2nix";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    # In nixos-unstable-small, kicad is broken
    # https://github.com/NixOS/nixpkgs/issues/327181
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    poetry2nix = {
      # url = "git+file:///home/roland/poetry2nix";
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication defaultPoetryOverrides;
        
      customOverrides = self: super: {
        # Overrides go here
        pyright = super.pyright.overridePythonAttrs (
          old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ self.setuptools ];
          }
        );

        pytest-only = super.pytest-only.overridePythonAttrs (
          old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ self.poetry ];
          }
        );
        
        datamodel-code-generator = super.datamodel-code-generator.overridePythonAttrs (
          old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ self.poetry ];
          }
        );
        
        sphinxawesome-theme = super.sphinxawesome-theme.overridePythonAttrs (
          old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ self.poetry ];
          }
        );

        sphinxcontrib-asciinema = super.sphinxcontrib-asciinema.overridePythonAttrs (
          old: {
            buildInputs = (old.buildInputs or [ ]) ++ [ self.setuptools ];
          }
        );

      };
      in
        {
          
        packages = {
          edea = mkPoetryApplication {
            projectDir = self;
            overrides =
              [
                defaultPoetryOverrides
                customOverrides
              ];
             propagatedBuildInputs = [ pkgs.kicad-small ]; 
          };
          default = self.packages.${system}.edea;
        };

        # Shell for app dependencies.
        #
        #     nix develop
        #
        # Use this shell for developing your app.
        devShells.default = pkgs.mkShell {
          inputsFrom = [ self.packages.${system}.myapp ];
        };

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
      });
}
