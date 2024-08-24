import time

from django.shortcuts import render
import mysql.connector
from .apps import usersfor3, comp_anis, over_100_a, user_infos, thirdgenre_list, secondgenre_list, firstgenre_list, fav_a_anime, myresult
import requests

users_list = []
r_2_result = []
sorted_ani_list = {}
r_1_result = []
wanted_score = 0
genre_dict = {}
av_scores0 = []
av_scores1 = []
list1 = {}
list3 = {}
list5 = {}
list7 = []
b_key = ""
d_key = ""
num_eps = 0
sum_s = 0
mydb = mysql.connector.connect(
            host="Your Host Name",
            user="Your User Name",
            password="Your Password",
            database="Your Db Name"
        )
cursor = mydb.cursor()
def load_func():
    users_list = []
    r_2_result = []
    r_1_result = []
    genre_dict = {}
    av_scores0 = []
    av_scores1 = []
    list1 = {}
    list3 = {}
    list5 = {}
    list7 = []
    b_key = ""
    d_key = ""
    num_eps = 0
    sum_s = 0
    wanted_score = 0
    return (users_list, r_2_result, r_1_result, genre_dict, av_scores0, av_scores1, list1, list3, list5,
            list7, b_key, d_key, num_eps, sum_s, wanted_score)
def data_load(a, users_list, mydb, cursor):
    cursor.execute(f"""
                CREATE TEMPORARY TABLE temp_users_list_{a} (
                    name VARCHAR(255),
                    id INT,
                    title VARCHAR(255),
                    score INT,
                    status VARCHAR(255),
                    ep_watched INT
                )
            """)

    cursor.executemany(
        f"INSERT INTO temp_users_list_{a} VALUES (%s, %s, %s, %s, %s, %s)",
        users_list
    )
    mydb.commit()

    cursor.execute(f"""
                SELECT temp_users_list_{a}.name, animes.name, animes.genre1_name, animes.genre2_name, animes.genre3_name, 
                    animes.genre4_name, animes.genre5_name, animes.genre6_name, animes.genre7_name, 
                    REPLACE(animes.genre8_name, '\r', ''), temp_users_list_{a}.ep_watched, temp_users_list_{a}.status, 
                    temp_users_list_{a}.score
                FROM temp_users_list_{a}
                JOIN animes ON animes.id = temp_users_list_{a}.id
            """)
    r_1_result = cursor.fetchall()

    cursor.execute(f"""
                SELECT temp_users_list_{a}.name, animes.name, temp_users_list_{a}.score, av_score_per_anime.score
                FROM temp_users_list_{a} 
                LEFT JOIN animes ON animes.id = temp_users_list_{a}.id
                LEFT JOIN av_score_per_anime on av_score_per_anime.name = animes.name
            """)
    r_2_result = cursor.fetchall()
    return r_1_result, r_2_result
def ani_load(request, a, comp_anis):
    try:
        del users_list
        del genre_dict
    except UnboundLocalError:
        pass
    users_list = []
    ep_sum = 0
    non_message = False
    over_1000 = True
    offset = 0
    headers = {"X-MAL-CLIENT-ID": "Your Client ID", }
    def rt_loop(response, ep_sum, a):
        for rt in range(0, 101):
            id = response.json()["data"][rt]["node"]["id"]
            title = response.json()["data"][rt]["node"]["title"]
            score = response.json()["data"][rt]["list_status"]["score"]
            status = response.json()["data"][rt]["list_status"]["status"]
            if status == "plan_to_watch":
                continue
            if status == "watching":
                comp_anis.append(title)
                continue
            if score == 0:
                comp_anis.append(title)
                continue
            ep = response.json()["data"][rt]["list_status"]["num_episodes_watched"]
            ep_sum += int(ep)
            users_list.append([a, id, title, score, status, ep])
    def over_th(offset, a, over_1000):
        offset += 100
        params = {
            # "status":
            "limit": 100,
            "offset": offset,
            "sort": "list_score",
            # "fields": "id, mean",
            "fields": "list_status",
            "nsfw": True,
        }
        try:
            response = session.get(api_url, params=params, headers=headers)
        except requests.exceptions.JSONDecodeError:
            response = session.get(api_url, params=params, headers=headers)
        try:
            response.json()["data"][0]
        except IndexError:
            return
        try:
            rt_loop(response, ep_sum, a)
        except IndexError:
            over_1000 = False
        if not over_1000:
            over_1000 = True
            over_th(offset, a, over_1000)

    with requests.Session() as session:
        api_url = f"https://api.myanimelist.net/v2/users/{a}/animelist"
        params = {
            # "status":
            "limit": 100,
            "offset": offset,
            "sort": "list_score",
            # "fields": "id, mean",
            "fields": "list_status",
            "nsfw": True,
        }
        try:
            response = session.get(api_url, params=params, headers=headers)
        except requests.exceptions.JSONDecodeError:
            response = session.get(api_url, params=params, headers=headers)
        if response.reason.strip() == "Not Found":
            return [], [], -1
        if "message" in response.json():
            non_message = True
        try:
            "node" in response.json()["data"][0]
        except KeyError:
            pass
        except IndexError:
            pass
        if not non_message:
            try:
                rt_loop(response, ep_sum, a)
            except IndexError:
                over_1000 = False
            if not over_1000:
                over_1000 = True
                over_th(offset, a, over_1000)
    session.close()
    return comp_anis, users_list, ep_sum
