# shell.nix
# Note: This only covers running the web API, not the PyQt GUI.
let
  # We pin to a specific nixpkgs commit for reproducibility.
  # Last updated: 2025-01-03. Check for new commits at https://status.nixos.org.
  pkgs = import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/d6973081434f88088e5321f83ebafe9a1167c367.tar.gz") { };
in
pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs: with python-pkgs; [
      # select Python packages here
			pynmeagps
			paho-mqtt_2
      pyjson5
			dataclass-wizard
			flask
			gunicorn
      h3
    ]))
  ];
}