import os

from fix_cbz_image import console
from fix_cbz_image.handler import HandleTask


def main():
    cbz_files = [
        os.path.join(root, file)
        for root, _, files in os.walk(os.getcwd())
        for file in files if file.endswith(".cbz")
    ]

    if not cbz_files:
        console.print("[cyan]No cbz files found.")
        return

    with HandleTask() as task:
        for cbz_file_path in cbz_files:
            task.submit(cbz_file_path)
        task.show_progress()

    console.print("[cyan]File fix completed")


if __name__ == "__main__":
    main()
