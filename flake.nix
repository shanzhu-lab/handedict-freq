{
  description = "HanDeDict without editing history, sorted by wordfreq word frequency";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    # Updated nightly upstream; run `nix flake update handedict` to pull the latest export.
    handedict = {
      url = "github:gugray/HanDeDict";
      flake = false;
    };
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      handedict,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
    }:
    let
      inherit (nixpkgs) lib;
      forAllSystems = lib.genAttrs [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
      ];

      # Python dependencies come from uv.lock.
      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };
      overlay = workspace.mkPyprojectOverlay { sourcePreference = "wheel"; };
      pyprojectOverrides = final: prev: {
        # jieba only ships a setup.py sdist without declared build dependencies.
        jieba = prev.jieba.overrideAttrs (old: {
          nativeBuildInputs = old.nativeBuildInputs ++ final.resolveBuildSystem { setuptools = [ ]; };
        });
      };
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonSet =
            (pkgs.callPackage pyproject-nix.build.packages { python = pkgs.python3; }).overrideScope
              (
                lib.composeManyExtensions [
                  pyproject-build-systems.overlays.default
                  overlay
                  pyprojectOverrides
                ]
              );
          venv = pythonSet.mkVirtualEnv "handedict-freq-env" workspace.deps.default;
        in
        {
          default = self.packages.${system}.handedict-freq;
          handedict-freq = pkgs.runCommand "handedict-freq-${handedict.lastModifiedDate}" { } ''
            mkdir -p $out
            ${venv}/bin/python -I ${./build.py} \
              --input ${handedict}/handedict.u8 \
              --output $out/handedict-freq.u8 \
              --rev ${handedict.rev}
          '';
        }
      );
    };
}
