from datetime import datetime
import psycopg2

print(datetime.today().date())

connection = psycopg2.connect(
    database="TG_DB",
    user="postgres",
    password="123",
    host="localhost",
    port="5432"
)


print(connection)
cursor = connection.cursor()
query = "SELECT * FROM public.\"MediaIds\""
cursor.execute(query)

random_record = cursor.fetchone()

connection.close()
print(random_record)
