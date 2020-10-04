from lxml import html
import requests
import csv

YEARS = [2013,2014,2015]
root_url = 'http://www.footballoutsiders.com/dvoa-ratings/{}/week-{}-dvoa-ratings'
dir_out = "../data/dvoa_ratings/"

def scrape_page(url, year, week):
    resp = requests.get(url)
    if resp.status_code == 200:
        try:
            pagecontent = resp.content
            soup = html.fromstring(pagecontent)
            tables = soup.xpath('//table[@class="stats"]')
            DVOA_table = match_table(tables)
            rows = DVOA_table.getchildren()
            header = rows[0].getchildren()
            header_row = ["".join(parse_td_header(td)) for td in header]
            rows_data = [["".join(parse_td(td)) for td in tr] for tr in rows[1:]]
            with open(dir_out+str(year)+"_"+str(week)+".csv", "w") as f:
                wr = csv.writer(f)
                wr.writerow(header_row)
                wr.writerows(rows_data)
        except:
            print("PAGE ERROR:",url)
    else:
        print("STATUS:",url)

def match_table(tables):
    table_attribs = {'border': '2', 'cellpadding': '3', 'cellspacing': '0', 'class': 'stats'}
    for t in tables:
        cmp_table = dict(t.attrib)
        if cmp_table == table_attribs:
            return t
    return None

def parse_td_header(td):
    regular_td = td.xpath("./b/text()")
    DAVE_td = td.xpath("./font/b/text()")
    if len(regular_td) > len(DAVE_td):
        return regular_td
    else:
        return DAVE_td

def parse_td(td):
    regular_td = td.xpath("./text()")
    DAVE_td = td.xpath("./font/text()")
    if len(regular_td) > len(DAVE_td):
        return regular_td
    else:
        return DAVE_td


for year in YEARS:
    for week in range(1,18):
        url = root_url.format(year, week)
        scrape_page(url, year, week)
