import io
import subprocess

from PIL import Image


def check_lossless_jxl(jxl_data):
    try:
        process = subprocess.run(
            ["djxl", "-", "/dev/null", "--output_format=jpeg"],
            input=jxl_data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        output = process.stderr.decode('utf-8', errors='replace')
        if "Warning: could not decode losslessly to JPEG." in output:
            return True  # 无损 JXL
        elif "Reconstructed to JPEG." in output:
            return False  # 转换自 JPEG
        else:
            return False  # 默认判断为有损 JPEG
    except subprocess.CalledProcessError as e:
        print(f"Error check lossless JXL: {e.stderr.decode()}")
        return False


def convert_jxl_to_webp(jxl_data):
    """
    Convert JXL data to WebP using a subprocess for the djxl command-line tool.
    Returns the WebP binary data.
    """
    try:
        process = subprocess.run(
            ["djxl", "-", "-", "--output_format=png"],
            input=jxl_data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        png_data = process.stdout
        with Image.open(io.BytesIO(png_data)) as img:
            # Save the image in WebP format with quality set to 90
            webp_io = io.BytesIO()
            img.save(webp_io, format="WEBP", quality=90)
            return webp_io.getvalue()
    except subprocess.CalledProcessError as e:
        print(f"Error converting JPEG to WebP: {e.stderr.decode()}")
        return None


def convert_jpeg_to_jxl(jpeg_data):
    """
    Convert JPEG data to JXL using a subprocess for the cjxl command-line tool.
    Returns the JXL binary data.
    """
    try:
        process = subprocess.run(
            ["cjxl", "-", "-"],  # No need for -d 0 for JPEG, as cjxl defaults to lossless for JPEG
            input=jpeg_data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return process.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error converting JPEG to JXL: {e.stderr.decode()}")
        return None


def convert_png_to_webp(png_data):
    """
    Convert PNG data to WebP using PIL.
    Returns the WebP binary data.
    """
    try:
        with Image.open(io.BytesIO(png_data)) as img:
            # Save the image in WebP format with quality set to 90
            webp_io = io.BytesIO()
            img.save(webp_io, format="WEBP", quality=90)
            return webp_io.getvalue()
    except subprocess.CalledProcessError as e:
        print(f"Error converting PNG to WebP: {e.stderr.decode()}")
        return None
