import os
import subprocess

import undetected_chromedriver as uc
from InquirerPy import inquirer
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType


class Config:
    chrome_type = ChromeType.GOOGLE
    headless: bool = True
    viewer_size: tuple[int, int] = (1400, 2140)
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    user_data_dir: str = "cookies"
    user_output_dir: str = "output"
    product_id: str = ""
    overwrite: bool = False

    def fix_webdriver_codesign(self):
        webdriver_path = ChromeDriverManager(chrome_type=self.chrome_type).install()
        subprocess.run(["codesign", "--remove-signature", webdriver_path], check=True)
        subprocess.run(["codesign", "--force", "--deep", "-s", "-", webdriver_path], check=True)

    def get_webdriver(self, headless: bool | None = None):
        data_dir = os.path.join(os.getcwd(), self.user_data_dir)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        options = uc.ChromeOptions()
        options.set_capability("unhandledPromptBehavior", "accept")
        options.add_argument("--high-dpi-support=1")
        options.add_argument("--device-scale-factor=1")
        options.add_argument("--force-device-scale-factor=1")
        options.add_argument(f"--user-agent={self.user_agent}")
        options.add_argument(f"--user-data-dir={data_dir}")
        chrome_driver = uc.Chrome(
            options=options,
            headless=headless if headless is not None else self.headless,
            driver_executable_path=ChromeDriverManager(chrome_type=self.chrome_type).install()
        )
        return chrome_driver

    def get_output_dir(self):
        output_dir = os.path.join(os.getcwd(), self.user_output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        elif not inquirer.confirm(message="存在 output，是否继续?", default=False).execute():
            exit(0)
        return output_dir
