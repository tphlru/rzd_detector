import os
import shutil

import git


def clone_and_extract(
    repo_url: str,
    target_dir: str,
    extract_dir: str,
    branch: str = "main",
):
    """Функция, чтобы скачать репозиторий и вытащить из него конкретную директторию

    Args:
        repo_url (str): Ссылка в формате https://github.com/user/repo.git
        branch (str): Ветка репозитория, по умолчанию main
        target_dir (str): В какую локальную директорию извлечь цель
        extract_dir (str): Путь в репозитории, который надо извлечь

    Raises:
        ValueError: Если нет такой директории в репозитории
    """
    # Клонируем репозиторий в временную директорию
    temp_dir = "temp_repo"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    git.Repo.clone_from(repo_url, temp_dir, branch=branch, depth=1)
    src_dir = os.path.join(temp_dir, extract_dir)
    if not os.path.isdir(src_dir):
        raise ValueError(f"Directory {src_dir} does not exist in the repository.")
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)  # Удаляем целевую директорию, если она существует
    shutil.copytree(src_dir, target_dir)
    shutil.rmtree(temp_dir)


def run_postinstall():
    print("Post-installation script")

    coco_repo_url = "https://github.com/tphlru/cornernet.git"
    clone_and_extract(coco_repo_url, "coco", "core/external")
    os.system("cd coco && python setup.py build_ext --inplace && rm -rf build")
    shutil.rmtree("coco")

    print("Installation finished!")


if __name__ == "__main__":
    run_postinstall()
