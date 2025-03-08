import os

from mkv_ass_subset.mkv_ass import process_file


def main():
    os.system('clear')
    file_list = os.listdir(os.getcwd())
    file_list.sort()
    for file_path_name in file_list:
        if file_path_name.lower().endswith(".mkv") or file_path_name.lower().endswith(".mp4"):
            os.system('clear')
            process_file(os.path.join(os.getcwd(), file_path_name))


if __name__ == "__main__":
    main()
