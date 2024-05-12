{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/refs/tags/23.05.tar.gz") {} }:

let 
  my-python = pkgs.python3;
  # jinja2 is required to build Coyote. 
  python-with-my-packages = my-python.withPackages (p: with p; 
  [
    jinja2
    seaborn
  ]);
in
pkgs.mkShell {
  name = "my-packages";
  runScript = "bash";

  buildInputs = with pkgs; [
    coreutils
    git 
    boost
    pahole

    cmake
    nasm
    binutils
    openssl
    zlib
    docker
    docker-compose
    kubectl
    # linux.dev
    usbutils
    pciutils
    curl
    fmt_9
    gzip
    scc
    gnumeric

    # python packages
    python3
#    python311Packages.seaborn
    python-with-my-packages
    
  ];  
  shellHook = ''
    PYTHONPATH=${python-with-my-packages}/${python-with-my-packages.sitePackages}
    # the other env-vars
  '';
}

