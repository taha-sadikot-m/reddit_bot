{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.nodejs_18
    pkgs.nodePackages.npm
    pkgs.ffmpeg
    pkgs.libxext
    pkgs.libx11
  ];
}
