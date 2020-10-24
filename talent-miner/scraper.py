
from typing import Callable, Any
import os
import time
from pathlib import Path
import json
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as exp_cond
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

# TODO: apply filter by 1 / 2end


HOME = Path( os.getenv('HOME') )
STOP = Path( "stop" )


class _Config:
    raw_profiles_path = HOME / '_data/talent/li_raw_profiles_data_eng'
    raw_srps_path = HOME / '_data/talent/li_raw_srps_data_eng'
    contact_info_path = HOME / '_data/talent/li_data_eng_contact_info'

    chrome_driver_path = HOME / 'bin/chromedriver'
    search = 'data engineer python SQL'
    location = 'Colombia'


CFG = _Config
# %%


def main():
    # %%
    CFG.raw_profiles_path.mkdir(exist_ok=True, parents=True)
    CFG.raw_srps_path.mkdir(exist_ok=True, parents=True)
    CFG.contact_info_path.mkdir(exist_ok=True, parents=True)
    # %%
    driver = start_driver( Path(os.getenv('HOME')) / 'Downloads', CFG.chrome_driver_path )
    login( driver )
    # %% Carry out manual search now..
    # _enter_search( driver, CFG.search )
    # _human_wait(1.0)
    # _apply_location_filter( driver, CFG.location )
    # %%
    while True:
        _human_wait(2.5)
        _loop_over_srp_results( driver )

        next_button = wait_for_and_get(driver, '//button[@aria-label="Siguiente"]',
                                       timeout=60.0)
        next_button.click()
    # %%


def _interactive_testing():
    # %%
    # noinspection PyUnresolvedReferences
    runfile("talent-miner/scraper.py")
    # %%


def _loop_over_srp_results( driver):
    # %%
    _scroll_down_like_human( driver )
    _scroll_up_like_human( driver )
    _save_srp_page_source( driver )
    profile_link_xpath = '//a[contains(@data-control-name, "search_srp_result")]'
    i = -1
    # %%
    while True:
        _scroll_up_like_human( driver )
        i += 1
        profile_links = driver.find_elements_by_xpath(profile_link_xpath)
        if i >= len(profile_links):
            break

        link = profile_links[i]
        href = link.get_attribute('href')
        if href.find('search/results/people') >= 0:
            continue

        out_path = get_out_path( href )
        if out_path.exists():
            print(f'{out_path.name} already there, skipping')
            continue

        _scroll_to_elem( driver, link, -70 )
        link.click()
        print( f'\n entering: {out_path.name}')
        _human_wait(2.0)
        download_one_profile( driver )
        _human_wait( 2.0 )
        _scroll_down_like_human(driver)

        if Path("stop").exists():
            print("stop marker found.")
            break
    # %%


def download_one_profile( driver: WebDriver ):
    """Follow link to profiel and dhownload html onto local file"""
    # %%
    _scroll_down_like_human( driver )
    _scroll_up_like_human( driver )
    # %%
    _expand_contact_info( driver )
    _expand_about_section( driver )
    _expand_experience( driver )
    # %%
    _expand_additional_skills( driver )
    _human_wait(1.0)
    # %%
    html = driver.page_source
    out_path = get_out_path( driver.current_url )
    print(f'saving {len(html)} to {out_path.name}')
    with out_path.open('wt') as f_out:
        print(html, file=f_out)

    # back to srp:
    driver.back()
    _human_wait(0.5)
    # %%


def _expand_contact_info( driver ):
    # %%
    xpath1 = '//a[@data-control-name="contact_see_more"]/span'
    exists = _scroll_to_elem_click_if_exists( driver, xpath1, "expand contact info")
    # %%
    if not exists:
        return
    # %%
    xpath2 = '//section[contains(@class, "ci-email") ]//div/a'
    email_anchor = wait_for_and_get(driver, xpath2, on_timeout_raise=False, timeout=5)
    # %%
    if email_anchor:
        email = email_anchor.get_attribute('href')

        li_handle = driver.current_url.split("/")[4]
        with open( CFG.contact_info_path / f'{li_handle}.json', 'wt') as f_out:
            json.dump( {"url": driver.current_url, "li_handle": li_handle, "email": email}, f_out )
    # %%
    driver.back()
    # %%