def uno_genre(genre_dict, results, genress, a, is_in, mydb, cursor):
    ep_sum = 0
    twoscore_sum = 0
    twocount_sum = 0
    for row11 in results:
        try:
            eps = int(row11[10])
        except IndexError or ValueError:
            continue
        score = int(row11[12])
        row_genres = {row11[2], row11[3], row11[4], row11[5], row11[6], row11[7], row11[8], row11[9]}
        intersection = list(genress.intersection(row_genres))
        len_of_int = len(intersection) - 1
        for index, genres in enumerate(intersection):
            if genres not in genre_dict:
                genre_dict[genres] = {"score": 0, "count": 0, "av": 0, "ep": 0}
            score_sum = genre_dict[genres]["score"] + score
            count_sum = genre_dict[genres]["count"] + 1
            ep_sum += eps
            twoscore_sum += score_sum
            twocount_sum += count_sum
            genre_dict[genres]["score"] = score_sum
            genre_dict[genres]["count"] = count_sum
            genre_dict[genres]["av"] = score_sum / count_sum if count_sum > 0 else 0
            genre_dict[genres]["ep"] = genre_dict[genres]["ep"] + eps
            max_left = len_of_int - index
            if max_left < 1:
                continue
            for in_int in range(1, max_left + 1):
                if intersection[index + in_int] not in genre_dict[genres]:
                    genre_dict[genres][intersection[index + in_int]] = {"score": 0, "count": 0, "av": 0, "ep": 0}
                score_sum = genre_dict[genres][intersection[index + in_int]]["score"] + score
                count_sum = genre_dict[genres][intersection[index + in_int]]["count"] + 1
                ep_sum += eps
                genre_dict[genres][intersection[index + in_int]]["score"] = score_sum
                genre_dict[genres][intersection[index + in_int]]["count"] = count_sum
                genre_dict[genres][intersection[index + in_int]]["av"] = score_sum / count_sum if count_sum > 0 else 0
                genre_dict[genres][intersection[index + in_int]]["ep"] = genre_dict[genres][intersection[index + in_int]]["ep"] + eps
                in_max_left = max_left - in_int
                for in_1_int in range(1, in_max_left + 1):
                    if intersection[index + in_int + in_1_int] not in genre_dict[genres][intersection[index + in_int]]:
                        genre_dict[genres][intersection[index + in_int]][intersection[index + in_int + in_1_int]] = {"score": 0, "count": 0, "av": 0, "ep": 0}
                    score_sum = genre_dict[genres][intersection[index + in_int]][intersection[index + in_int + in_1_int]]["score"] + score
                    count_sum = genre_dict[genres][intersection[index + in_int]][intersection[index + in_int + in_1_int]]["count"] + 1
                    ep_sum += eps
                    genre_dict[genres][intersection[index + in_int]][intersection[index + in_int + in_1_int]]["score"] = score_sum
                    genre_dict[genres][intersection[index + in_int]][intersection[index + in_int + in_1_int]]["count"] = count_sum
                    genre_dict[genres][intersection[index + in_int]][intersection[index + in_int + in_1_int]][
                        "av"] = score_sum / count_sum if count_sum > 0 else 0
                    genre_dict[genres][intersection[index + in_int]][intersection[index + in_int + in_1_int]]["ep"] = \
                        genre_dict[genres][intersection[index + in_int]][intersection[index + in_int + in_1_int]]["ep"] + eps
    if not is_in:
        cursor.execute(f"""
                                                                       DELETE FROM 1genre_list
                                                                       WHERE username = "{a}"        
                                                                   """)
        cursor.execute(f"""
                                       DELETE FROM first_userinfo
                                       WHERE name = "{a}"        
                                   """)
    data_to_insert_list = []
    for sasa in genre_dict:
        if genre_dict[sasa]["ep"] != 0:
            data_to_insert = (a, sasa, genre_dict[sasa]["count"], genre_dict[sasa]["av"],
                              genre_dict[sasa]["ep"], float(
                genre_dict[sasa]["av"] - (twoscore_sum / twocount_sum) + (
                        25 * genre_dict[sasa]["ep"] / ep_sum)
                + (25 * genre_dict[sasa]["count"] / twocount_sum)))
            data_to_insert_list.append(data_to_insert)
            list1[sasa] = float(
                    genre_dict[sasa]["av"] - (twoscore_sum / twocount_sum) + (
                            25 * genre_dict[sasa]["ep"] / ep_sum)
                    + (25 * genre_dict[sasa]["count"] / twocount_sum))
        else:
            list1[sasa] = 0
    sql_query = "INSERT INTO 1genre_list (username, genre_name, count, av, ep_count, 2_av) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.executemany(sql_query, data_to_insert_list)
    mydb.commit()
    genre_list = []
    for genr in genress:
        if genr not in genre_dict:
            continue
        for sas in genress:
            if sas not in genre_dict[genr]:
                continue
            if genre_dict[genr][sas]["ep"] != 0:
                new_dict = {f"{genr} and {sas}": float(
                    genre_dict[genr][sas]["av"] - (twoscore_sum / twocount_sum) + (
                            25 * genre_dict[genr][sas]["ep"] / ep_sum)
                    + (25 * genre_dict[genr][sas]["count"] / twocount_sum))}
                genre_list.append(new_dict)
    genre_list = sorted(genre_list, key=lambda x: list(x.values())[0], reverse=True)
    b_key = list(genre_list[0].keys())[0]
    if not is_in:
        cursor.execute(f"""
                                                                    DELETE FROM 2genre_list
                                                                    WHERE username = "{a}"        
                                                                """)
    data_to_insert_list = []
    for kale in genre_list[:10]:
        for key in kale.keys():
            key2 = key.split("and")
            key12 = key2[0].strip()
            key13 = key2[1].strip()
            data_to_insert = (
                a, key, genre_dict[key12][key13]["count"], genre_dict[key12][key13]["av"],
                genre_dict[key12][key13]["ep"], float(
                    genre_dict[key12][key13]["av"] - (twoscore_sum / twocount_sum) + (
                            25 * genre_dict[key12][key13]["ep"] / ep_sum)
                    + (25 * genre_dict[key12][key13]["count"] / twocount_sum))
            )
            data_to_insert_list.append(data_to_insert)
            list3[(key12, key13)] = float(
                              genre_dict[key12][key13]["av"] - (twoscore_sum / twocount_sum) + (
                                      25 * genre_dict[key12][key13]["ep"] / ep_sum)
                              + (25 * genre_dict[key12][key13]["count"] / twocount_sum))
    sql_query = "INSERT INTO 2genre_list (username, genre_name, count, av, ep_count, 2_av) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.executemany(sql_query, data_to_insert_list)
    mydb.commit()
    genre_list = []
    for genre123 in genress:
        if genre123 not in genre_dict:
            genre_dict[genre123] = {}
        for sasa133 in genress:
            if sasa133 not in genre_dict[genre123]:
                continue
            for sasa233 in genress:
                if sasa233 not in genre_dict[genre123][sasa133] or sasa233 not in genre_dict[genre123]:
                    continue
                if genre_dict[genre123][sasa133][sasa233]["ep"] != 0:
                    new_dict = {f"{genre123} and {sasa133} and {sasa233}": float(
                        genre_dict[genre123][sasa133][sasa233]["av"] - (twoscore_sum / twocount_sum) + (
                                25 * genre_dict[genre123][sasa133][sasa233]["ep"] / ep_sum)
                        + (25 * genre_dict[genre123][sasa133][sasa233]["count"] / twocount_sum))}
                    genre_list.append(new_dict)
    genre_list = sorted(genre_list, key=lambda x: list(x.values())[0], reverse=True)
    d_key = list(genre_list[0].keys())[0]
    if not is_in:
        cursor.execute(f"""
                                                                    DELETE FROM 3genre_list
                                                                    WHERE username = "{a}"        
                                                                """)
    data_to_insert_list = []
    for kale in genre_list[:5]:
        for key in kale.keys():
            key2 = key.split("and")
            key12 = key2[0].strip()
            key13 = key2[1].strip()
            key14 = key2[2].strip()
            data_to_insert = (
                a, key, genre_dict[key12][key13][key14]["count"],
                genre_dict[key12][key13][key14]["av"],
                genre_dict[key12][key13][key14]["ep"],
                float(
                    genre_dict[key12][key13][key14]["av"] - (twoscore_sum / twocount_sum) + (
                            25 * genre_dict[key12][key13][key14]["ep"] / ep_sum)
                    + (25 * genre_dict[key12][key13][key14]["count"] / twocount_sum)))
            data_to_insert_list.append(data_to_insert)
            list5[(key12, key13, key14)] = float(
                     genre_dict[key12][key13][key14]["av"] - (twoscore_sum / twocount_sum) + (
                             25 * genre_dict[key12][key13][key14]["ep"] / ep_sum)
                     + (25 * genre_dict[key12][key13][key14]["count"] / twocount_sum))
            genre_dict[key12][key13][key14] = {"score": 0, "count": 0, "av": 0, "ep": 0}
    sql_query = "INSERT INTO 3genre_list (username, genre_name, count, av, ep_count, 2_av) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.executemany(sql_query, data_to_insert_list)
    mydb.commit()
    if twocount_sum > 0:
        sum_s = twoscore_sum / twocount_sum
    else:
        return
    if float(sum_s) and float(sum_s) > 0:
        data_to_insert = (
            f"{a}", sum_s, sum_s)
        sql_query = "INSERT INTO first_userinfo (name, av_score, av_score_wo_dropped) VALUES (%s, %s, %s)"
        cursor.execute(sql_query, data_to_insert)
        mydb.commit()
        av_scores1.append([a, sum_s, sum_s])
    return list5, list3, list1, av_scores0, av_scores1, sum_s, d_key, b_key
