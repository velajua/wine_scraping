import pandas as pd
import json
import os

country = '''argentina'''

filename = f'scrapy/decanter_{country}.json'

with open(filename, 'r', encoding='utf-8') as json_:
    json__ = json.loads(json_.read())

pd.DataFrame.from_records(json__).to_csv(
    f'wine_data_{country}.csv', sep=';')

if os.path.exists(filename):
    os.remove(filename)
