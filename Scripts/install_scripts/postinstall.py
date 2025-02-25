import os
from rzd_detector.codemodules.behaviour.clothes.cornernetlib.loadinstall import (
    install_coco,
    load_cornernet_pretrained,
)


def install_cpools():
    os.system("pip install git+https://github.com/tphlru/cpools.git")


def install_pycocotools():
    command = """
    rm -rf cocoapi &&
    git clone https://github.com/abhi-kumar/cocoapi.git &&
    cd cocoapi/PythonAPI &&
    make install &&
    cd ../.. &&
    rm -rf cocoapi
    """
    os.system(command)


def run_postinstall():
    print("Post-installation script")
    install_cpools()
    install_coco()
    install_pycocotools()
    load_cornernet_pretrained()
    print("Installation finished!")


if __name__ == "__main__":
    run_postinstall()
