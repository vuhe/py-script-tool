import os
from concurrent.futures import ThreadPoolExecutor

from fix_cbz_image.cbz_handler import check_zip_file, process_zip_file


def process_file(file_path):
    if check_zip_file(file_path):
        process_zip_file(file_path)


def main():
    for root, _, files in os.walk(os.getcwd()):
        with ThreadPoolExecutor() as executor:
            for file in files:
                if file.endswith(".cbz"):
                    cbz_file_path = os.path.join(root, file)
                    executor.submit(process_file, cbz_file_path)


if __name__ == "__main__":
    main()
