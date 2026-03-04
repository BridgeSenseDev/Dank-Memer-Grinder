{
  inputs = {
    flake-schemas.url = "https://flakehub.com/f/DeterminateSystems/flake-schemas/*";
    nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1.*";
  };
  outputs =
    {
      self,
      flake-schemas,
      nixpkgs,
    }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forEachSupportedSystem =
        f:
        nixpkgs.lib.genAttrs supportedSystems (
          system:
          f {
            pkgs = import nixpkgs { inherit system; };
          }
        );
    in
    {
      schemas = flake-schemas.schemas;
      devShells = forEachSupportedSystem (
        { pkgs }:
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              gcc
              pkg-config
              go_1_26
              git
              bun

              gtk3
              gtk4
              webkitgtk_4_1
              webkitgtk_6_0
            ];
            shellHook = ''
              export PATH="$PATH:$(go env GOPATH)/bin"
            '';
          };
        }
      );
    };
}
