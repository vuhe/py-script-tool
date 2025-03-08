import io
import os
import zipfile

from PIL import Image

from tool_helper.console import for_print_path
from .converter import convert_jpeg_to_jxl, convert_jxl_to_webp, convert_png_to_webp, check_lossless_jxl


def check_zip_file(zip_path):
    changes_made = False

    with zipfile.ZipFile(zip_path, 'r') as original_zip:
        for item in original_zip.infolist():
            if changes_made:
                break
            with original_zip.open(item.filename) as original_zip_file:
                data = original_zip_file.read()

                # Check if the file is an image
                try:
                    # lossless JXL to WebP
                    # if item.filename.endswith(".jxl") and check_lossless_jxl(data):
                    #     changes_made = True
                    #     break

                    img = Image.open(io.BytesIO(data))
                    img.verify()  # Verify image integrity

                    # Correct suffix if necessary
                    if not item.filename.endswith(f".{img.format.lower()}"):
                        changes_made = True

                    # Convert PNG to WebP
                    if img.format == "PNG":
                        changes_made = True

                    # Convert JPEG to JXL
                    elif img.format == "JPEG":
                        changes_made = True

                except (IOError, OSError):
                    pass  # Not an image, write as is

    #	if not changes_made:
    #		print(f"Skip: {zip_path}")

    return changes_made


def process_zip_file(zip_path):
    print(f"Updating: {for_print_path(os.getcwd(), zip_path)}")
    temp_zip_path = zip_path + ".tmp"
    changes_made = False

    with zipfile.ZipFile(zip_path, 'r') as original_zip:
        with zipfile.ZipFile(temp_zip_path, 'w', compression=zipfile.ZIP_STORED) as new_zip:
            for item in original_zip.infolist():
                with original_zip.open(item.filename) as original_zip_file:
                    data = original_zip_file.read()
                    new_filename = item.filename

                    # Check if the file is an image
                    try:
                        # lossless JXL to WebP
                        if item.filename.endswith(".jxl") and check_lossless_jxl(data):
                            webp_data = convert_jxl_to_webp(data)
                            if webp_data:
                                new_filename = f"{os.path.splitext(new_filename)[0]}.webp"
                                new_zip.writestr(new_filename, webp_data)
                                changes_made = True
                                continue

                        img = Image.open(io.BytesIO(data))
                        img.verify()  # Verify image integrity

                        # Correct suffix if necessary
                        if not item.filename.endswith(f".{img.format.lower()}"):
                            new_filename = f"{os.path.splitext(item.filename)[0]}.{img.format.lower()}"
                            changes_made = True

                        # Convert PNG to WebP
                        if img.format == "PNG":
                            webp_data = convert_png_to_webp(data)
                            if webp_data:
                                new_filename = f"{os.path.splitext(new_filename)[0]}.webp"
                                new_zip.writestr(new_filename, webp_data)
                                changes_made = True
                                continue

                        # Convert JPEG to JXL
                        elif img.format == "JPEG":
                            jxl_data = convert_jpeg_to_jxl(data)
                            if jxl_data:
                                new_filename = f"{os.path.splitext(new_filename)[0]}.jxl"
                                new_zip.writestr(new_filename, jxl_data)
                                changes_made = True
                                continue

                    except (IOError, OSError):
                        pass  # Not an image, write as is

                    # Write the original file if no changes were made
                    new_zip.writestr(new_filename, data)

    # Replace the original ZIP file only if changes were made
    if changes_made:
        os.replace(temp_zip_path, zip_path)
    else:
        os.remove(temp_zip_path)
        print(f"No changes made to: {zip_path}")
