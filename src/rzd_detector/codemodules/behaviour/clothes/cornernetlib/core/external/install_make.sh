#!/bin/bash

# Function to check if make is already installed
check_make() {
    if command -v make &> /dev/null; then
        echo "make is already installed:"
        make --version
        exit 0
    fi
}

install_make_linux() {
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y make gcc
    elif command -v yum &> /dev/null; then
        sudo yum install -y make
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y make gcc
    elif command -v zypper &> /dev/null; then
        sudo zypper install -y make
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm make
    else
        echo "Unsupported package manager. Please install 'make' manually."
        exit 1
    fi
}

install_chocolatey() {
    echo "Chocolatey not found. Installing Chocolatey..."
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
    if [ $? -eq 0 ]; then
        echo "Chocolatey installed successfully."
        # Refresh environment variables
        eval "$(/c/ProgramData/chocolatey/bin/refreshenv.cmd)"
    else
        echo "Failed to install Chocolatey. Please install it manually."
        exit 1
    fi
}

install_make_windows() {
    if command -v winget &> /dev/null; then
        echo "Using winget to install make..."
        winget install GnuWin32.Make
    elif command -v choco &> /dev/null; then
        echo "Using Chocolatey to install make..."
        choco install make
    elif command -v scoop &> /dev/null; then
        echo "Using Scoop to install make..."
        scoop install make
    else
        echo "No supported package manager found. Attempting to install Chocolatey..."
        install_chocolatey
        if command -v choco &> /dev/null; then
            echo "Using newly installed Chocolatey to install make..."
            choco install make
        else
            echo "Failed to install a package manager. Please install 'make' manually."
            exit 1
        fi
    fi
}

# Check if make is already installed
check_make

# Detect the operating system
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    install_make_linux
elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* || "$OSTYPE" == "win32" ]]; then
    install_make_windows
else
    echo "Unsupported operating system: $OSTYPE"
    exit 1
fi

# Check if make was successfully installed
if command -v make &> /dev/null; then
    echo "make has been successfully installed."
    make --version
else
    echo "Failed to install make. Please try installing it manually."
    exit 1
fi
