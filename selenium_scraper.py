import os
import argparse
import pandas as pd

# from google.cloud import storage    # Uncomment to save/load the csv file in/from GCS

from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor

from utils.utils import timed_retries
from utils.selenium_utils import (getDriver, find_element_data,
                                  click_element, page_interaction,
                                  type_or_get_text)

FILE_PREF: str = '' if 'wine_scraping' in os.getcwd() else '/tmp/'


@timed_retries(max_retries=6, minutes=2)
def get_wine_info(page: int, country: str, headless: bool,
                  ) -> List[Dict[str, str]]:
    """
    Scrapes wine information from Decanter website for a
    specific country and page.

    Args:
        page (int): Page number of the website to scrape
        country (str): Country name to scrape wine information
        headless (bool): Shows the Chrome drivers

    Returns:
        List[Dict[str, str]]: List of dictionaries with wine
        information scraped from website.
    """
    try:
        driver, full_ = getDriver('headless'
                                  if not headless else None), []
        driver.get(
            f'''https://www.decanter.com\
/wine-reviews/search/{country}/page/{page}/3''')

        for i in find_element_data(
                driver, contains_src=
                'https://decanter-prod-aws1-timeincuk-net.s3.eu-west-1',
                tag_name='img', time=5):
            data_ = {}
            try:
                click_element(
                    driver, 5, find_element_data(
                        driver, return_xpath=True,
                        contains_src=i['src'], tag_name='img', time=5))
            except Exception:
                page_interaction(driver, 'refresh')
                click_element(
                    driver, 5, find_element_data(
                        driver, return_xpath=True,
                        contains_src=i['src'], tag_name='img', time=5))
            try:
                title_ = type_or_get_text(
                    driver, 5, find_element_data(
                        driver, contains_class=
                        'WineInfo_wine-title__X8VR4',
                        return_xpath=True), action='get')
                data_['Title'] = title_
            except Exception:
                page_interaction(driver, 'refresh')
                title_ = type_or_get_text(
                    driver, 5, find_element_data(
                        driver, contains_class=
                        'WineInfo_wine-title__X8VR4',
                        return_xpath=True), action='get')
                data_['Title'] = title_
            try:
                info_ = type_or_get_text(
                    driver, 5, find_element_data(
                        driver, contains_class=
                        'column is-4 WineInfo_wineInfo__OVnX8',
                        return_xpath=True), action='get')
                info__ = info_.split('\n')
                for i in range(0, len(info__), 2):
                    if info__[i] == 'Grapes':
                        data_[info__[i]] = info__[i+1:]
                        break
                    else:
                        data_[info__[i]] = info__[i+1]
            except Exception:
                page_interaction(driver, 'refresh')
                info_ = type_or_get_text(
                    driver, 5, find_element_data(
                        driver, contains_class=
                        'column is-4 WineInfo_wineInfo__OVnX8',
                        return_xpath=True), action='get')
                info__ = info_.split('\n')
                
                for i in range(0, len(info__), 2):
                    if info__[i] == 'Grapes':
                        data_[info__[i]] = info__[i+1:]
                        break
                    else:
                        data_[info__[i]] = info__[i+1]
            full_.append(data_)
            page_interaction(driver, 'back')
        driver.quit()
        return full_
    finally:
        driver.quit()


def main(country: str = 'france', headless: bool = False,
         pages: int = 400) -> None:
    """
    Scrapes wine data for a given country using multiple threads
    and saves the results to a CSV file.

    Args:
        country: A string representing the name of the country to
            scrape wine data from (default: 'france').
        headless: Shows the chrome drivers.
        pages: The number of pages to scrape.
    """
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(get_wine_info, page+1, country,
                                   headless)
                   for page in range(pages)]
    ans = [x for future in futures if future.result()
           for x in future.result()]
    df = pd.DataFrame.from_records(ans)
    df.to_csv(
        f'{FILE_PREF}wine_data_{country}.csv', sep=';')

    # client = storage.Client()    # Uncomment to save/load the csv file in/from GCS
    # bucket = client.bucket('my-bucket-name')
    # blob = bucket.blob(f'wine_data_{country}.csv')
    # blob.upload_from_string(df.to_csv(index=False), content_type='text/csv')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--country', default=None,
                        help='country name (default: france)')
    parser.add_argument('-s', '--show', default=None,
                        action="store_true",
                        help='shows the chrome drivers')
    parser.add_argument('-p', '--pages', default=None,
                        type=int,
                        help='number of pages to scrape')
    args = parser.parse_args()
    country = args.country.lower() if args.country else 'france'
    headless = args.show if args.show else False
    pages = args.pages if args.pages else 400
    
    main(country=country, headless=headless, pages=pages)