def home_page(request, *args, **kwargs):
    global sorted_ani_list
    global wanted_score
    name = request.POST.get("account_name")
    if name:
        (users_list, r_2_result, r_1_result, genre_dict, av_scores0, av_scores1, list1, list3, list5,
         list7, b_key, d_key, num_eps, sum_s, wanted_score) = load_func()
        user_list = {}
        genress = {'Action', 'Adventure', 'Avant Garde', 'Award Winning', 'Boys Love',
                   'Comedy', 'Drama', 'Fantasy', 'Girls Love', 'Gourmet', 'Horror', 'Mystery',
                   'Romance', 'Sci-Fi', 'Slice of Life', 'Sports', 'Supernatural', 'Suspense', 'Ecchi',
                   'Erotica', 'Hentai', 'Adult Cast', 'Anthropomorphic', 'CGDCT', 'Childcare', 'Combat Sports',
                   'Crossdressing',
                   'Delinquents', 'Detective', 'Educational', 'Gag Humor', 'Gore', 'Harem', 'High Stakes Game',
                   'Historical', 'Idols (Female)',
                   'Idols (Male)', 'Isekai', 'Iyashikei', 'Love Polygon', 'Magical Sex Shift', 'Mahou Shoujo',
                   'Martial Arts', 'Mecha', 'Medical',
                   'Military', 'Music', 'Mythology', 'Organized Crime', 'Otaku Culture', 'Parody',
                   'Performing Arts', 'Pets', 'Psychological', 'Racing',
                   'Reincarnation', 'Reverse Harem', 'Romantic Subtext', 'Samurai', 'School', 'Showbiz', 'Space',
                   'Strategy Game', 'Super Power', 'Survival',
                   'Team Sports', 'Time Travel', 'Vampire', 'Video Game', 'Visual Arts', 'Workplace', 'Josei',
                   'Kids', 'Seinen', 'Shoujo', 'Shounen'}
        is_in = True
        a = name.strip()
        #Enter The Same Mydb thing here
        mydb = mysql.connector.connect(
            host="Your Host Name",
            user="Your User Name",
            password="Your Password",
            database="Your Db Name"
        )
        cursor = mydb.cursor()
        cursor.execute(f"DROP TEMPORARY TABLE IF EXISTS temp_users_list_{a}")
        fake_comp_anis = []
        fake_comp_anis, users_list, ep_sum = ani_load(request, a, fake_comp_anis)
        if ep_sum < 0:
            return render(request, "1index.html", {"user_not_found": True, "user": a.strip()})
        comp_anis.extend(fake_comp_anis)
        r_1_result, r_2_result = data_load(a, users_list, mydb, cursor)
        try:
            num_eps = float(ep_sum / len(users_list))
        except ZeroDivisionError:
            return render(request, "1index.html", {"user_0": True, "user": name.strip()})
        if name in usersfor3:
            is_in = False
        list5, list3, list1, av_scores0, av_scores1, sum_s, d_key, b_key = uno_genre(genre_dict, r_1_result, genress, a, is_in, mydb, cursor)
        user_anime_stats = []
        u_list = []
        user_dict = {}
        for row77 in r_2_result:
            try:
                av_score = float(row77[3])
            except TypeError:
                continue
            users_av_score = float(int(row77[2]) / float(sum_s))
            fin = float(users_av_score - av_score)
            user_dict[row77[1]] = fin
        sorted_user_list = sorted(user_dict.items(), key=lambda x: x[1])
        if not is_in:
            cursor.execute(f"""
                                                                                            DELETE FROM fav_a_per_anime
                                                                                            WHERE user = "{a}"        
                                                                                        """)
        data_to_insert_list = []
        for aa in sorted_user_list[:5]:
            data_to_insert = (
                a, aa[0], aa[1])
            data_to_insert_list.append(data_to_insert)
            user_anime_stats.append([a, aa[0], aa[1]])
            u_list.append(aa)
        sql_query = "INSERT INTO fav_a_per_anime (user, name, score) VALUES (%s, %s, %s)"
        cursor.executemany(sql_query, data_to_insert_list)
        mydb.commit()
        sorted_user_list = sorted(user_dict.items(), key=lambda x: x[1], reverse=True)
        f_key = sorted_user_list[0][0]
        data_to_insert_list = []
        for aaa in sorted_user_list[:5]:
            if aaa in u_list:
                continue
            data_to_insert = (
                a, aaa[0], aaa[1])
            data_to_insert_list.append(data_to_insert)
            user_anime_stats.append([a, aaa[0], aaa[1]])
        sql_query = "INSERT INTO fav_a_per_anime (user, name, score) VALUES (%s, %s, %s)"
        cursor.executemany(sql_query, data_to_insert_list)
        mydb.commit()
        del user_dict
        av_sum = 0
        for a, b in list1.items():
            av_sum += b
        av_sum = float(av_sum / len(list1))
        for genre, users in firstgenre_list.items():
            try:
                score2 = list1[genre]
            except KeyError:
                score2 = av_sum * 2
            for user, score in users.items():
                score = float(abs(score - score2) / 35)
                try:
                    user_list[user] += score
                except KeyError:
                    user_list[user] = score
        for genre, users in secondgenre_list.items():
            try:
                score2 = list1[genre]
            except KeyError:
                score2 = av_sum * 2
            for user, score in users.items():
                score = float(abs(score - score2) / 10)
                user_list[user] += score
        for genre, users in thirdgenre_list.items():
            try:
                score2 = list1[genre]
            except KeyError:
                score2 = av_sum * 2
            for user, score in users.items():
                score = float(abs(score - score2) / 5)
                user_list[user] += score
        for reader8_2 in user_anime_stats:
            anime = reader8_2[1]
            score = float(reader8_2[2])
            for user_4_ in usersfor3:
                try:
                    fav_a_anime[user_4_]
                except KeyError:
                    continue
                if anime in fav_a_anime[user_4_]:
                    score2 = fav_a_anime[user_4_][anime]
                else:
                    score2 = 5
                if score2 == 0:
                    score2 = 5
                score_abs = abs(score - score2)
                abs_score = float((score_abs / 20))
                if user_4_ not in user_list:
                    user_list[user_4_] = abs_score
                else:
                    user_list[user_4_] += abs_score
        for user_5_ in usersfor3:
            try:
                user_infos[user_5_]
            except KeyError:
                continue
            score2 = user_infos[user_5_]
            score = float(score2 - sum_s)
            abs_score = abs(score)
            if user_5_ not in user_list:
                user_list[user_5_] = abs_score
            else:
                user_list[user_5_] += abs_score
        sorted_user_list = sorted(user_list.items(), key=lambda x: x[1])
        ani_list = {}
        for coms in users_list:
            comp_anis.append(coms[2])
        point_list = 0
        for coms8 in user_anime_stats:
            new_list = []
            for user_6_ in usersfor3:
                try:
                    fav_a_anime[user_6_]
                except KeyError:
                    continue
                if coms8[1] in fav_a_anime[user_6_]:
                    new_list.append(user_6_)
            point_list += len(new_list)
            for new_list_1 in new_list:
                for coms8_2 in fav_a_anime[new_list_1]:
                    if coms8_2 not in ani_list:
                        ani_list[coms8_2] = {"score": fav_a_anime[new_list_1][coms8_2], "pic": "", "id": 0}
                    else:
                        ani_list[coms8_2]["score"] = ani_list[coms8_2]["score"] + fav_a_anime[new_list_1][coms8_2]
        for coms1 in myresult:
            pic = coms1[9]
            id = str(coms1[10])
            if None in coms1[1:9]:
                if coms1[0] not in ani_list:
                    ani_list[coms1[0]] = {"score": 0, "pic": pic, "id": id}
                else:
                    ex_score = ani_list[coms1[0]]["score"]
                    ani_list[coms1[0]] = {"score": ex_score, "pic": pic, "id": id}
            else:
                for a in coms1[1:9]:
                    if a == "blank":
                        break
                    try:
                        score = list1[a]
                        score = float(float(score) * point_list / 35000)
                    except KeyError:
                        score = -abs(float(float(av_sum * 2) * point_list / 35000))
                    if coms1[0] not in ani_list:
                        ani_list[coms1[0]] = {"score": score, "pic": pic, "id": id}
                    else:
                        ex_score = ani_list[coms1[0]]["score"]
                        ani_list[coms1[0]] = {"score": ex_score + score, "pic": pic, "id": id}
                set1 = set(coms1[1:9])
                for temp_tuple, score in list3.items():
                    set2 = set(temp_tuple)
                    if set1.intersection(set2) == 2:
                        score = float(float(score) * point_list / 28000)
                        ani_list[coms1[0]]["score"] += score
                for sec_temp_tuple, sec_score in list5.items():
                    set3 = set(sec_temp_tuple)
                    if set1.intersection(set3) == 3:
                        sec_score = float(float(sec_score) * point_list / 21000)
                        ani_list[coms1[0]]["score"] += sec_score
        for user_list_row1 in sorted_user_list[1::11]:
            try:
                fav_a_anime[user_list_row1[0]]
            except KeyError:
                continue
            for coms9_2 in fav_a_anime[user_list_row1[0]]:
                if coms9_2 in ani_list:
                    ani_list[coms9_2]["score"] = ani_list[coms9_2]["score"] + fav_a_anime[user_list_row1[0]][coms9_2] / 10
        for hasa2 in over_100_a:
            if hasa2 in ani_list:
                if num_eps > 26:
                    ani_list[hasa2]["score"] = float(ani_list[hasa2]["score"] * 5 / 4)
                else:
                    ani_list[hasa2]["score"] = ani_list[hasa2]["score"] / 2
        wanted_score = ani_list[f_key]["score"]
        for hasa in comp_anis:
            ani_list[hasa] = {"score": -6900}
        sorted_ani_list = sorted(ani_list.items(), key=lambda x: x[1]["score"], reverse=True)
        if wanted_score <= 0:
            wanted_score = sorted_ani_list[0][1]["score"]
        cursor.execute(f"DROP TEMPORARY TABLE IF EXISTS temp_users_list_{a}")
        if is_in:
            data_to_insert = (f"{a}",)
            sql_query = "INSERT INTO user_act1 (name) VALUES (%s)"
            cursor.execute(sql_query, data_to_insert)
            mydb.commit()
        return render(request, "1index.html", {"user": name.strip(), "ani1": sorted_ani_list[0][0],
                                               "ani1_score": f"{(sorted_ani_list[0][1]['score'] / wanted_score) * 100:.5f}%",
                                               "ani1_pic": sorted_ani_list[0][1]["pic"],
                                               "ani1_id": sorted_ani_list[0][1]["id"],
                                               "ani2": sorted_ani_list[1][0],
                                               "ani2_score": f"{(sorted_ani_list[1][1]['score'] / wanted_score) * 100:.5f}%",
                                               "ani2_pic": sorted_ani_list[1][1]["pic"],
                                               "ani2_id": sorted_ani_list[1][1]["id"],
                                               "ani3": sorted_ani_list[2][0],
                                               "ani3_score": f"{(sorted_ani_list[2][1]['score'] / wanted_score) * 100:.5f}%",
                                               "ani3_pic": sorted_ani_list[2][1]["pic"],
                                               "ani3_id": sorted_ani_list[2][1]["id"],
                                               "ani4": sorted_ani_list[3][0],
                                               "ani4_score": f"{(sorted_ani_list[3][1]['score'] / wanted_score) * 100:.5f}%",
                                               "ani4_pic": sorted_ani_list[3][1]["pic"],
                                               "ani4_id": sorted_ani_list[3][1]["id"],
                                               "ani5": sorted_ani_list[4][0],
                                               "ani5_score": f"{(sorted_ani_list[4][1]['score'] / wanted_score) * 100:.5f}%",
                                               "ani5_pic": sorted_ani_list[4][1]["pic"],
                                               "ani5_id": sorted_ani_list[4][1]["id"],
                                               "ani6": sorted_ani_list[5][0],
                                               "ani6_score": f"{(sorted_ani_list[5][1]['score'] / wanted_score) * 100:.5f}%",
                                               "ani6_pic": sorted_ani_list[5][1]["pic"],
                                               "ani6_id": sorted_ani_list[5][1]["id"], "1genre": b_key,
                                               "3genre": d_key, "av_score": sum_s, "top_anime": f_key,
                                               "user1": sorted_user_list[1][0],
                                               "user1_s": sorted_user_list[1][1],
                                               "user2": sorted_user_list[2][0],
                                               "user2_s": sorted_user_list[2][1],
                                               "user3": sorted_user_list[3][0],
                                               "user3_s": sorted_user_list[3][1],
                                               "user4": sorted_user_list[4][0],
                                               "user4_s": sorted_user_list[4][1],
                                               "user5": sorted_user_list[5][0],
                                               "user5_s": sorted_user_list[5][1],
                                               "user6": sorted_user_list[6][0],
                                               "user6_s": sorted_user_list[6][1],
                                               "user7": sorted_user_list[7][0],
                                               "user7_s": sorted_user_list[7][1],
                                               "user8": sorted_user_list[8][0],
                                               "user8_s": sorted_user_list[8][1],
                                               "user9": sorted_user_list[9][0],
                                               "user9_s": sorted_user_list[9][1],
                                               "user10": sorted_user_list[10][0],
                                               "user10_s": sorted_user_list[10][1],
                                               "user11": sorted_user_list[11][0],
                                               "user11_s": sorted_user_list[11][1],
                                               "user12": sorted_user_list[12][0],
                                               "user12_s": sorted_user_list[12][1],
                                               "user13": sorted_user_list[13][0],
                                               "user13_s": sorted_user_list[13][1],
                                               "user14": sorted_user_list[14][0],
                                               "user14_s": sorted_user_list[14][1],
                                               "user15": sorted_user_list[15][0],
                                               "user15_s": sorted_user_list[15][1],
                                               "user16": sorted_user_list[16][0],
                                               "user16_s": sorted_user_list[16][1],
                                               "user17": sorted_user_list[17][0],
                                               "user17_s": sorted_user_list[17][1],
                                               "user18": sorted_user_list[18][0],
                                               "user18_s": sorted_user_list[18][1],
                                               "user19": sorted_user_list[19][0],
                                               "user19_s": sorted_user_list[19][1],
                                               "user20": sorted_user_list[20][0],
                                               "user20_s": sorted_user_list[20][1],
                                               "user21": sorted_user_list[21][0],
                                               "user21_s": sorted_user_list[21][1],
                                               "user22": sorted_user_list[22][0],
                                               "user22_s": sorted_user_list[22][1],
                                               "user23": sorted_user_list[23][0],
                                               "user23_s": sorted_user_list[23][1],
                                               "user24": sorted_user_list[24][0],
                                               "user24_s": sorted_user_list[24][1],
                                               "user25": sorted_user_list[25][0],
                                               "user25_s": sorted_user_list[25][1],
                                               "user26": sorted_user_list[26][0],
                                               "user26_s": sorted_user_list[26][1],
                                               "user27": sorted_user_list[27][0],
                                               "user27_s": sorted_user_list[27][1],
                                               "user28": sorted_user_list[28][0],
                                               "user28_s": sorted_user_list[28][1],
                                               "user29": sorted_user_list[29][0],
                                               "user29_s": sorted_user_list[29][1],
                                               "user30": sorted_user_list[30][0],
                                               "user30_s": sorted_user_list[30][1],
                                               "user31": sorted_user_list[31][0],
                                               "user31_s": sorted_user_list[31][1],
                                               "user32": sorted_user_list[32][0],
                                               "user32_s": sorted_user_list[32][1],
                                               "user33": sorted_user_list[33][0],
                                               "user33_s": sorted_user_list[33][1],
                                               "user34": sorted_user_list[34][0],
                                               "user34_s": sorted_user_list[34][1],
                                               "user35": sorted_user_list[35][0],
                                               "user35_s": sorted_user_list[35][1],
                                               "user36": sorted_user_list[36][0],
                                               "user36_s": sorted_user_list[36][1],
                                               "user37": sorted_user_list[37][0],
                                               "user37_s": sorted_user_list[37][1],
                                               "user38": sorted_user_list[38][0],
                                               "user38_s": sorted_user_list[38][1],
                                               "user39": sorted_user_list[39][0],
                                               "user39_s": sorted_user_list[9][1],
                                               "user40": sorted_user_list[40][0],
                                               "user40_s": sorted_user_list[40][1],
                                               "user41": sorted_user_list[41][0],
                                               "user41_s": sorted_user_list[41][1],
                                               "user42": sorted_user_list[42][0],
                                               "user42_s": sorted_user_list[42][1],
                                               "user43": sorted_user_list[43][0],
                                               "user43_s": sorted_user_list[43][1],
                                               "user44": sorted_user_list[44][0],
                                               "user44_s": sorted_user_list[44][1],
                                               "user45": sorted_user_list[45][0],
                                               "user45_s": sorted_user_list[45][1],
                                               "user46": sorted_user_list[46][0],
                                               "user46_s": sorted_user_list[46][1],
                                               "user47": sorted_user_list[47][0],
                                               "user47_s": sorted_user_list[47][1],
                                               "user48": sorted_user_list[48][0],
                                               "user48_s": sorted_user_list[48][1],
                                               "user49": sorted_user_list[49][0],
                                               "user49_s": sorted_user_list[9][1],
                                               "user50": sorted_user_list[50][0],
                                               "user50_s": sorted_user_list[50][1]})
    elif request.POST.get("fixed_field"):
        return view_all(sorted_ani_list, wanted_score, request, *args, **kwargs)
    else:
        return render(request, "index.html", {})

