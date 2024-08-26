import requests
import csv
import time
import mysql.connector


api_url = "https://api.myanimelist.net/v2/anime/ranking"
api_client_id = "Your Client Id"
mydb = "Your Database"
cursor = mydb.cursor()
ani_list = []
cursor.execute("""
        SELECT a.id
        FROM animes a
        
    """)
for anime in cursor.fetchall():
    ani_list.append(anime[0])

headers = {"X-MAL-CLIENT-ID": api_client_id,}
limit = 10
offset = -10
while True:
    offset += 10
    ranking_type = "all"
    #"upcoming"
    params = {
        "ranking_type": ranking_type,
        "limit": limit,
        "offset": offset,
        "fields": "id, title, genres, media_type, ",
        "nsfw": True,
    }
    response = requests.get(api_url, params=params, headers=headers)
    print(response.json())
    data = response.json()
    for rt in range(0, 9):
        id = data["data"][rt]["node"]["id"]
        title = data["data"][rt]["node"]["title"]
        pic = data["data"][rt]["node"]["main_picture"]["medium"]
        genres = data["data"][rt]["node"]["genres"]
        genre_list = []
        for genre in genres:
            print(genre)
            genre_list.append(genre["id"])
            genre_list.append(genre["name"])
        if id not in ani_list:
            first_list = [id, title]
            first_list.extend(genre_list)
            empty_to_blank = [0, "blank"]
            for index in range(0, int(8 - (len(genre_list) / 2))):
                first_list.extend(empty_to_blank)
            print(first_list)
            cursor.execute(
                    f"INSERT INTO animes VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                ,first_list
                )
            mydb.commit()






