import argparse
import os
import re


def main():
    parser = argparse.ArgumentParser(description='漫画文件夹名称集数对其')
    parser.add_argument('--start', type=int, required=True, help="开始处理的序号（分隔符前）")
    parser.add_argument('--add', type=int, required=True, help='增加的值')

    args = parser.parse_args()

    for path in os.listdir(os.getcwd()):
        matched = re.match(r'^(\d+)\.(\d+)$', path)
        if matched:
            prefix = int(matched.group(1))
            subfix = int(matched.group(2))
            if args.start <= prefix:
                name = str(prefix) + '.' + str(subfix + args.add)
                os.rename(path, name)


if __name__ == "__main__":
    main()
