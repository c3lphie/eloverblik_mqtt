{pkgs ? import <nixpkgs> {}}:
pkgs.mkShell {
  buildInputs = with pkgs; [
    # Insert packages here
   python312Packages.paho-mqtt 
   python312Packages.requests
   python312Packages.schedule
   python312Packages.pytz
  ];
}
