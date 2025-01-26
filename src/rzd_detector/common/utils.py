import numpy as np
from typing import TypeVar, Iterable, Union
import shutil
import os
import git
import cv2

T = TypeVar("T", bound=Iterable)


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


def add_offset_to_values(data: T, offset: Union[str, int, float]) -> T:
    """Очень простая функция, чтобы добаить смещение ко всем числам. Например, прибавить 10 к каждому числу.

    Args:
        data (Iterable): Исходная последовательность любых значений
        offset (Union[str, int, float]): Значение смещения, котороебудет добавлено к каждому элементу.

    Returns:
        Iterable: Последовательность со смещенными значениями
    """
    return [i + offset for i in data]


def get_trend(seq: list, negative_trend=0.5, positive_trend=1.1) -> int:
    """Получить направление тренда в последовательности чисел. Используется polyfit.

    Args:
        seq (list): последовательность чисел
        negative_trend (float, optional): Пороговое значение угла для отрицательного тренда. По умолчанию 0.5.
        positive_trend (float, optional): Пороговое значение угла для положительного тренда. По умолчанию 1.1.

    Returns:
        int: (-1) - отрицательный тренд, 1 - положительный тренд, 0 - нет тренда
    """
    # TODO: Проверить пороговые значения. Не работает с [5, 5, 5, 5, 5]
    if not seq or len(seq) < 2:
        return 0

    list_of_index = list(range(len(seq)))
    result = np.polyfit(list_of_index, seq, 1)
    slope = float(result[-2])

    if slope < negative_trend:
        return -1  # negative trend
    elif slope > positive_trend:
        return 1  # positive trend
    else:
        return 0  # no trend


def _devide_plot_tops(seq: list, dividing_line: list, win_size: int = 2) -> list:
    """Разделяет список значений по линии-разделителю.

    Args:
        seq (list): Исходная последовательность значений
        dividing_line (list): Последовательность значений линии-разделителя, длина должна совпадать с длиной seq.

    Returns:
        list: Список значений выше средней линии. Длина не определена.
    """

    return [
        [n, v]
        for n, (i, v) in enumerate(zip(range(len(dividing_line) - win_size + 2), seq))
        if v > (max(dividing_line[i : i + win_size]))
    ]


def get_midpoints(seq: list, win_size: int = 2) -> list:
    """Расчёт средних линий последовательности значений.
    Args:
        seq (list): Исходная последовательность значений
        win_size (int, optional): Размер окна. По умолчанию 2.

    Returns:
        list: Список значений средних линий
    """
    wins = [seq[i : i + win_size] for i in range(len(seq) - win_size + 1)]
    return [(f + s) / 2 for f, s in wins]


def get_plot_tops_n_times(raw_data: list, n: int):
    """Получить верхушки графика, повторяя n итераций.

    Args:
        raw_data (list): Исходная последовательность значений
        n (int): Количество итераций

    Returns:
        tuple[list, list, list]: Cписки значений средних линий, индексов верхушек, значений верхушек.
    """
    tops_values = raw_data
    for _ in range(n):
        midpoints = get_midpoints(tops_values)
        tops = _devide_plot_tops(tops_values, midpoints)
        tnums = [i[0] for i in tops]
        tops_values = [i[1] for i in tops]
    return midpoints, tnums, tops_values


def get_plot_tops_adaptive(
    raw_data: list, reqired_length: int = 50, max_iterations: int = 8
):
    """Получить верхушки графика, повторяя адаптивное количество итераций,
        пока кол-во значений не сокротится ниже reqired_length.

    Args:
        raw_data (list): Исходная последовательность значений
        reqired_length (int, optional): Требуемое количество значений (не больше чем). По умолчанию 50.
        max_iterations (int, optional): Максимальное количество итераций, если предел не соблюдён. По умолчанию 8.

    Returns:
        tuple[list, list, list]: Cписки значений средних линий, индексов верхушек, значений верхушек.
    """
    # Максимум N (8) итераций
    for iteration in range(1, max_iterations):
        mids, tnums, tvals = get_plot_tops_n_times(raw_data, iteration)

        # print("iteration no.", iteration, len(tvals))
        if len(tvals) < 50:
            break

    return mids, tnums, tvals


def cur_resize_image(input_img_path: str, output_img_path: str, needed_size: int):
    '''
    Преобразует любое изображение в квадратное изображение со стороной needed_size,
    добавляя сверху и снизу чёрные рамки для сохранения соотношения сторон исходного
    изображения.

    Args:
       input_img_path(str): путь к исходному изображению
       output_img_path(str): путь для сохранения нормализованного изображения
       needed_size(int): сторона изображениях в пикселях
    
    Returns:
        tuple[int, int, int]: высота исходного изображения, ширина исходного изображения, высота нормализованного изображения
    '''
    img = cv2.imread(input_img_path)
    cv2.imshow("lol", img)
    cv2.waitKey(0)
    h, l, _ = img.shape
    if l > h:
        attitude = h/l
        cur_y = int(needed_size/attitude)
        missing_y = needed_size - cur_y
        cur_img = cv2.resize(img, (needed_size, cur_y))
        black = np.zeros((int(missing_y // 2), needed_size, 3), dtype='uint8')
        cur_img = np.vstack((black, cur_img))
        cur_img = np.vstack((cur_img, black))
        cv2.imwrite(output_img_path, cur_img)
        cv2.imshow("lol", cur_img)
        cv2.waitKey(0)
        return (h, l, cur_y)
    else:
        attitude = l/h
        cur_x = int(needed_size*attitude)
        missing_x = needed_size - cur_x
        cur_img = cv2.resize(img, (cur_x, needed_size))
        black = np.zeros((needed_size, int(missing_x // 2), 3), dtype='uint8')
        cur_img = np.hstack((black, cur_img))
        cur_img = np.hstack((cur_img, black))
        cv2.imwrite(output_img_path, cur_img)
        cv2.imshow("lol", cur_img)
        cv2.waitKey(0)
        return (h, l, cur_x)
