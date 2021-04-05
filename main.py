import requests
from bs4 import BeautifulSoup
import pandas as pd
import aiosmtplib
import asyncio
import re
from email.message import EmailMessage
from typing import Tuple

# Turn on: https://myaccount.google.com/lesssecureapps

print("Covid-19 vaccine appointment in your area....")
find = input("Enter ZIP code: ")
url = f'https://www.findashot.org/appointments/us/zip/{find}'
headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0'}
host = 'smtp.gmail.com'

carrier_map = {
    "verizon": "vtext.com",
    "tmobile": "tmomail.net",
    "sprint": "messaging.sprintpcs.com",
    "at&t": "txt.att.net",
    "boost": "smsmyboostmobile.com",
    "cricket": "sms.cricketwireless.net",
    "uscellular": "email.uscc.net",
}

def get_data(url):
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'lxml')
    return soup

def parse(soup):
    vac_data = []
    results = soup.find_all('div', {'class': 'findashot-location card mb-4'})
    for item in results:
        try:
            products = {
                'Name': item.find('p', {'class': 'title is-size-5-mobile is-size-4-tablet'}).text.strip(),
                'Location': item.find('p', {'class': 'subtitle is-6'}).text.strip(),
                'Website': item.find('a', {'class': 'card-footer-item has-background-success has-text-white'}).attrs['href'],
            }
        except Exception:
            "AttributeError: 'NoneType' object has no attribute 'attrs'"

            vac_data.append(products)
        print(products)
    return vac_data

def output(vac_data):
    vacdf = pd.DataFrame(vac_data)
    vacdf.to_csv('output.csv', index=False)
    print('Saved to CSV')
    return

async def send_txt(*args: str) -> Tuple[dict, str]:
    num, carrier, email, pword, msg, subj = args
    num = str(num)
    to_email = carrier_map[carrier]

    # build message
    message = EmailMessage()
    message["From"] = email
    message["To"] = f"{num}@{to_email}"
    message["Subject"] = subj
    message.set_content(msg)

    # send
    send_kws = dict(username=email, password=pword, hostname=host, port=587, start_tls=True)
    res = await aiosmtplib.send(message, **send_kws)
    msg = "failed" if not re.search(r"\sOK\s", res[1]) else "succeeded"
    print(msg)
    return res
soup = get_data(url)
vac_data = parse(soup)
output(vac_data)

if __name__ == '__main__':
    _num = input("Enter phone number(no spaces or symbols): ")
    _carrier = input("Enter phone service provider: ")
    _email = input("Enter your email: ")
    _pword = input("Enter password for your email: ")
    _msg = "You have been emailed a list of local vaccine locations websites to set an appointment to get vaccinated"
    _subj = "Covid-19 vaccine appointment register"
    coro = send_txt(_num, _carrier, _email, _pword, _msg, _subj)
    asyncio.run(coro)
