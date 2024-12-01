{ pkgs ? import <nixpkgs> { } }:
with pkgs;
stdenvNoCC.mkDerivation {
  name = "dev-shell";
  buildInputs = [ uv black pyright libxml2 libxslt ];
}
