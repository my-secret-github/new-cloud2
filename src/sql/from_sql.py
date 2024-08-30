import pymysql


def input_query(query):
            
    connection = pymysql.connect(
        host='35.222.24.104',
        user='root',
        password='j}(biN#qCJkt(|tK',
        database='amora_general',
        port=3306
    )

    cursor = connection.cursor()

    try:
        cursor.execute(query)
        list = cursor.fetchall()
        result = []
        for value in list:
            result.append(value)
        

        return list

    except Exception as e :
        print("exception: ", e)


    finally:
        connection.close()

