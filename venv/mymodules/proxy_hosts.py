from urllib import request
from bs4 import BeautifulSoup

url = 'https://free-proxy-list.net'
#bs = BeautifulSoup(request.urlopen(url), 'html.parser')
#print(bs)
bs = BeautifulSoup(request.urlopen(request.Request(url, headers={'User-Agent': 'Mozilla'})), 'html.parser')
for tr in bs.tbody.findAll('tr'):
  td = tr.findAll('td')
  print(tr.text)

"""
import requests

url = 'https://httpbin.org/ip'
proxies = {
  "https": '35.185.201.225:8080',
  "https": '159.65.109.68:8080',
  "https": '200.255.122.174:8080',
  "https": '157.230.179.73:8080',
  "https": '122.102.43.9:8080'
}

response = requests.get(url=url, proxies=proxies)
response.close()

print(response.json())  # 200 - good
"""