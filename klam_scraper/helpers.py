
import sys
from collections.abc import Callable
from hashlib import sha256
from pathlib import Path
from typing import Any

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as exp_cond
from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy import Column, Integer, String
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base

URL = str
# %%


def start_driver( executable_path: Path ) -> WebDriver:
    """Starts the external webdriver that opens Chrome window and connects to it"""
    # download_path.mkdir(parents=True, exist_ok=True)
    # l_info(f'country_2let={country_2let} Download path is: {download_path}')

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument(f"--lang={country_2let}")

    # preference = {'download.default_directory': str(download_path),
    #              "safebrowsing.enabled": "false"}
    # chrome_options.add_experimental_option('prefs', preference)

    driver = webdriver.Chrome(executable_path=executable_path, options=chrome_options)

    return driver
    # %%


def wait_for_and_get(driver: WebDriver, xpath: str,
                     priority: Callable[ [Any], float] = None, timeout: float = 10):
    """Fait for an element to appear and return it
    if more than one element found, order using the priority function and
    """
    try:
        WebDriverWait(driver, timeout).until(
            exp_cond.presence_of_element_located((By.XPATH, xpath)))
    except TimeoutException as exc:
        print(f'timeout {timeout} when waiting for:\n{xpath}')
        raise exc

    els = driver.find_elements_by_xpath(xpath)

    if priority:
        els = sorted(els, key=priority)
    # print( [el.text for el in els] )
    return els[0]
    # %%


def l_info(*args):
    """Just print stuff to the console"""
    print(*args, file=sys.stderr)


def runpyfile( path, **kwargs ):
    """A wrapper around pycharms own runfile function so that we can import it
    from scripts and avoid 'undefined variable runfile' errors from code checkers
    """
    # noinspection PyUnresolvedReferences
    runfile( path, **kwargs )  # pylint: disable=undefined-variable

    # %%

Base = declarative_base()
# %%


def create_db_engine():
    # %%
    engine = create_engine( 'sqlite:///klam_scraper.db' )

    return engine




def create_schema( engine ):
    # %%
    Base.metadata.drop_all(engine)
    # %%
    Base.metadata.create_all( engine )
    # %%
    Base.metadata.tables
    # %%

class DownloadedImage(Base):
    """Defines a record representing a downloaded image"""

    __tablename__ = 'downloaded_images'
    id = Column(Integer, primary_key=True)
    product_url = Column(String)
    source_url = Column(String)
    filename = Column(String)
    filesize = Column(Integer)
    mime_type = Column(String)
    width = Column(Integer)
    height = Column(Integer)


# %%

def make_file_path( base_path: Path, img_url: URL ) -> Path:
    return base_path / (sha256(img_url.encode('utf8')).hexdigest()[:24] + Path(img_url).suffix)
    # %%
