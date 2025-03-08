import argparse
import os

import numpy as np
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from PIL import Image


def get_min_white_border(image_files, mode):
    min_left, min_right = float('inf'), float('inf')
    min_top, min_bottom = float('inf'), float('inf')

    for file in image_files:
        img = Image.open(file).convert("RGB")
        img_array = np.array(img)
        non_white = np.any(img_array != [255, 255, 255], axis=-1)

        if mode == "horizontal":
            # 计算水平方向的白边
            cols = np.any(non_white, axis=0)
            width = cols.size

            if np.any(cols):
                left = np.argmax(cols)  # 左边白边宽度
                right = np.argmax(cols[::-1])  # 右边白边宽度
            else:
                left, right = width, width  # 全白图片

            min_left = min(min_left, left)
            min_right = min(min_right, right)

        elif mode == "vertical":
            # 计算垂直方向的白边
            rows = np.any(non_white, axis=1)
            height = rows.size

            if np.any(rows):
                top = np.argmax(rows)  # 顶部白边宽度
                bottom = np.argmax(rows[::-1])  # 底部白边宽度
            else:
                top, bottom = height, height  # 全白图片

            min_top = min(min_top, top)
            min_bottom = min(min_bottom, bottom)

        else:
            raise ValueError("Mode must be 'horizontal' or 'vertical'")

    # 返回结果
    if mode == "horizontal":
        return min_left, min_right, 0, 0
    elif mode == "vertical":
        return 0, 0, min_top, min_bottom


def crop_images(input_folder, output_folder, mode):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder)
                   if f.lower().endswith(('png', 'jpg', 'jpeg'))]

    if not image_files:
        print("未找到图片文件")
        return

    min_left, min_right, min_top, min_bottom = get_min_white_border(image_files, mode)
    print(f"L {min_left}, R {min_right}, T {min_top}, B {min_bottom}")
    min_left_right, min_top_bottom = 0, 0

    if mode == "horizontal":
        min_left_right = inquirer.number(
            message="横向裁剪:",
            float_allowed=True,
            default=max(min_left, min_right)
        ).execute()
        min_left_right = float(min_left_right)
    elif mode == "vertical":
        min_top_bottom = inquirer.number(
            message="纵向裁剪:",
            float_allowed=True,
            default=max(min_top, min_bottom)
        ).execute()
        min_top_bottom = float(min_top_bottom)

    for file in image_files:
        img = Image.open(file)
        width, height = img.size
        cropped = img.crop((min_left_right, min_top_bottom, width - min_left_right, height - min_top_bottom))
        output_path = os.path.join(output_folder, os.path.basename(file) + ".webp")
        cropped.save(output_path, "WEBP", quality=90)

    print(f"所有图片已裁剪并保存到 {output_folder}")


def main():
    try:
        parser = argparse.ArgumentParser(description="裁剪图片的白边")
        _ = parser.parse_args()

        mode = inquirer.select(
            message="裁剪方向:",
            choices=[
                Choice(value="horizontal", name="horizontal (左右)"),
                Choice(value="vertical", name="vertical (上下)"),
            ],
            default="vertical",
        ).execute()

        cwd = os.getcwd()  # 当前文件夹
        output = os.path.join(cwd, "output")
        crop_images(cwd, output, mode)
    except KeyboardInterrupt:
        print("Exiting……")


if __name__ == "__main__":
    main()
