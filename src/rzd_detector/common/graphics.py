from matplotlib import pyplot as plt
from matplotlib.patches import Circle, Wedge, Rectangle
import numpy as np


def degree_range(n):
    start = np.linspace(0, 180, n + 1, endpoint=True)[:-1]
    end = np.linspace(0, 180, n + 1, endpoint=True)[1::]
    mid_points = start + ((end - start) / 2.0)
    return np.c_[start, end], mid_points


def gauge_chart(
    arrow,
    labels=["TOO BAD", "BAD", "NORMAL", "OK", "SUPER"],
    colors=["red", "LightCoral", "LightSkyBlue", "LightGreen", "ForestGreen"],
    title="",
    show=True,
    fname=False,
):  # sourcery skip: default-mutable-arg
    """Создает гейдж-индукатор с заданными метками и цветами.
    Гейдж-индукатор представляет собой 180-градусную круговую диаграмму с цветными делениями и стрелкой.

    Args:
        arrow (int): Индекс положения стрелки на индикаторе.
        labels (list of str, опционально): Названия меток для зон индикатора. Требуется ровно 5 значений.
            По умолчанию ["TOO BAD", "BAD", "NORMAL", "OK", "SUPER"].
        colors (list of str, опционально): Цвета для для зон индикатора. Требуется ровно 5 значений.
            По умолчанию ["red", "LightCoral", "LightSkyBlue", "LightGreen", "ForestGreen"].
        title (str, опционально): Заголовок диаграммы-индикатора. По умолчанию None.
        fname (str or bool, опционально): Имя файла для сохранения диаграммы. По умолчанию False.

    Returns:
        None
    """

    if len(labels) != 5:
        raise ValueError("Exactly 5 labels are required.")
    if len(colors) != 5:
        raise ValueError("Exactly 5 colors are required.")

    N = len(labels)
    fig, ax = plt.subplots(figsize=(4, 2))
    fig.subplots_adjust(0, 0, 1, 1)
    ang_range, mid_points = degree_range(N)
    patches = []

    for ang, c in zip(ang_range, colors):
        patches.extend(
            (
                Wedge((0.0, 0.0), 0.4, *ang, facecolor="w", lw=2),
                Wedge((0.0, 0.0), 0.4, *ang, width=0.2, facecolor=c, lw=2, alpha=0.5),
            )
        )

    for p in patches:
        ax.add_patch(p)

    for mid, lab in zip(mid_points, labels):
        radians_mid = np.radians(mid)
        ax.text(
            0.42 * np.cos(radians_mid),
            0.42 * np.sin(radians_mid),
            lab,
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=14,
            fontweight="bold",
            rotation=np.degrees(radians_mid) - 90,
        )

    r = Rectangle((-0.4, -0.1), 0.8, 0.1, facecolor="w", lw=2)
    ax.add_patch(r)
    ax.text(
        0,
        -0.1,
        title,
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=18,
    )

    pos = mid_points[abs(arrow - N)]
    radians_pos = np.radians(pos)
    ax.arrow(
        0,
        0,
        0.225 * np.cos(radians_pos),
        0.225 * np.sin(radians_pos),
        width=0.04,
        head_width=0.09,
        head_length=0.1,
        fc="k",
        ec="k",
    )
    ax.add_patch(Circle((0, 0), radius=0.02, facecolor="k"))
    ax.add_patch(Circle((0, 0), radius=0.01, facecolor="w", zorder=11))
    ax.set_frame_on(False)
    ax.axes.set_xticks([])
    ax.axes.set_yticks([])
    ax.axis("equal")

    if fname:
        plt.savefig(fname, bbox_inches="tight")
    if show:
        plt.show(block=False)
