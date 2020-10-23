import requests

headers = {
    'authority': 'fantasydata.com',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'origin': 'https://fantasydata.com',
    'content-type': 'application/x-www-form-urlencoded',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://fantasydata.com/user/login?redirecturi=^%^2fnfl^%^2fdfs-projections^%^2ffanduel',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': '_ga=GA1.2.1185220917.1601832129; _fbp=fb.1.1601832129228.609506651; __adroll_fpc=d049e6170f2b7cea5d422f6fc0e63cec-1601832130804; __gads=ID=3f3a95e913c14fb3-22bc663131c40028:T=1603146541:RT=1603146541:S=ALNI_MbnlQRkricMH4K1irw4YEbkyK2vSw; _gid=GA1.2.1512801887.1603426507; _cio=5c1caefc-e24a-65ba-a436-c04cbb9c47b3; __ar_v4=2YUP7TATPFC7XD6D2GIARW^%^3A20201003^%^3A36^%^7CZUS4OCBXGBDWLCGQSOCSQN^%^3A20201003^%^3A36^%^7CNHFCO3TELVGCHHJD5FHXVD^%^3A20201003^%^3A36',
}

data = {
  'Email': 'cjshono^%^40gmail.com^',
  'Password': 'C0dewFriend^%^24^',
  'RedirectUri': '^%^2Fnfl^%^2Fdfs-projections^%^2Ffanduel^',
  'secondary_email': ''
}

response = requests.post('https://fantasydata.com/user/login', headers=headers, data=data)

print(response.status_code)