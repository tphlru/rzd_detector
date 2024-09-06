# CornerNet-Lite project - https://github.com/princeton-vl/CornerNet-Lite
# DeepFashoin2 Dataset - https://github.com/switchablenorms/DeepFashion2
import os
import cv2
from .cornernetlib.core.vis_utils import draw_bboxes
from .cornernetlib.core.detectors import CornerNet_Saccade

class_list = [
    "long_sleeve_dress",
    "long_sleeve_outwear",
    "long_sleeve_top",
    "short_sleeve_dress",
    "short_sleeve_outwear",
    "short_sleeve_top",
    "shorts",
    "skirt",
    "sling",
    "sling_dress",
    "trousers",
    "vest",
    "vest_dress",
]


def get_clothes(
    source_img,
    thresh: float = 0.5,
    show=True,
    fname=False,
):
    if source_img is None:
        ValueError("Image is empty!")
    base_path = os.path.abspath(os.path.dirname(__file__))
    model_path = os.path.join(
        base_path,
        "cornernetlib",
        "models",
        "cache",
        "nnet",
        "CornerNet_Saccade",
        "CornerNet_Saccade_best.pkl",
    )
    detector = CornerNet_Saccade(
        test=True, class_list=class_list, model_path=model_path
    )
    raw_result = detector(source_img)

    featured_categories = []
    for cat in raw_result:
        keep_index = raw_result[cat][:, -1] > thresh
        if len(raw_result[cat][keep_index]) == 0:
            continue
        featured_categories.append(cat)

    out_image = draw_bboxes(source_img, raw_result, thresh=thresh)
    if fname:
        cv2.imwrite(fname, out_image)
    if show:
        cv2.imshow("", out_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return featured_categories


# TODO: Add log and docstring
