import os
from zipfile import ZipFile


def install_coco():
    coco_path = f"{os.path.abspath(os.path.dirname(__file__))}/core/external"
    print(coco_path)
    os.system(
        f"""
        cd {coco_path} \
        && python setup.py build_ext --inplace \
        && rm -rf build \
        """
    )


def load_cornernet_pretrained():
    models_dir = f"{os.path.abspath(os.path.dirname(__file__))}/models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    if not os.listdir(models_dir):
        os.system(
            f"cd {models_dir} \
            && gdown 11VIda1EEUG9FkDUVVSRYqg0LADeKmCL8"
        )
        with ZipFile(f"{models_dir}/fashion_trained.zip", "r") as zip_ref:
            zip_ref.extractall(models_dir)
        os.remove(f"{models_dir}/fashion_trained.zip")
