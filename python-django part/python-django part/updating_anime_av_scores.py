import mysql.connector
from bs4 import BeautifulSoup
import requests
import time

mydb = mysql.connector.connect(
            host="Your Host Name",
            user="Your User Name",
            password="Your Password",
            database="Your Db Name"
        )
cursor = mydb.cursor()
with requests.Session() as session:
    ddict = {}
    start = time.time()
    url = f"https://myanimelist.net/anime/season"
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    if response.status_code == 200:
        count = 0
        for row in soup.select('h2.h2_anime_title a'):
            if row.get_text(strip=True) == "add":
                continue
            count += 1
            name = row.get_text(strip=True)
            ddict[count] = {"name": f"'{name}'", "score": 0.0}
        count = 0
        for row in soup.select('div.scormem-container div.score-label'):
            sss = row.get_text(strip=True)
            print(sss)
            if sss == 'N/A':
                score = 0.8
            else:
                score = float(float(row.get_text(strip=True)) / 7.8146)
            count += 1
            ddict[count]["score"] = score
for x in ddict:
    print(ddict[x]["name"])
    try:
        cursor.execute(f"""
                        UPDATE av_score_per_anime
                        SET score = {ddict[x]['score']}
                        WHERE name = {ddict[x]['name']}
                """)
    except mysql.connector.errors.ProgrammingError:
        continue
    mydb.commit()