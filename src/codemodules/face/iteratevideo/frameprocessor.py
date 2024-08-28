from typing import List, Callable, Any, Dict, Union


class FrameProcessor:
    def __init__(self):
        """Инициализирует frame-processor.
        Используется для обработки видео, когда необходимо выполнять какую-то функцию к каждому кадру.
        """
        self.functions: List[Callable] = []

        # Список функций для обработки
        # Словарь для хранения результатов по каждой функции
        self.results: Dict[str, List[Any]] = {}

        # Хранение настроек по каждой функции
        # Сохранять всё / Только последний результат
        self.save_all: Dict[str, bool] = {}
        # Интервал с которым функция будет вызываться для кадра
        self.do_every_n: Dict[str, int] = {}
        # Что подавать на функцию в качестве второго параметра
        # all_results / last_result / all_items / nothing / result of callable(all_results)
        self.pass_mode: Dict[str, Union[str, Callable]] = {}

    def add_function(
        self,
        func: Callable,
        save_all_results: bool = True,
        do_every_n: int = 1,
        pass_mode: Union[str, Callable] = "last_result",
    ) -> None:
        """Добавить новую функцию для обрпботки обработчикоом видео кадров.
        Этот метод также позволяет зарегистрировать callable фунцию, которая будет вызываться для каждого кадра.

        Args:
            func (callable): Функция, которая будет вызываться для каждого кадра. Должен быть callable.
            save_all_results (bool, optional): Сохранять всё / Только результат предыдущего
                выполнения функции. По умолчанию True.
            do_every_n (int, optional): Указывает интервал с которым функция будет вызываться для кадра
                (например, вызываться для каждого 5-го кадра). По умолчанию 1.
            pass_mode (str, optional): Что передавать в функцию в качестве второго параметра.
                Допустимые значения:
                "all_results", "last_result", "all_items", "nothing", результат callable(all_results).
                Если настройка save_all_results = False, то "all_results" будет аналогичен "last_result".
                По умолчанию "last_result".

        Raises:
            ValueError: Если предоставленная функция не callable
        """
        if not callable(func):
            raise ValueError("Provided argument is not callable.")

        # Добавляем функцию в список функций
        self.functions.append(func)

        # Создаём список для хранения результатов этой функции
        self.results[func.__name__] = []

        # Настройка о сохранении всех результатов
        self.save_all[func.__name__] = save_all_results

        # Настройка о необходимости обработки функцией каждого n-го элемента
        self.do_every_n[func.__name__] = do_every_n

        # Настройка того, какие данные передвать в функцию
        possible_modes = ["all_results", "last_result", "all_items", "nothing"]
        if isinstance(pass_mode, str) and pass_mode not in possible_modes:
            raise ValueError(
                f"pass_mode must be one of the following: {possible_modes} or Callable."
            )
        self.pass_mode[func.__name__] = pass_mode

    def process(
        self, items: List[Any], last_result_only: bool = False
    ) -> Dict[str, List[Any]]:
        """Последовательно обрабатывает элементы из items (кадры),
        применяя зарегистрированные функции к каждому элементу.

        Args:
            items (List[Any]): Список элементов для обработки.
            last_result_only (bool, optional): . Defaults to False.

        Returns:
            Dict[str, List[Any]]: Словарь с результатами обработки
        """

        # Перебираем все элементы
        for count, item in enumerate(items):
            # Для каждого элемента перебираем все функции, которые нужно выполнить
            for func in self.functions:
                if count % self.do_every_n[func.__name__] == 0:
                    # Получаем список предыдущих результатов вызовов
                    previous_results = self.results[func.__name__]

                    # Выполняем функцию
                    # В зависимости от настройки передаём второй параметр
                    options = {
                        "all_results": previous_results,
                        "last_result": previous_results[-1],
                        "all_items": items,
                    }

                    mode = self.pass_mode[func.__name__]
                    if mode in options:
                        result = func(item, options[mode])
                    elif mode == "nothing":
                        result = func(item)
                    elif callable(mode):
                        result = func(item, mode(previous_results))

                    # Сохраняем результаты в зависимости от настройки
                    if self.save_all[func.__name__]:
                        self.results[func.__name__].append(result)  # Добавляем
                    else:
                        # Заменяем последним результатов
                        self.results[func.__name__] = result

        return self.results
