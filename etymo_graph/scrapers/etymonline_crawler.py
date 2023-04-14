"""Scrape pages from etymonline.com"""
from typing import List
import os
from pathlib import Path
from pprint import pprint
import time

from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from sqlalchemy import text, create_engine
from sqlalchemy.engine import Engine
import requests

from hashlib import sha256

BASE_DOMAIN = "https://www.etymonline.com"
DATA_PATH = Path(os.getenv("HOME") + "/data/etymo_graph")

# typealias
Url = str
# %%


def _main():
    # %%
    runfile("etymo_graph/scrapers/etymonline_crawler.py")
    db_url = f'sqlite:///{DATA_PATH}/crawling.db'
    print(db_url)
    # %%
    eng = create_engine(db_url)
    all_urls_cur = eng.execute("select url, crawled from urls").fetchall()
    all_urls = set(tup[0] for tup in all_urls_cur)
    print(f"all_urls: {len(all_urls)}")

    # %%
    seed_url = "https://www.etymonline.com/word/laboratory"
    # %%
    # mark_as_crawled(con, seed_url, 0)
    # %%
    for url in all_urls:
        mark_as_crawled(con, url, 0)
    # %%
    insert_new(con, seed_url)
    # %%


def insert_new(eng: Engine, url: Url):
    """Add a new url as uncrawled and unscraped, to db"""
    url_hash = _url_hash(url)

    insert = text(f"""insert into urls 
                      (url_hash, url, crawled, scraped) values (:url_hash, :url, 0, 0)
                      on conflict(url_hash) do nothing""")
    eng.execute(insert, url_hash=url_hash, url=url)


def mark_as_crawled(eng: Engine, url: Url, crawled=1):
    """raise crawled flag for url on db"""
    url_hash = _url_hash(url)
    eng.execute(f"""update urls set crawled = {crawled} where url_hash = '{url_hash}'""")
    # %%


def _url_hash(url: Url) -> str:
    return sha256(url.encode("utf8")).hexdigest()
    # %%


def crawl(eng: Engine):
    # %%
    all_urls_cur = eng.execute("select url, crawled from urls").fetchall()
    all_urls = set(tup[0] for tup in all_urls_cur)
    print(f"all_urls: {len(all_urls)}")

    uncrawled_urls = (eng.execute("select url_hash, url from urls where crawled = 0")
                      .fetchall())
    print(f"uncrawled_urls: {len(uncrawled_urls)}")

    for url_hash, url in uncrawled_urls:
        new_ones = crawl_one(url, url_hash)
        time.sleep(2)
        print(f'{url} new_ones has: {len(new_ones)}')
        for new_url in new_ones:
            # print(f'new_url: {new_url} in all_urls: {new_url in all_urls}')
            # print(f'inserting: {new_url}')
            insert_new(eng, new_url)

        mark_as_crawled(eng, url)
    # %%


def crawl_one(url: Url, url_hash: str) -> List[Url]:
    """Crawl one url"""
    resp = requests.get(url)
    if resp.status_code == 200:
        bs = BeautifulSoup(resp.text, features="html.parser")
        (DATA_PATH / (url_hash + ".txt")).write_text(resp.text)
    else:
        print(f"When crawling: {url} error: {resp.status_code} {resp.text}")
        return []

    links = bs.find_all("a")

    other_word_urls = []
    for link in links:
        if 'href' not in link.attrs:
            continue
        href = link.attrs['href']
        if href.startswith('/word/'):
            if '?' in href:
                href = href.split('?')[0]
            if '#' in href:
                href = href.split('#')[0]
            other_word_urls.append(href)

    return [BASE_DOMAIN + url for url in other_word_urls]
    # %%


def scrape_one():
    bs = BeautifulSoup(resp.text, features="html.parser")
    # %%
    h1 = bs.find("h1")
    # %%
    h1_children = h1
    # %%
    definition = h1.findNext()
    # %%
    pprint(list(df_enumerate(definition, [])))
    a# %%


def _create_urls_table(con):
    # %%
    # con.execute('drop table urls ')
    # %%
    con.execute("""create table urls
                       (url_hash text primary key,
                        url varchar, crawled int, scraped int)""")

    # %%


def _df_enumerate(elem: Tag, path: List[str]):
    if isinstance(elem, NavigableString):
        children = []
    else:
        children = list(elem.children)

    if len(children) == 0:
        yield (".".join([str(p) for p in path]), elem)
    else:
        for child in children:
            if child.name:
                new_path = path + [child.name]
            else:
                new_path = path
            yield from df_enumerate(child, new_path)

    # %%