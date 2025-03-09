import io
import subprocess

from PIL import Image


class LibJxlError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


def convert_img_data(data: bytes, filename: str, dry: bool = False):
    try:
        # lossless JXL to WebP
        if filename.endswith(".jxl"):
            if dry:
                return None
            if check_lossless_jxl(data):
                return convert_jxl_to_webp(data), "webp"
            return None

        img = Image.open(io.BytesIO(data))
        img.verify()  # Verify image integrity

        # Correct suffix if necessary
        if not filename.endswith(f".{img.format.lower()}"):
            return data, img.format.lower()

        # Convert PNG to WebP
        if img.format == "PNG":
            if dry:
                return b'', "webp"
            return convert_png_to_webp(data), "webp"

        # Convert JPEG to JXL
        elif img.format == "JPEG":
            if dry:
                return b'', "jxl"
            return convert_jpeg_to_jxl(data), "jxl"

        # unsupported data
        return None

    except (IOError, OSError):
        return None  # Not an image, write as is


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
        raise LibJxlError(f"Error check lossless JXL: {e.stderr.decode()}")


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
        raise LibJxlError(f"Error converting JPEG to WebP: {e.stderr.decode()}")


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
        raise LibJxlError(f"Error converting JPEG to JXL: {e.stderr.decode()}")


def convert_png_to_webp(png_data):
    """
    Convert PNG data to WebP using PIL.
    Returns the WebP binary data.
    """
    with Image.open(io.BytesIO(png_data)) as img:
        # Save the image in WebP format with quality set to 90
        webp_io = io.BytesIO()
        img.save(webp_io, format="WEBP", quality=90)
        return webp_io.getvalue()
