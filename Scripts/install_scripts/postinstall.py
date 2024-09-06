from rzd_detector.codemodules.behaviour.clothes.cornernetlib.loadinstall import (
    install_coco,
    load_cornernet_pretrained,
)


def run_postinstall():
    print("Post-installation script")
    install_coco()
    load_cornernet_pretrained()
    print("Installation finished!")


if __name__ == "__main__":
    run_postinstall()
