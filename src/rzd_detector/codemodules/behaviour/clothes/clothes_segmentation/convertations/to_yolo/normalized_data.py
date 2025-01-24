import cv2
import numpy as np


def cur_resize_image(input_img_path: str, output_img_path: str, needed_size: int):
    img = cv2.imread(input_img_path)
    h, l, _ = img.shape
    attitude = h/l
    cur_y = int(needed_size/attitude)
    missing_y = needed_size - cur_y
    cur_img = cv2.resize(img, (needed_size, cur_y))
    black = np.zeros((int(missing_y // 2), needed_size, 3), dtype='uint8')
    cur_img = np.vstack((black, cur_img))
    cur_img = np.vstack((cur_img, black))
    cv2.imwrite(output_img_path, cur_img)
    return (h, l, cur_y)


def cur_resize_segmentation(h: int, l: int, normalized_y: int, normalized_x: int,  seg: list):
    normalized_seg = []
    for x in range(0, len(seg), 2):
        cur_x = (normalized_x*seg[x])/l
        normalized_seg[x] = cur_x
    for y in range(0, len(seg), 2):
        cur_y = (normalized_y*seg[y])/h + (normalized_x - normalized_y)/2
        normalized_seg[y] = cur_y
    return normalized_seg



cur_resize_image(r'C:\Users\Georges\Projects\Trasport\rzd_detector\tests\image.jpg', r'cur_image.jpg', 460)
