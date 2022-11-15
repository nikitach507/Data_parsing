import json
import time
from datetime import datetime, timezone
import psycopg2


start_time = time.time()
# json file upload
with open("sample-data.json", 'r', encoding='utf-8') as file:
    container_data = json.load(file)

# dictionary for the desired data from the file
required_data = []

number_of_containers = 1

# connect the code to the database
connection = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password=12345,
    host="0.0.0.0",
    port=5432
)

try:
    connection.autocommit = True

    # creating a table
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS data_container(
                id serial PRIMARY KEY,
                name_container varchar(50) NOT NULL,
                cpu varchar(2) NOT NULL,
                memory varchar(15) NOT NULL,
                created_at varchar(12) NOT NULL,
                status varchar(15) NOT NULL,
                ip_lo varchar(50),
                ip_eth0 varchar(350),
                ip_docker0 varchar(60));
                """
        )

        print("[INFO] Table created successfully")

    for step in container_data:
        # find and convert human date to UTC
        human_date = step["created_at"]
        year, month = int(human_date[:4]), int(human_date[5:7])
        day, hour = int(human_date[8:10]), int(human_date[11:13])
        minutes, seconds = int(human_date[14:16]), int(human_date[17:19])

        date = datetime(year, month, day, hour, minutes, seconds)
        utc_timestamp = date.replace(tzinfo=timezone.utc).timestamp()

        try:
            # find ip addresses of containers(eth0, lo, docker0)
            list_eth0, list_docker0, list_lo = [], [], []

            lo = step['state']['network']['lo']['addresses']
            for l in lo:
                list_lo.append(l['address'])

            eth0 = step['state']['network']['eth0']['addresses']
            for e0 in eth0:
                list_eth0.append(e0['address'])
            try:
                docker0 = step['state']['network']['docker0']['addresses']
                for d0 in docker0:
                    list_docker0.append(d0['address'])
            except KeyError:
                pass

            # add data to list
            required_data.append(
                {
                    "name": step['name'],
                    "cpu": step['state']['cpu']['usage'],
                    "memory": step['state']['memory']['usage'],
                    "created_at": utc_timestamp,
                    "status": step['state']['status'],
                    "ip_lo": list_lo,
                    "ip_eth0": list_eth0,
                    "ip_docker0": list_docker0
                }
            )
            # insert data into created table
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""INSERT INTO data_container VALUES (
                        '%s',
                        '{step['name']}',
                        '{step['state']['cpu']['usage']}',
                        '{step['state']['memory']['usage']}',
                        '{utc_timestamp}',
                        '{step['state']['status']}',
                        '{" / ".join(list_lo)}',
                        '{" / ".join(list_eth0)}',
                        '{" / ".join(list_docker0)}')""", number_of_containers
                )
            print(f" [+] Processed container: {number_of_containers}")
            number_of_containers += 1

        except TypeError:
            pass
    print(f"[INFO] The database 'data_container' has been created")

    # data output to another json file for transfer to the database
    with open("required_data.json", "a") as file:
        json.dump(required_data, file, indent=4, ensure_ascii=False)
        print(f"[INFO] required_data.json has been created")

# in case of error
except Exception as ex:
    print("[INFO] Error while working with PostgreSql", ex)
# termination of the connection
finally:
    if connection:
        connection.close()
        print("[INFO] PostgreSQL connection closed")
        finish_time = time.time() - start_time
        print(f"Time spent working: {finish_time}")