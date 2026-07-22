from django.db import connection


FORBIDDEN = [

"INSERT",

"UPDATE",

"DELETE",

"DROP",

"ALTER",

"CREATE",

"TRUNCATE",

"PRAGMA",

"ATTACH",

"DETACH"

]


def execute_sql(sql):

    sql_upper = sql.upper()

    if not sql_upper.startswith("SELECT"):
        raise Exception("Only SELECT queries are allowed.")

    if ";" in sql[:-1]:
        raise Exception("Multiple queries not allowed.")

    for word in FORBIDDEN:

        if word in sql_upper:
            raise Exception("Unsafe SQL.")

    with connection.cursor() as cursor:

        cursor.execute(sql)

        columns = [c[0] for c in cursor.description]

        rows = cursor.fetchall()

    result = []

    for row in rows:

        result.append(dict(zip(columns,row)))

    return result