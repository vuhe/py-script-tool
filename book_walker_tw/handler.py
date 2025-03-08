import io
import time
from base64 import b64decode
from collections import deque
from contextlib import suppress
from pathlib import Path
from time import sleep

from PIL import Image
from rich.progress import track
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from book_walker_tw import domain
from book_walker_tw.config import Config

login_url = f"https://member.{domain}/login"


def validate_login(driver: webdriver.Chrome) -> bool:
    driver.get(login_url)
    try:
        WebDriverWait(driver, 2).until(EC.url_changes(login_url))
        return True
    except TimeoutException:
        return False


def login(config: Config):
    driver = config.get_webdriver(headless=False)
    driver.get(login_url)


def wait4loading(driver: webdriver.Chrome, timeout: int = 30):
    WebDriverWait(driver, timeout).until_not(
        lambda x: any(e.is_displayed() for e in x.find_elements(By.CLASS_NAME, "loading")))


def get_pages(driver: webdriver.Chrome, timeout: int = 10):
    begin = time.time()
    while True:
        page_counter = driver.find_element(By.ID, "pageSliderCounter")
        with suppress(ValueError):
            text = page_counter.get_attribute("innerText") or ''
            current_page, total_pages = map(int, text.split('/'))
            break
        if time.time() - begin > timeout:
            raise TimeoutException
    return current_page, total_pages


def get_menu_name(driver: webdriver.Chrome) -> str:
    obj_name = driver.execute_script(
        "for (let k in NFBR.a6G.Initializer){if (NFBR.a6G.Initializer[k]['menu'] !== undefined){ return k; }}")
    return f"NFBR.a6G.Initializer.{obj_name}.menu"


def go2page(driver: webdriver.Chrome, menu_name: str, page: int):
    driver.execute_script(f"{menu_name}.options.a6l.moveToPage({page - 1});")


def download_book(driver: webdriver.Chrome, cfg: Config):
    product_id = cfg.product_id
    overwrite = cfg.overwrite
    save_dir = Path(cfg.get_output_dir())

    driver.get(f"https://www.bookwalker.com.tw/browserViewer/{product_id}/read")

    WebDriverWait(driver, 10).until(
        EC.url_contains(f"pcreader.{domain}"))

    driver.set_window_size(*cfg.viewer_size)  # size of bw page

    driver.switch_to.window(driver.window_handles[-1])

    with suppress(TimeoutException):
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.ID, "pageSliderCounter"))
        )

    if "Error 998" in driver.page_source:
        raise ValueError("Error 998: Must log out from another device")

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".currentScreen canvas")))

    WebDriverWait(driver, 30).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "progressbar")))

    # save_cookies(driver, driver.current_url)
    _, total_pages = get_pages(driver)
    prev_imgs = deque[bytes](maxlen=2)  # used for checking update for 2 buffers
    max_retries = 30

    print(f"Total pages: {total_pages}")

    menu_name = get_menu_name(driver)
    go2page(driver, menu_name, 1)

    for current_page in track(range(1, total_pages + 1), description="Downloading", total=total_pages):
        retry = 0
        savename = save_dir / f"page_{current_page}.png"
        if savename.exists() and not overwrite:
            # logging.debug("Page %s already exists, skipping", current_page)
            continue
        go2page(driver, menu_name, current_page)
        while current_page != get_pages(driver)[0]:
            sleep(0.1)
        wait4loading(driver)
        # logging.debug("Getting page %s out of %s", current_page, total_pages)
        canvas = driver.find_element(By.CSS_SELECTOR, ".currentScreen canvas")
        while retry < max_retries:
            canvas_base64 = driver.execute_script(
                "return arguments[0].toDataURL('image/png').slice(21);", canvas)
            img_bytes = b64decode(canvas_base64)
            img = Image.open(io.BytesIO(img_bytes))
            if all(all(v == 0 for v in c) for c in img.getdata()):
                pass
                # print(f"Blank page {current_page}, treated as unloaded page")
            elif img_bytes not in prev_imgs:
                prev_imgs.append(img_bytes)
                break
            retry += 1
            # logging.debug("Retrying page %s (%s/%s)", current_page, retry, max_retries)
            sleep(0.3)
        if retry == max_retries:
            print("Potentially repeated page {current_page}")
        img.save(savename)
