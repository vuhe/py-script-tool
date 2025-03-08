import glob
import io
import os
import re

from PIL import Image
from rich.progress import track
from rich.console import Console

from tool_helper.console import for_print_path

console = Console()


def check_ppcat_folder(cwd, folder_path):
    # Check if there are image files in the folder (assumes .jpg, .png, .gif, etc.)
    image_files = glob.glob(os.path.join(folder_path, '*.[jJ][pP][gG]')) + \
                  glob.glob(os.path.join(folder_path, '*.[pP][nN][gG]')) + \
                  glob.glob(os.path.join(folder_path, '*.[gG][iI][fF]'))

    # Skip the folder if it contains only 'Cover' images
    cover_images = [f for f in image_files if 'cover' in os.path.basename(f).lower()]
    if len(cover_images) == len(image_files):  # Only Cover images present
        return

    # Find index.html file in the folder
    index_html = os.path.join(folder_path, 'index.html')

    # Skip folder if no index.html is found
    if not os.path.isfile(index_html):
        console.print(f"[yellow]Missing index.html: {for_print_path(cwd, folder_path)}[/yellow]")
        return

    # Check if the folder contains images referenced in index.html
    with open(index_html, 'r') as index_file:
        html_content = index_file.read()

    # Find all image file references in the src attributes of <img> tags
    img_tags = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html_content)

    for img_tag in img_tags:
        img_name = os.path.basename(img_tag)
        img_path = os.path.join(folder_path, img_name)
        if not os.path.isfile(img_path):  # If the image file is missing
            console.print(f"[yellow]Missing {img_tag}: {for_print_path(cwd, folder_path)}[/yellow]")


def check_image_for_error(cwd, image_path):
    with open(image_path, 'rb') as image_file:
        image_data = io.BytesIO(image_file.read())
        try:
            with Image.open(image_data) as img:
                img.verify()
                # img.convert("RGB")
        except Exception as e:
            console.print(f"[red]Error image: {for_print_path(cwd, image_path)}[/red]")
            console.print(f"Error processing image: {e}")


def main():
    try:
        for root, _, files in track(os.walk(os.getcwd()), description="[blue]Check folder"):
            check_ppcat_folder(os.getcwd(), root)
            for file in track(files, description="[yellow]Check img", transient=True):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    check_image_for_error(os.getcwd(), os.path.join(root, file))
    except KeyboardInterrupt:
        print("Exiting……")


if __name__ == "__main__":
    main()
