"""Scrape images from a site starting from a search results page (START_URL):
Example:

https://kunastores.com/peru/category/poncho/14/

Conventions:
_xp = XPath
"""

import os
from importlib import reload
from pathlib import Path
from time import sleep
from typing import List

import pandas as pd
import requests
from klam_scraper import helpers as hp
from klam_scraper.helpers import URL, DownloadedImage, WebDriver, make_file_path, sessionmaker
from PIL import Image

START_URL = "https://kunastores.com/peru/category/poncho/14/"
CHROME_DRIVER_PATH = Path(os.getenv('HOME')) / "chromedriver"
IMAGES_PATH = Path('./images')

# %%


def _interactive_testing():
    # %%
    reload( hp )
    hp.runpyfile('klam_scraper/scraper.py')
    # %%
    IMAGES_PATH.mkdir(exist_ok=True, parents=True)
    # %% DB Connection setup
    engine = hp.create_db_engine()
    Session = sessionmaker( bind=engine )
    db_session = Session()
    # %%
    print( "starting chrome driver ...")
    driver = hp.start_driver(executable_path=CHROME_DRIVER_PATH)
    # %%
    product_urls = get_product_urls(driver, start_url=START_URL )
    # %%
    print( f'{len(product_urls)} product urls found')
    [ print(f"\t{url}") for url in product_urls ]

    for prod_url in product_urls:
        download_images_from_product_page( driver, prod_url, db_session )
    # %%
    df = pd.read_sql('select * from downloaded_images', engine )
    # %%
    df.to_csv('downloaded_images.csv', index=False)
    # %%


def get_product_urls( driver: WebDriver, start_url: str ) -> List[URL]:
    """Get all product urls linked from a product list / grid"""
    driver.get( start_url )

    for _ in range(2):
        load_more_button_xp = "//div[contains(@class, 'products-list__products__load-more')]"
        load_more_button = hp.wait_for_and_get( driver, load_more_button_xp )

        load_more_button.click()
        # %% Wait for more results to load
        sleep(5)

    result_links_xp = "//div[contains(@class, 'products-list__products')]//a"
    result_links = driver.find_elements_by_xpath(result_links_xp)

    product_urls = [ link.get_attribute('href') for link in result_links ]

    return product_urls


def download_images_from_product_page( driver: WebDriver, prod_url: URL, db_session ):
    print(f"Visiting product page: {prod_url}")
    driver.get(prod_url)

    thumbnail_xp = "//img[contains(@class, 'image-gallery-thumbnail-image')]"
    hp.wait_for_and_get(driver, thumbnail_xp)

    thumbnails = driver.find_elements_by_xpath(thumbnail_xp)

    image_urls = [ thumbnail.get_attribute('src') for thumbnail in thumbnails ]

    print( f"{len( thumbnails )} thumbnails found, now downloading "
           f"{len(image_urls)} images" )

    for img_url in image_urls:
        print(img_url)
        download_img_to_local( img_url, prod_url, db_session )
    # %%


def download_img_to_local( img_url: URL, prod_url: URL, session ):

    fpath = make_file_path( IMAGES_PATH, img_url )

    if fpath.exists():
        print("Image already in local disk, not downloading again:")

        with fpath.open( "rb" ) as f_in:
            data = f_in.read()
    else:
        resp = requests.get( img_url )
        data = resp.content  # bytes

        with fpath.open( "wb" ) as f_out:
            f_out.write( data )

        img = Image.open(fpath)

        dl = DownloadedImage( product_url=prod_url, source_url=img_url,
                              filename=str(fpath), filesize=len( data ),
                              mime_type=resp.headers['Content-Type'],
                              width=img.size[0], height=img.size[1] )
        session.add(dl)
        session.commit()
        # %%
