from lxml import html
import requests
import csv
import re

YEARS = [2013,2014,2015,2016,2017]
CURR_WEEK = 18
root_url = 'http://nflweather.com/en/week/{}/week-{}/'
dir_out = "../data/nfl_weather/" 

def scrape_page(url, year, week):
    resp = requests.get(url)
    if resp.status_code == 200:
        pagecontent = resp.content
        soup  = html.fromstring(pagecontent)
        table = soup.xpath('//table')[0]
        rows  = table.xpath('./tbody/tr')
        teams = [row.xpath('./td[@class="team-img"]/a/@href') for row in rows]
        team1 = [re.sub('/en/team/','',team[0]) for team in teams]
        team2 = [re.sub('/en/team/','',team[1]) for team in teams]
        wind_speeds = clean_fields([row.xpath('./td[12]/text()') for row in rows])
        forecasts = clean_fields([row.xpath('./td[10]/text()') for row in rows])
        header_row = ['team1','team2','wind_conditions','weather_forecast']
        rows_data = list(zip(team1,team2,wind_speeds,forecasts))

        with open(dir_out+str(year)+"_"+str(week)+".csv", "w") as f:
            wr = csv.writer(f)
            wr.writerow(header_row)
            wr.writerows(rows_data)
        
    else:
        print("STATUS:",url)

def parse_td(row):
    teams = row.xpath('./td[@class="team-img"]/a/@href')
    wind_speed = row.xpath('./td[12]/text()')
    new_rows = []
    for i, matchup in enumerate(teams):
        new_row = [matchup]+[wind_speed[i]]
    return new_rows

def clean_fields(rows):
    new_rows = []
    for row in rows:
        for field in row:
            new_rows.append(field.strip())
    return new_rows


for year in YEARS:
    for week in range(1,CURR_WEEK):
        url = root_url.format(year, week)
        scrape_page(url, year, week)