def _scroll_to_elem_click_if_exists( driver: WebDriver, xpath: str, label: str, verbose=False ):
    # %%
    elem = wait_for_and_get(driver, xpath, timeout=0.0,  on_timeout_raise=False)
    # %%
    if elem:
        print( "scroll_click_if_x: ", label, elem.location )
        _scroll_to_elem(driver, elem, y_delta=-200, verbose=verbose)
        elem.click()
        _human_wait( 0.5 )
        return True
    else:
        return False
    # %%


def _expand_about_section( driver: WebDriver ):
    # %%
    xpath = '//a[@class="lt-line-clamp__more" and @aria-expanded="false"]'
    # %%
    _scroll_to_elem_click_if_exists(driver, xpath, "expand about" )
    # %%


def _test( driver ):
    # %%
    xpath = '//a[@class="lt-line-clamp__more" and @aria-expanded="false"]'
    elems = driver.find_elements_by_xpath( xpath )
    # %%


def _expand_experience( driver: WebDriver ):
    # %%
    xpath = ('//div[contains(@class,"pv-experience-section__see-more")]/button')
    # %%
    _scroll_to_elem_click_if_exists( driver, xpath, "expand experience" )
    # %%


def _expand_additional_skills( driver: WebDriver ):
    # %%
    xpath = ('//button[contains( @class, "pv-skills-section__additional-skills")]'
             '/span[@aria-hidden="true"]')
    _scroll_to_elem_click_if_exists( driver, xpath, "expand skills", verbose=False )
    # %%


def get_out_path( url: str ) -> Path:
    """Local path for saving this profile"""
    # %%
    url_parts = url.lstrip('/').split('/')
    assert url_parts[-3] == 'in', f'url = {url}'
    user_handle = url_parts[-2]
    out_path = CFG.raw_profiles_path / (user_handle + '.html')
    # %%
    return out_path


def _scroll_down_like_human( driver: WebDriver, step=70, wait=0.03 ):
    pos = 100
    prev_yoffset = 0
    while True:
        driver.execute_script(f"window.scrollTo(0, {pos})")
        pos += step * random.lognormvariate(0, 0.1)
        _human_wait( wait )

        yoffset = driver.execute_script('return window.pageYOffset;')
        if yoffset == prev_yoffset or should_stop():
            break

        prev_yoffset = yoffset
    # %%


def _scroll_up_like_human(driver: WebDriver, step=50, wait=0.03, verbose=False):
    pos = driver.execute_script('return window.pageYOffset;')
    if verbose:
        print(  "pos0: ", pos )
    prev_yoffset = -1

    while True:
        driver.execute_script(f"window.scrollTo(0,{pos})")
        pos -= step * random.lognormvariate(0, 0.1)
        _human_wait(wait)

        yoffset = driver.execute_script('return window.pageYOffset;')
        if yoffset == prev_yoffset or should_stop():
            break

        prev_yoffset = yoffset
    # %%


def _scroll_to_elem( driver: WebDriver, elem: WebElement,
                     y_delta=-70, step=70, verbose=False, stop_if_visible=True ):
    prev_y = -1
    while True:
        elem_y = elem.location['y']
        target_y = elem.location['y'] + y_delta

        cur_y = driver.execute_script('return window.pageYOffset')
        if verbose:
            print(f'scroll_to_elem: target_y: {target_y} elem.displayed: {elem.is_displayed()} '
                  f'cur_y: {cur_y}')

        if abs( target_y - cur_y ) < 50:
            driver.execute_script(f"window.scrollTo(0, {target_y})")
            prev_y = cur_y
            break
        elif (cur_y == prev_y) and elem.is_displayed() and elem.is_enabled():
            break
        else:
            direction = +1.0 if (target_y - cur_y) >= 0 else -1.0
            next_y = int( cur_y + direction * step * random.lognormvariate(0, 0.2) )
            driver.execute_script(f"window.scrollTo(0, {next_y})")
            prev_y = cur_y
        if should_stop():
            break
        _human_wait(0.05)


