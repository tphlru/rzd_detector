from PIL import Image, ImageOps
import sys
def cur_resize_image(input_img_path, output_path, h=640, w=640):
    image = Image.open(input_img_path)

    width, height = image.size
    scale = min(w / width, h / height)
    resized_image = image.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)
    new_size = resized_image.size
    delta_w = w - new_size[0]
    delta_h = h - new_size[1]
    border = (delta_w // 2, delta_h // 2, delta_w - delta_w // 2, delta_h - delta_h // 2)
    ImageOps.expand(resized_image, border=border, fill="black").save(output_path)
    return (height, width, new_size[0], new_size[1])


def cur_resize_segmentation(h: int, l: int, normalized_y: int, normalized_x: int,  seg: list, normalized_size: int):
    normalized_seg = copy_shape(seg)
    for i in range(0, len(seg)):
        for x in range(0, len(seg[i]), 2):
            cur_x = seg[i][x]*(normalized_x/l)
            if l < h:
                cur_x += (normalized_y - normalized_x)/2
                if cur_x < 0:
                    input()
            cur_x /= normalized_size
            normalized_seg[i][x] = cur_x
        for y in range(1, len(seg[i]), 2):
            cur_y = (normalized_y*seg[i][y])/h
            if l > h:
                cur_y += (normalized_x - normalized_y)/2
                if cur_y < 0:
                    input()
            cur_y /= normalized_size
            normalized_seg[i][y] = cur_y
    return normalized_seg


def copy_shape(l: list):
    nl = []
    for x in range(len(l)):
        nl.append([0]*len(l[x]))
    return nl
