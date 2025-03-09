import argparse
import os
import re

from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator


def main():
    parser = argparse.ArgumentParser(description='漫画文件夹名称集数对其')
    _ = parser.parse_args()

    start = inquirer.number(
        message="开始处理的序号（分隔符前）:",
        min_allowed=0,
        validate=EmptyInputValidator(),
    ).execute()

    add = inquirer.number(
        message="加值:",
        validate=EmptyInputValidator(),
    ).execute()

    for path in os.listdir(os.getcwd()):
        matched = re.match(r'^(\d+)\.(\d+)$', path)
        if matched:
            prefix = int(matched.group(1))
            subfix = int(matched.group(2))
            if start <= prefix:
                name = str(prefix) + '.' + str(subfix + add)
                os.rename(path, name)


if __name__ == "__main__":
    main()