def _scroll_to_y(driver: WebDriver, target_y: int, step=70, verbose=False ):

    # print( f'target_t = {target_y}')
    while True:
        cur_y = driver.execute_script('return window.pageYOffset')
        if verbose:
            print(f'scroll_to_y: cur_y: {cur_y}')

        if abs( target_y - cur_y ) < 50:
            driver.execute_script(f"window.scrollTo(0, {target_y})")
            break
        else:
            direction = +1.0 if (target_y - cur_y) >= 0 else -1.0
            next_y = int( cur_y + direction * step * random.lognormvariate(0, 0.2) )
            # print(cur_y, next_y)
            driver.execute_script(f"window.scrollTo(0, {next_y})")

        if should_stop(): break
        _human_wait(0.05)


def _apply_location_filter( driver: WebDriver, location: str ):
    location_filter = wait_for_and_get( driver, "//button[@id = 'ember2614']")
    assert location_filter.text == "Ubicaciones"
    location_filter.click()
    # %%
    location_field = wait_for_and_get( driver, "//input[contains(@placeholder, 'país o región')]")
    _send_keys_like_human( location_field, location  )
    # %%
    location_apply = wait_for_and_get(driver, "//button[@id = 'ember2622']")
    assert location_apply.text == "Aplicar"
    location_apply.click()
    # %%
    _human_wait( 1.0 )
    # %%


def should_stop() -> bool:
    if STOP.exists():
        STOP.unlink()
        raise RuntimeError('stop found')
    else:
        return False


def start_driver( download_path: Path, executable_path: Path ) -> WebDriver:
    """Starts the external webdriver that opens Chrome window and connects to it"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")

    preference = {'download.default_directory': str(download_path),
                  "safebrowsing.enabled": "false"}
    chrome_options.add_experimental_option('prefs', preference)

    driver = webdriver.Chrome(executable_path=str(executable_path), options=chrome_options)

    return driver
    # %%


def login( driver: WebDriver ):
    """login to ahrefs assumes credentials are available as a json file under
    $HOME/ahref_credentials.txt . example contents:
    {"email": "mateo@me.com", "password": "asdasdsd"}  """

    # %%
    login_url: str = "https://www.linkedin.com/?_l=en_US"
    driver.get(login_url)
    # %%

    credentials = json.loads( open( os.getenv('HOME') + '/' + 'linkedin_credentials.json' ).read() )
    # %%
    # WebDriverWait(driver, 10).until(
    #     exp_cond.presence_of_element_located((By.XPATH, '//form') ) )

    email = driver.find_element_by_name("session_key")
    _send_keys_like_human( email, credentials['email'])
    pwd = driver.find_element_by_name("session_password")
    _send_keys_like_human( pwd, credentials['password'] )
    form = driver.find_elements_by_tag_name("form" )[0]
    _human_wait( 1.0 )
    form.submit()
    # %%


def _enter_search( driver: WebDriver, search: str ):
    elem = wait_for_and_get(driver, "//input[contains(@class, 'search-global-typeahead')]")
    _send_keys_like_human( elem, search + Keys.ENTER )


def _send_keys_like_human( elem: WebElement, keys: str):
    for key in keys:
        elem.send_keys( key )
        _human_wait( mu=0.03 )
    # %%


def _human_wait( mu=0.1, sigma=0.2 ):
    time.sleep( mu * random.lognormvariate(1.0, sigma))
    # %%


def wait_for_and_get(driver: WebDriver, xpath: str,
                     priority: Callable[ [Any], float] = None,
                     timeout: float = 10,
                     on_timeout_raise: bool = True):
    """Fait for an element to appear and return it
    if more than one element found, order using the priority function and"""
    try:
        WebDriverWait(driver, timeout).until(
            exp_cond.presence_of_element_located((By.XPATH, xpath)))
    except TimeoutException as exc:
        print(f'timeout {timeout} when waiting for:\n{xpath}')
        if on_timeout_raise:
            raise exc
        else:
            return None

    els = driver.find_elements_by_xpath(xpath)

    if priority:
        els = sorted(els, key=priority)
    # print( [el.text for el in els] )
    return els[0]
    # %%


def _save_srp_page_source( driver: WebDriver ):
    html = driver.page_source

    fname = driver.current_url.replace('https://', '').replace('/', '__').replace('?', '_')
    with ( CFG.raw_srps_path / fname).open('wt') as f_out:
        print( html, file=f_out)
    # %%
