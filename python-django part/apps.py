from django.apps import AppConfig
import mysql.connector

users_list = []
over_100_a = []
thirdgenre_list = {}
secondgenre_list = {}
firstgenre_list = {}
fav_a_anime = {}
myresult = []
r_2_result = []
comp_anis = ["Ishuzoku Reviewers", "Kaifuku Jutsushi no Yarinaoshi", "Ex-Arm", "Hametsu no Mars",
                     "Miru Tights", "Chika Gentou Gekiga: Shoujo Tsubaki", "Inu ni Nattara Suki na Hito ni Hirowareta.",
                     "Shitcom",
                     "School Days", "001", "Shibai Taroka", "Pikotarou no Lullaby Lullaby",
                     "Sword Art Online: Extra Edition", "Sword Art Online II", "Tesla Note",
             "Yosuga no Sora: In Solitude, Where We Are Least Alone.", "Go! Saitama", "180-byou de Kimi no Mimi wo Shiawase ni Dekiru ka?",
             "Tenkuu Danzai Skelter+Heaven"]
r_1_result = []
user_infos = []
usersfor3 = set()
genre_dict = {}
av_scores0 = []
av_scores1 = []
list1 = []
list3 = []
list5 = []
list7 = []
b_key = ""
d_key = ""
num_eps = 0
sum_s = 0
mydb = "Same MyDb"
cursor = mydb.cursor()
def data_load():
    global usersfor3, comp_anis, over_100_a, user_infos, thirdgenre_list, secondgenre_list, firstgenre_list, fav_a_anime, myresult
    fetch_size = 1000

    def fetch_in_batches(cursor, fetch_size):
        while True:
            results = cursor.fetchmany(fetch_size)
            if not results:
                break
            for line in results:
                yield line

    cursor.execute("SELECT * FROM user_act1")
    usersfor3.update(line[0].strip() for line in cursor.fetchall())

    cursor.execute("SELECT * FROM hid_as")
    comp_anis.extend(line[0] for line in cursor.fetchall())

    cursor.execute("SELECT * FROM over_100")
    over_100_a.extend(line[0] for line in cursor.fetchall())

    cursor.execute("SELECT * FROM first_userinfo")
    user_infos = {line[0]: line[1] for line in cursor.fetchall() if line[0] in usersfor3}

    cursor.execute("SELECT * FROM 3genre_list")
    for line in cursor.fetchall():
        if line[0] in usersfor3:
            if line[1] not in thirdgenre_list:
                thirdgenre_list[line[1]] = {}
            thirdgenre_list[line[1]][line[0]] = line[5]

    cursor.execute("SELECT * FROM 2genre_list")
    for line in fetch_in_batches(cursor, fetch_size):
        if line[0] in usersfor3:
            if line[1] not in secondgenre_list:
                secondgenre_list[line[1]] = {}
            secondgenre_list[line[1]][line[0]] = line[5]

    cursor.execute("SELECT * FROM 1genre_list")
    for line in fetch_in_batches(cursor, fetch_size):
        if line[0] in usersfor3:
            if line[1] not in firstgenre_list:
                firstgenre_list[line[1]] = {}
            firstgenre_list[line[1]][line[0]] = line[5]

    cursor.execute("SELECT * FROM fav_a_per_anime")
    for line in cursor.fetchall():
        if line[0] in usersfor3:
            if line[0] not in fav_a_anime:
                fav_a_anime[line[0]] = {}
            fav_a_anime[line[0]][line[1]] = line[2]

    cursor.execute("""
        SELECT a.name, a.genre1_name, a.genre2_name, a.genre3_name, a.genre4_name, a.genre5_name, 
            a.genre6_name, a.genre7_name, REPLACE(a.genre8_name, '\r', ''), a.picture_url, a.id
        FROM animes a
    """)
    myresult = cursor.fetchall()

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pages'  # Replace with your app name
    def ready(self):
        data_load()
        print("Done.")
