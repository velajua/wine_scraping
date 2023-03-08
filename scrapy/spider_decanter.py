# scrapy runspider spider_decanter.py -a limit=10

import os
import re
import scrapy

from envyaml import EnvYAML
from scrapy.crawler import CrawlerProcess

CONF = EnvYAML(os.path.join('utils', 'config.yaml'))

global page, url, country_, limit_
url = 'https://www.decanter.com/wine-reviews/search/country/page/{page}/3'
page, limit_, country_ = 0, 0, ''


def grape_parsing(list_):
    out = []
    for i in range(0, len(list_), 2):
        if list_[i][0].isnumeric():
            out.append(list_[i].strip() + ' ' + list_[i+1].strip())
        else:
            try:
                out.append(list_[i].strip())
                out.append(list_[i+1].strip())
            except:
                out.append(list_[i].strip())
    return list(set(out))


class SpiderDecanter(scrapy.Spider):
    global page, country_, limit_, url
    
    def __init__(self, country=None, limit=0, *args, **kwargs):
        global country_, limit_
        super(SpiderDecanter, self).__init__(*args, **kwargs)
        if not country:
            country = '''italy'''
        if country.capitalize() in CONF['COUNTRIES'] and not country.isnumeric():
            country_ = str(country.lower())
            self.country_ = country_
        else:
            print('country', country, 'not in', CONF['COUNTRIES'])
        if type(limit) == int or limit.isnumeric():
            limit_ = int(limit)
            self.limit_ = limit_
        else:
            print('limit', limit, 'is not numeric')
    
    name = 'decanter'
    country_ = '''italy''' if not country_ else country_
    limit_ = CONF[country_] if not limit_ else limit_
    url = url.replace('country', country_)

    start_urls = [url.format(page=page+1)]
    allowed_domains = ['www.decanter.com']
    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': f'scrapy/decanter_{country_}.json',
        'FEED_EXPORT_ENCODING': 'utf-8',
        }

    def parse(self, response):
        global page, url, limit_, country_

        link = response.xpath(
            f'//a[contains(@href, "/wine-reviews/{country_}/")]/@href').getall()
        for i in link:

            yield response.follow(i, callback=self.parse_link)
        page += 1

        if page < limit_:
            yield response.follow(url.format(page=page+1),
                                  callback=self.parse)

    def parse_link(self, link):
        title = link.xpath(
            '//h1[@class="WineInfo_wine-title__X8VR4"]/text()').get()
        data_ = link.xpath(
            '//div[contains(@class, "WineInfo_wineInfo__item__type")]/text()'
            ).getall()
        data__ = [re.search(r'<div>(.*)</div>', i).group(1)
                  for i in link.xpath(
                      '//div[contains(@class, "WineInfo_wineInfo__item__value")]/div'
                      ).getall()
                  if re.search(r'<div>(.*)</div>', i)]
        temp = [i[0] if len(i) == 1 else grape_parsing(i)
                if len(i) > 1 else ''
                for i in
                [re.findall(r'(\w*\s?\w+%?)\s*<', i) for i in data__]]
        data__ = [temp[i] if temp[i] else j for i, j in enumerate(data__)]
        ans = {i: j for i, j in zip(data_, data__)}

        yield {'Title': title} | ans


if __name__ == '__main__':
    proc = CrawlerProcess()
    proc.crawl(SpiderDecanter)
    proc.start()
