import numpy as np
from typing import TypeVar, Iterable, Union

T = TypeVar("T", bound=Iterable)


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
    assert len(dividing_line) == len(seq)

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
