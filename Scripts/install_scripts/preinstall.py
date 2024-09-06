import os


# Add pre-installation actions here:
def run_preinstall():
    print("Pre-installation script")
    os.system("python -m pip install cython")


if __name__ == "__main__":
    run_preinstall()
