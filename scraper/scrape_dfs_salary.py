import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

CURR_WEEK = 18
YEARS = [2017, 2018, 2019]
PATH = "../data/fanduel_salaries/"
root_url = "http://rotoguru1.com/cgi-bin/fyday.pl?week={}&year={}&game={}&scsv=1"
urls_by_service = {}
services = ['fd'] # dk, yh
for year in YEARS:
    for service in services:
        urls = []
        for week in range(14, CURR_WEEK):
            urls.append(root_url.format(str(week), str(year),service))
        urls_by_service[service] = urls

for year in YEARS:
    for service in services:
        with open(PATH+service+'_salaries_'+str(year)+'.csv', 'a') as f:
            header = "Week,Year,GID,FirstName,LastName,Pos,Team,h/a,Oppt,"+service+"_points,"+service+"_salary\n"
            f.write(header)
            for url in urls_by_service[service]:
                page = requests.get(url)
                soup = BeautifulSoup(page.text)
                pre_tag_text = soup.find('pre').text
                csv_text = re.sub(';', ',', pre_tag_text)
                csv = csv_text.split('\n')[1:]
                f.write("\n".join(csv))
            f.close()
