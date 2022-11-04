import json
from datetime import datetime, timezone

# json file upload
with open("sample-data.json", 'r', encoding='utf-8') as file:
    container_data = json.load(file)

# dictionary for the desired data from the file
required_data = []

# # check for the presence of a second IP in the docker0
# def docker0_ip_check(list_d0):
#     if len(list_d0) == 2:
#         return list_d0[1]
#     else:
#         return None

for step in container_data:

    # find and convert human date to UTC
    human_date = step["created_at"]
    year, month = int(human_date[:4]), int(human_date[5:7])
    day, hour = int(human_date[8:10]), int(human_date[11:13])
    minutes, seconds = int(human_date[14:16]), int(human_date[17:19])

    date = datetime(year, month, day, hour, minutes, seconds)
    utc_timestamp = date.replace(tzinfo=timezone.utc).timestamp()

    try:
        try:
            # find name, cpu, memory usage, status, ip address
            name = step['name']
            cpu = step['state']['cpu']['usage']
            memory = step['state']['memory']['usage']
            status = step['state']['status']

            # find ip addresses of containers(eth0, lo, docker0)
            list_eth0 = []
            list_docker0 = []
            list_lo = []
            eth0 = step['state']['network']['eth0']['addresses']

            for e0 in eth0:
                list_eth0.append(e0['address'])
            docker0 = step['state']['network']['docker0']['addresses']

            for d0 in docker0:
                list_docker0.append(d0['address'])
            lo = step['state']['network']['lo']['addresses']
            for l in lo:
                list_lo.append(l['address'])

            # add data to list
            required_data.append(
                {
                    "name": name,
                    "cpu": cpu,
                    "memory": memory,
                    "created_at": utc_timestamp,
                    "status": status,
                    "ip_lo": list_lo,
                    "ip_eth0": list_eth0,
                    "ip_docker0": list_docker0
                }
            )
        except TypeError:
            pass
    except KeyError:
        pass
# data output to another json file for transfer to the database
with open("required_data.json", "a") as file:
    json.dump(required_data, file, indent=4, ensure_ascii=False)
