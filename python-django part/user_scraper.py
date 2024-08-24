import requests

from bs4 import BeautifulSoup
import time

users = set()

def get_users():
    start_len = len(users)
    start = time.time()
    url = "https://myanimelist.net/users.php"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    for row in soup.select('td.borderClass a'):
        user = row.get_text(strip=True)
        users.add(user)
    end = time.time()
    delay = end - start
    with open("users1.txt", mode="w") as s:
        for a in users:
            s.write(a + "\n")
    end_len = len(users)
    print(end_len)
    time.sleep(delay * 2)
    change_amount = end_len - start_len
    print(change_amount)
    if change_amount == 0:
        time.sleep(60)

while len(users) < 200000:
    get_users()

