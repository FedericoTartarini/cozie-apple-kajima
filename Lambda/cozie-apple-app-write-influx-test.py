import influxdb_client
import time
from influxdb_client.client.write_api import SYNCHRONOUS
import json
from pprint import pprint
from datetime import datetime

token = "XXX"
org = "XXX"
url = "https://us-west-2-1.aws.cloud2.influxdata.com"
bucket = "cozie-apple-test"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

message = {
    "body": '{"heart_rate":{"2022-09-26T08:06:00.483Z":70,"2022-09-26T08:07:00.483Z":57},"soundÍ_pressure":{"2022-09-26T08:06:00.483Z":70,"2022-09-26T08:07:00.483Z":58},"timestamp_location":"2022-09-26T08:07:00.483Z","timestamp_start":"2022-09-26T08:09:00.483Z","id_participant":"lamda_id_participant","id_device":"E7E3EB30-7AF7-4362-AAF4-F8DF9C0A38E1","id_experiment":"lambda_id_experiment","vote_count":5,"latitude":1.3273774028097676,"longitude":103.84081749857995,"body_mass":0,"responses":{"end":"Submit","clo":"Verylight","location-place":"Home","location-in-out":"Indoor","tc-preference":"Cooler","met":"Relaxing","any-change":"Yes"},"timestamp_end":"2022-09-26T08:16:00.483Z"}'
}

# this is the payload that arrives from the lambda function
payload = json.loads(message["body"])
pprint(payload)

timestamp_lambda = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

# Check for fields
fields = {}
json_body = []
tags = ["id_participant", "id_device", "id_experiment", "timestamp_end"]

for key in payload.keys():
    # Check if the key value is an integer or a float
    print("# Key: ", key)
    if key in tags:
        # print('tag')
        pass
    elif key == "responses":
        # print("responses")
        for key_r in payload[key].keys():
            fields[key_r] = payload[key][key_r]
        fields["vote_count"] = payload["vote_count"]
    elif key == "heart_rate" or "ts_" in key or key == "sound_pressure":  # in key:
        for key_ts in payload[key].keys():
            timestamp_ts = key_ts
            print(
                "key_ts: ",
                key_ts,
                "timestamp_ts: ",
                timestamp_ts,
                "timestamp_test",
                int(time.time()),
            )
            json_body.append(
                {
                    "time": timestamp_ts,  # XXX
                    "measurement": payload["id_experiment"],
                    "tags": {
                        "id_participant": payload["id_participant"],
                        "id_device": payload["id_device"],
                    },
                    "fields": {
                        key: payload[key][key_ts],
                        "timestamp_lambda": timestamp_lambda,
                    },
                }
            )

timestamp = payload["timestamp_end"]  # for debugging
fields["timestamp_lambda"] = timestamp_lambda
json_body.append(
    {
        "time": timestamp,
        "measurement": payload["id_experiment"],
        "tags": {
            "id_participant": payload["id_participant"],
            "id_device": payload["id_device"],
        },
        "fields": fields,
    }
)

print("##########################################################")
print("json_body:")
print(json.dumps(json_body, indent=4))

write_api = client.write_api(write_options=SYNCHRONOUS)

for point in json_body:
    pprint(point)
    write_api.write(bucket=bucket, org="t.hasama@kajima.com.sg", record=point)

query_api = client.query_api()

query = """from(bucket: "cozie-apple-test")
 |> range(start: -10d)
 |> filter(fn: (r) => r._measurement == "lambda_id_experiment")"""
tables = query_api.query(query, org="t.hasama@kajima.com.sg")

for table in tables:
    for record in table.records:
        print(record)
