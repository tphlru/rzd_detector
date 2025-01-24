import cv2
import numpy as np


def cur_resize_image(input_img_path: str, output_img_path: str, needed_size: int):
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


def cur_resize_segmentation(h: int, l: int, normalized_y: int, normalized_x: int,  seg: list):
    normalized_seg = copy_shape(seg)
    for i in range(0, len(seg)):
        for x in range(0, len(seg[i]), 2):
            cur_x = (normalized_x*seg[i][x])/l
            normalized_seg[i][x] = cur_x
        for y in range(0, len(seg[i]), 2):
            cur_y = (normalized_y*seg[i][y])/h + (normalized_x - normalized_y)/2
            normalized_seg[i][y] = cur_y
    return normalized_seg


def copy_shape(l: list):
    nl = []
    for x in range(len(l)):
        nl.append([0]*len(l[x]))
    return nl
