import argparse
from contextlib import suppress
from pathlib import Path

from InquirerPy import inquirer
from selenium.common import WebDriverException

from book_walker_tw.config import Config
from book_walker_tw.handler import login, validate_login, download_book


def main():
    config = Config()

    parser = argparse.ArgumentParser(description='book walker downloader')
    parser.add_argument('--login', action="store_true")
    args = parser.parse_args()

    if args.login:
        login(config)
        inquirer.confirm(message="请登录完后关闭chrome，并重新运行", default=True).execute()
        exit(0)

    driver = config.get_webdriver()

    try:
        if not validate_login(driver):
            raise ValueError("未检测到登录信息")
        config.product_id = inquirer.text(message="要下载的 product id:").execute()
        download_book(driver, config)
    except Exception as e:
        Path("error.png").write_bytes(driver.get_screenshot_as_png())
        raise e
    finally:
        with suppress(WebDriverException):
            driver.quit()


if __name__ == "__main__":
    main()
