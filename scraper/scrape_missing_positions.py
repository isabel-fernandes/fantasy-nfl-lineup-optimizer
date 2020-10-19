from lxml import html
import pandas as pd
import requests
import pickle
import csv
import re
import os

with open('../data/missing_positions_urls.pkl', 'rb') as f:
    missing_positions_urls = pickle.load(f)

def scrape_page(url):
    resp = requests.get(url)
    if resp.status_code == 200:
        pagecontent = resp.content
        soup  = html.fromstring(pagecontent)
        player_position = soup.xpath('//div[@id="player-bio"]/div[2]/p/span[2]/text()')
        if len(player_position) == 0:
            return ''
        else:
            return str(re.sub('[^A-Za-z]','',player_position[0]))
    else:
        print("STATUS ERROR:",url)
        return ''

missing_positions_dict = {}
for url in missing_positions_urls:
    position = scrape_page(url)
    missing_positions_dict[url] = position

with open('../data/missing_positions_dict.pkl', 'wb') as f:
    pickle.dump(missing_positions_dict, f)

path = '../data/'
files = os.listdir(path)
player_stats_files = [path+f for f in files if "player" in f]

df_dict = {}
for fn in player_stats_files:
    df_dict[fn] = pd.read_csv(fn, index_col=False)

missing_vals = pd.Series(missing_positions_dict).reset_index()
missing_vals.columns = ['profile_url','position_fill']
missing_vals = missing_vals[missing_vals.position_fill != '']

def fill_missing_positions(df, miss_vals):
    df2 = df.merge(miss_vals, how='left', on='profile_url')
    df2.position.fillna(df2.position_fill, inplace=True)
    return df2

for fn, df in df_dict.items():
    replace = fill_missing_positions(df, missing_vals)
    replace.to_csv(fn)

# Fill based on colname_patternspath = '../data/'
files = os.listdir(path)
player_stats_files = [path+f for f in files if "player" in f]

df_dict = {}
for fn in player_stats_files:
    df_dict[fn] = pd.read_csv(fn, index_col=False)
