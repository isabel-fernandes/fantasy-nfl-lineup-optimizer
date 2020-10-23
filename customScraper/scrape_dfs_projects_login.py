import requests
from requests.adapters import HTTPAdapter

URL = 'https://fantasydata/com'
LOGIN_ROUTE = '/user/login'
REDIRECT_URL = '/nfl/dfs-projections/fanduel'
referer = 'https://fantasydata.com/user/login?redirecturi=%2fnfl%2fdfs-projections%2ffanduel'

cookie = {

}

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    'origin' : URL,
    'referer' : URL + LOGIN_ROUTE
}

s = requests.session()

payload = {
    'Email': 'cjhono@gmail.com',
    'Password' : 'C0dewFriend$',
    'RedirectUri' : REDIRECT_URL,
    'secondary_email' : ''
}

s.mount(URL+LOGIN_ROUTE, HTTPAdapter(max_retries=5))
login_req = s.post(url=URL+LOGIN_ROUTE, headers=HEADERS, data=payload)

print(login_req.status_code)