def view_all(sorted_ani_list, wanted_score, request, *args, **kwargs):
    try:
        sorted_ani_list[0]
        print(wanted_score)
        return render(request, "2index.html", {"ani1": sorted_ani_list[0][0],
                                                   "ani1_score": f"{(sorted_ani_list[0][1]['score'] / wanted_score) * 100:.5f}%", "ani1_pic": sorted_ani_list[0][1]["pic"],
                                                   "ani1_id": sorted_ani_list[0][1]["id"],
                                                   "ani2": sorted_ani_list[1][0], "ani2_score": f"{(sorted_ani_list[1][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani2_pic": sorted_ani_list[1][1]["pic"], "ani2_id": sorted_ani_list[1][1]["id"],
                                                   "ani3": sorted_ani_list[2][0],
                                                   "ani3_score": f"{(sorted_ani_list[2][1]['score'] / wanted_score) * 100:.5f}%", "ani3_pic": sorted_ani_list[2][1]["pic"],
                                                   "ani3_id": sorted_ani_list[2][1]["id"],
                                                   "ani4": sorted_ani_list[3][0], "ani4_score": f"{(sorted_ani_list[3][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani4_pic": sorted_ani_list[3][1]["pic"], "ani4_id": sorted_ani_list[3][1]["id"],
                                                   "ani5": sorted_ani_list[4][0],
                                                   "ani5_score": f"{(sorted_ani_list[4][1]['score'] / wanted_score) * 100:.5f}%", "ani5_pic": sorted_ani_list[4][1]["pic"],
                                                   "ani5_id": sorted_ani_list[4][1]["id"],
                                                   "ani6": sorted_ani_list[5][0], "ani6_score": f"{(sorted_ani_list[5][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani6_pic": sorted_ani_list[5][1]["pic"], "ani6_id": sorted_ani_list[5][1]["id"], "ani7": sorted_ani_list[6][0],
                                                   "ani7_score": f"{(sorted_ani_list[6][1]['score'] / wanted_score) * 100:.5f}%", "ani7_pic": sorted_ani_list[6][1]["pic"],
                                                   "ani7_id": sorted_ani_list[6][1]["id"],
                                                   "ani8": sorted_ani_list[7][0], "ani8_score": f"{(sorted_ani_list[7][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani8_pic": sorted_ani_list[7][1]["pic"], "ani8_id": sorted_ani_list[7][1]["id"],
                                                   "ani9": sorted_ani_list[8][0],
                                                   "ani9_score": f"{(sorted_ani_list[8][1]['score'] / wanted_score) * 100:.5f}%", "ani9_pic": sorted_ani_list[8][1]["pic"],
                                                   "ani9_id": sorted_ani_list[8][1]["id"],
                                                   "ani10": sorted_ani_list[9][0], "ani10_score": f"{(sorted_ani_list[9][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani10_pic": sorted_ani_list[9][1]["pic"], "ani10_id": sorted_ani_list[9][1]["id"],
                                                    "ani11": sorted_ani_list[10][0],
                                                   "ani11_score": f"{(sorted_ani_list[10][1]['score'] / wanted_score) * 100:.5f}%", "ani11_pic": sorted_ani_list[10][1]["pic"],
                                                   "ani11_id": sorted_ani_list[10][1]["id"],
                                                   "ani12": sorted_ani_list[11][0], "ani12_score": f"{(sorted_ani_list[11][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani12_pic": sorted_ani_list[11][1]["pic"], "ani12_id": sorted_ani_list[11][1]["id"],
                                                   "ani13": sorted_ani_list[12][0],
                                                   "ani13_score": f"{(sorted_ani_list[12][1]['score'] / wanted_score) * 100:.5f}%", "ani13_pic": sorted_ani_list[12][1]["pic"],
                                                   "ani13_id": sorted_ani_list[12][1]["id"],
                                                   "ani14": sorted_ani_list[13][0], "ani14_score": f"{(sorted_ani_list[13][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani14_pic": sorted_ani_list[13][1]["pic"], "ani14_id": sorted_ani_list[13][1]["id"],
                                                   "ani15": sorted_ani_list[14][0],
                                                   "ani15_score": f"{(sorted_ani_list[14][1]['score'] / wanted_score) * 100:.5f}%", "ani15_pic": sorted_ani_list[14][1]["pic"],
                                                   "ani15_id": sorted_ani_list[14][1]["id"],
                                                   "ani16": sorted_ani_list[15][0], "ani16_score": f"{(sorted_ani_list[15][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani16_pic": sorted_ani_list[15][1]["pic"], "ani16_id": sorted_ani_list[15][1]["id"], "ani17": sorted_ani_list[16][0],
                                                   "ani17_score": f"{(sorted_ani_list[16][1]['score'] / wanted_score) * 100:.5f}%", "ani17_pic": sorted_ani_list[16][1]["pic"],
                                                   "ani17_id": sorted_ani_list[16][1]["id"],
                                                   "ani18": sorted_ani_list[17][0], "ani18_score": f"{(sorted_ani_list[17][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani18_pic": sorted_ani_list[17][1]["pic"], "ani18_id": sorted_ani_list[17][1]["id"],
                                                   "ani19": sorted_ani_list[18][0],
                                                   "ani19_score": f"{(sorted_ani_list[18][1]['score'] / wanted_score) * 100:.5f}%", "ani19_pic": sorted_ani_list[18][1]["pic"],
                                                   "ani19_id": sorted_ani_list[18][1]["id"],
                                                   "ani20": sorted_ani_list[19][0], "ani20_score": f"{(sorted_ani_list[19][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani20_pic": sorted_ani_list[19][1]["pic"], "ani20_id": sorted_ani_list[19][1]["id"],
                                                    "ani21": sorted_ani_list[20][0], "ani21_score": f"{(sorted_ani_list[20][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani21_pic": sorted_ani_list[20][1]["pic"],
                                                    "ani21_id": sorted_ani_list[20][1]["id"],
                                                    "ani22": sorted_ani_list[21][0], "ani22_score": f"{(sorted_ani_list[21][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani22_pic": sorted_ani_list[21][1]["pic"], "ani22_id": sorted_ani_list[21][1]["id"],
                                                    "ani23": sorted_ani_list[22][0], "ani23_score": f"{(sorted_ani_list[22][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani23_pic": sorted_ani_list[22][1]["pic"], "ani23_id": sorted_ani_list[22][1]["id"],
                                                    "ani24": sorted_ani_list[23][0], "ani24_score": f"{(sorted_ani_list[23][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani24_pic": sorted_ani_list[23][1]["pic"], "ani24_id": sorted_ani_list[23][1]["id"],
                                                    "ani25": sorted_ani_list[24][0], "ani25_score": f"{(sorted_ani_list[24][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani25_pic": sorted_ani_list[24][1]["pic"], "ani25_id": sorted_ani_list[24][1]["id"],
                                                    "ani26": sorted_ani_list[25][0], "ani26_score": f"{(sorted_ani_list[25][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani26_pic": sorted_ani_list[25][1]["pic"],
                                                    "ani26_id": sorted_ani_list[25][1]["id"], "ani27": sorted_ani_list[26][0],
                                                    "ani27_score": f"{(sorted_ani_list[26][1]['score'] / wanted_score) * 100:.5f}%", "ani27_pic": sorted_ani_list[26][1]["pic"],
                                                    "ani27_id": sorted_ani_list[26][1]["id"],
                                                    "ani28": sorted_ani_list[27][0], "ani28_score": f"{(sorted_ani_list[27][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani28_pic": sorted_ani_list[27][1]["pic"], "ani28_id": sorted_ani_list[27][1]["id"],
                                                    "ani29": sorted_ani_list[28][0], "ani29_score": f"{(sorted_ani_list[28][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani29_pic": sorted_ani_list[28][1]["pic"], "ani29_id": sorted_ani_list[28][1]["id"],
                                                    "ani30": sorted_ani_list[29][0], "ani30_score": f"{(sorted_ani_list[29][1]['score'] / wanted_score) * 100:.5f}%",
                                                    "ani30_pic": sorted_ani_list[29][1]["pic"], "ani30_id": sorted_ani_list[29][1]["id"]
                                                   })
    except KeyError:
        pass