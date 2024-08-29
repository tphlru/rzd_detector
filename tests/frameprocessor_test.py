from rzd_detector.codemodules.face.iteratevideo.frameprocessor import FrameProcessor
import inspect
import pytest


# Helper functions for testing
def dummy_func(item, previous_result=None):
    if previous_result is not None and not isinstance(previous_result, list):
        return item + previous_result  # Use previous result if available
    return item * 2  # Default case: return item multiplied by 2


def dummy_func_no_params(item):
    return item * 3


def dummy_callable(results):
    return sum(results)


@pytest.fixture
def frame_processor():
    return FrameProcessor()


@pytest.mark.parametrize(
    "func, save_all_results, do_every_n, pass_mode, items, expected_results",
    [
        # Happy path tests
        (
            dummy_func,
            True,
            1,
            "last_result",
            [1, 2, 3],
            {"dummy_func": [2, 4, 7]},
        ),  # 1*2=2, 2+2=4, 4+3=7
        (
            dummy_func,
            False,
            1,
            "last_result",
            [1, 2, 3],
            {"dummy_func": 7},
        ),  # 1*2=2 -> 2+2=4 -> 4+3=7
        (
            dummy_func,
            True,
            2,
            "last_result",
            [1, 2, 3, 4],
            {"dummy_func": [2, 5]},
        ),  # 1*2=2, ..., 3+2=5
        (
            dummy_func_no_params,
            True,
            1,
            "nothing",
            [1, 2, 3],
            {"dummy_func_no_params": [3, 6, 9]},
        ),
        (
            dummy_func,
            True,
            1,
            dummy_callable,
            [1, 2, 3],
            {"dummy_func": [1, 3, 7]},
        ),  # 1 + sum(0) = 1, 2 + sum(0, 1) = 3, 3 + sum(0, 1, 3) = 7
        # Edge cases
        (dummy_func, True, 1, "last_result", [], {"dummy_func": []}),
        (dummy_func, True, 1, "all_results", [1], {"dummy_func": [2]}),
        (dummy_func, True, 1, "all_items", [1], {"dummy_func": [2]}),
        # Error cases
        (None, True, 1, "last_result", [1, 2, 3], ValueError),
        (dummy_func, True, 1, "invalid_mode", [1, 2, 3], ValueError),
    ],
    ids=[
        "happy_path_save_all",
        "happy_path_save_last",
        "happy_path_every_2nd",
        "happy_path_no_params",
        "happy_path_callable_mode",
        "edge_case_empty_items",
        "edge_case_single_item_all_results",
        "edge_case_single_item_all_items",
        "error_case_non_callable_func",
        "error_case_invalid_pass_mode",
    ],
)
def test_frame_processor(
    frame_processor,
    func,
    save_all_results,
    do_every_n,
    pass_mode,
    items,
    expected_results,
):

    # Act
    if isinstance(expected_results, type) and issubclass(expected_results, Exception):
        with pytest.raises(expected_results):
            frame_processor.add_function(func, save_all_results, do_every_n, pass_mode)
            frame_processor.process(items)
    else:
        frame_processor.add_function(func, save_all_results, do_every_n, pass_mode)
        results = frame_processor.process(items)

        # Assert
        assert results == expected_results


@pytest.mark.parametrize(
    "func, save_all_results, do_every_n, pass_mode, expected_exception",
    [
        (None, True, 1, "last_result", ValueError),
        (dummy_func, True, 1, "invalid_mode", ValueError),
    ],
    ids=[
        "non_callable_func",
        "invalid_pass_mode",
    ],
)
def test_add_function_errors(
    frame_processor, func, save_all_results, do_every_n, pass_mode, expected_exception
):
    # Act & Assert
    with pytest.raises(expected_exception):
        frame_processor.add_function(func, save_all_results, do_every_n, pass_mode)


def test_add_function():
    # Create an instance of the class
    frame_processor = FrameProcessor()

    # Define a test function
    def test_function(item):
        return item * 2

    # Add the test function to the list of functions
    frame_processor.add_function(test_function)

    # Check if the function was added to the list of functions
    assert test_function in frame_processor.functions
    print(f"Test passed: {inspect.currentframe().f_code.co_name}")
