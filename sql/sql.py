import psycopg2


def get_random_record_from_postgres():
    connection = psycopg2.connect(
        database="TG_DB",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM public.\"MediaIds\" ORDER BY RANDOM() LIMIT 1")
    random_record = cursor.fetchone()

    connection.close()
    return random_record


