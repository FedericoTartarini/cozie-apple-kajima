import json
import datetime
import pandas as pd
import influxdb_client
import os
import numpy as np


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


# Influx authentication
token = os.environ["influxdb_token"]
org = os.environ["influxdb_org"]
url = "https://us-west-2-1.aws.cloud2.influxdata.com"
bucket = "cozie-apple-test"


def lambda_handler(event, context):

    if len(event["queryStringParameters"]) == 0:
        print("query string parameter not defined")
        return {
            "statusCode": 400,
            "body": json.dumps(
                "Please indicate the experiment-id in the url"
            ),
        }

    if ("id_participant" not in event["queryStringParameters"]) or (
        "id_experiment" not in event["queryStringParameters"]
    ):
        print("ids not defined")
        return {
            "statusCode": 400,
            "body": json.dumps("participant_id or experiment_id not in url"),
        }
    else:
        measurement = event["queryStringParameters"]["id_experiment"]
        id_participant = event["queryStringParameters"]["id_participant"]

    # Select the number of weeks to query data: Default is 2 weeks
    if "weeks" in event["queryStringParameters"]:
        print("did not pass week number")
        weeks = float(event["queryStringParameters"]["weeks"])
    else:
        weeks = 2

    # Set time strings to query data from influx
    now = datetime.datetime.utcnow()  # Set time strings to query data from influx
    time_start = now - datetime.timedelta(weeks=weeks)  # Get the time x weeks ago

    # Limit start time of data to be retrieved
    # This hack is needed because some fault data was inserted on 29.03.2022. All
    # queries including data from data they return empty. The exact reason is unkown.
    influx_time_horizon = datetime.datetime.strptime(
        "30.08.2022, 00:00", "%d.%m.%Y, %H:%M"
    )
    if time_start < influx_time_horizon:
        time_start = influx_time_horizon

    from_time_str = time_start.strftime("%Y-%m-%dT%H:%M:%SZ")

    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()

    query = f"""from(bucket: "{bucket}")
     |> range(start: {from_time_str})
     |> filter(fn: (r) => r["id_participant"] == "{id_participant}")
     |> filter(fn: (r) => r._measurement == "{measurement}")
     |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
     |> keep(columns: ["_time","id_participant", "id_device", "vote_count"])"""

    df = query_api.query_data_frame(query, org=org)

    last_sync_timestamp = datetime.datetime.now().timestamp()

    try:
        # In order to keep the example on the website working and the app version from
        # the freelancers working there is some adjustment needed to the datetime-index
        # Ideally, the website and app are adapted in order to remove the following
        # lines. (Using the DataFrameClient instead of the InfluxDBClient might resolve
        # this issue)
        df["time"] = pd.to_datetime(df["_time"])
        df["time"] = df["time"].dt.tz_localize(None)
        df.index = df["time"]
        df = df.drop(["time"], axis=1)

        query = f"""from(bucket: "{bucket}")
         |> range(start: {from_time_str})
         |> filter(fn: (r) => r["id_participant"] == "{id_participant}")
         |> filter(fn: (r) => r._measurement == "{measurement}")
         |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
         |> keep(columns: ["_time", "heart_rate"])"""
        df_hr = query_api.query_data_frame(query, org=org)
        df_hr.dropna(inplace=True)
        last_sync_timestamp = (
            df_hr.sort_values("_time")["_time"]
            .values[-1]
            .astype("datetime64[s]")
            .astype("int")
        )

    # no data for that query were available
    except KeyError:
        df = pd.DataFrame()

    field1 = event["queryStringParameters"]
    field1["last_sync_timestamp"] = last_sync_timestamp

    json_df = df.drop(columns=["_time", "result", "table"]).to_json(orient="index")
    dict_df = json.loads(json_df)

    # hack for freelancesrs
    for key in dict_df:
        dict_df[key]["timestamp"] = key

    json_body = [
        field1,
        {"data": dict_df},
    ]
    print(f"number of surveys queried for that participant = {df.shape[0]}")
    print("------------------------")

    return {"statusCode": 200, "body": json.dumps(json_body, cls=NpEncoder)}
