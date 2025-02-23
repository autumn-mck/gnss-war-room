# shell.nix
# Note: This only covers running the web API, not the PyQt GUI.
let
  # We pin to a specific nixpkgs commit for reproducibility.
  # Last updated: 2025-02-14. Check for new commits at https://status.nixos.org.
  pkgs =
    import
      (fetchTarball "https://github.com/NixOS/nixpkgs/archive/1128e89fd5e11bb25aedbfc287733c6502202ea9.tar.gz")
      { };
in
pkgs.mkShell {
  packages = with pkgs; [
    bun

    (python3.withPackages (
      python-pkgs: with python-pkgs; [
        pynmeagps
        paho-mqtt_2
        pyjson5
        dataclass-wizard
        flask
        gunicorn
        h3
        python-dotenv
      ]
    ))
  ];
}
