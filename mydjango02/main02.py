import sqlite3

# sql injection 공격 방어하기
query = "1' OR 1=1 --"  # 오류문법
# query = "악뮤"
print(" 검색어 : ", query)

connection = sqlite3.Connection("melon-20230906.sqlite3")
cursor = connection.cursor()
connection.set_trace_callback(print)

param = "%" + query + "%"
# sql = f"SELECT * FROM songs WHERE 가수 LIKE '{param}' OR 곡명 LIKE '{param}'"
sql = f"SELECT * FROM songs WHERE 가수 LIKE ? OR 곡명 LIKE ?"  # sql injection 공격 방어하기

cursor.execute(sql, [param, param])
# cursor.execute(sql)
# cursor.execute("SELECT * FROM songs")

column_names = [desc[0] for desc in cursor.description]
print(column_names)

song_list = cursor.fetchall()
print(" list size :", len(song_list))

for song_tuple in song_list:
    song_dict = dict(zip(column_names, song_tuple))
    print("{곡명} {가수}".format(**song_dict))
    # print(song_dict["곡명"], song_dict["가수"])
    print(song_dict)
#     print(song_tuple)

connection.close()
