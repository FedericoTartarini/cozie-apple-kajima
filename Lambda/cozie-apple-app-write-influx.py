import influxdb_client
import time
from influxdb_client.client.write_api import SYNCHRONOUS
import json
from pprint import pprint
from datetime import datetime
import os
import requests


def check_type(key, value):
    # Fields with integer values
    int_fields = [
        "body_mass",
        "heart_rate",
        "ts_heartRate",
        "ts_oxygenSaturation",
        "ts_restingHeartRate",
        "ts_standTime",
        "ts_stepCount",
        "sound_pressure",
        "vote_count",
    ]

    # Fields with float values
    float_fields = [
        "latitude",
        "longitude",
        "ts_hearingEnvironmentalExposure",
        "ts_walkingDistance",
    ]

    if key in int_fields:
        return int(value)

    elif key in float_fields:
        return float(value)

    else:
        return value  # by default no changes are made to 'value'


token = os.environ["influxdb_token"]
org = os.environ["influxdb_org"]
url = "https://us-west-2-1.aws.cloud2.influxdata.com"
bucket = "cozie-apple-test"


def lambda_handler(event, context):

    # Forward request to node red
    try:
        node_red_url = "http://ec2-52-76-31-138.ap-southeast-1.compute.amazonaws.com:1880/cozie-apple-kajima"
        payload = json.loads(event["body"])
        response = requests.post(node_red_url, json=payload)
    except:
        print("Forward request to old Node-Red server failed.")

    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

    # this is the payload that arrives from the lambda function
    payload = json.loads(event["body"])
    #     print(payload)

    # Check for minimal presence of required fields/tags
    required_keys = ["id_participant", "timestamp_end"]
    for key_required in required_keys:
        if key_required not in payload:
            print(f"Either the {required_keys} were not in the payload")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": "Error: Required fields or tags ar missing",
            }
    # Get timestmap from call of lambda function
    timestamp_lambda = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Check for fields
    fields = {}
    json_body = []
    tags = ["id_participant", "id_device", "id_experiment", "timestamp_end"]

    for key in payload.keys():
        # Check if the key value is an integer or a float
        # print("# Key: ", key)
        if key in tags:
            # print('tag')
            pass
        elif key == "responses":
            # print("responses")
            for key_r in payload[key].keys():
                fields[key_r] = payload[key][key_r]
        elif key == "heart_rate" or "ts_" in key or key == "sound_pressure":  # in key:
            for key_ts in payload[key].keys():
                timestamp_ts = key_ts
                #                 print(
                #                     "key_ts: ",
                #                     key_ts,
                #                     "timestamp_ts: ",
                #                     timestamp_ts,
                #                     "timestamp_test",
                #                     int(time.time()),
                #                 )

                value_checked = check_type(key, payload[key][key_ts])

#                 json_body.append(
#                     {
#                         "time": timestamp_ts,  # XXX
#                         "measurement": payload["id_experiment"],
#                         "tags": {
#                             "id_participant": payload["id_participant"],
#                             "id_device": payload["id_device"],
#                         },
#                         "fields": {
#                             key: value_checked,
#                         },
#                     }
#                 )
        else:
            fields[key] = check_type(key, payload[key])

    fields["timestamp_lambda"] = timestamp_lambda
    json_body.append(
        {
            "time": payload["timestamp_end"],
            "measurement": payload["id_experiment"],
            "tags": {
                "id_participant": payload["id_participant"],
                "id_device": payload["id_device"],
            },
            "fields": fields,
        }
    )

    print({
                      "time": payload["timestamp_end"],
                      "measurement": payload["id_experiment"],
                      "tags": {
                          "id_participant": payload["id_participant"],
                          "id_device": payload["id_device"],
                      },
                      "fields": fields,
                  })

    #     print("##########################################################")
    #     print("json_body:")
    #     print(json.dumps(json_body, indent=4))

    write_api = client.write_api(write_options=SYNCHRONOUS)

    for point in json_body:
        print(f"point===== {point}")
        write_api.write(bucket=bucket, org=org, record=point)

    print("##########################################################")
    print("##########################################################")
    print("##########################################################")

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": "Success",
    }
