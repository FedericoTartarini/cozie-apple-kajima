import datetime
import influxdb_client

# Influx authentication
token = "XXXX"
org = "XXXX"
url = "https://us-west-2-1.aws.cloud2.influxdata.com"
bucket = "cozie-apple-test"
measurement = "lambda_id_experiment"
weeks = 2

# Set time strings to query data from influx
now = datetime.datetime.utcnow()  # Set time strings to query data from influx
time_start = now - datetime.timedelta(weeks=weeks)  # Get the time x weeks ago

# Limit start time of data to be retrieved
# This hack is needed because some fault data was inserted on 29.03.2022. All
# queries including data from data they return empty. The exact reason is unkown.
influx_time_horizon = datetime.datetime.strptime("30.08.2022, 00:00", "%d.%m.%Y, %H:%M")
if time_start < influx_time_horizon:
    time_start = influx_time_horizon

from_time_str = time_start.strftime("%Y-%m-%dT%H:%M:%SZ")

# section of the code run if query comes from the cozie apple app

# Influx client
client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

query = f"""from(bucket: "cozie-apple-test")
 |> range(start: -{weeks}w)
 |> filter(fn: (r) => r["id_participant"] == "lamda_id_participant")
 |> filter(fn: (r) => r._measurement == "lambda_id_experiment")
 |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") """

# print("query influx: ", query)
tables = query_api.query_data_frame(query, org="t.hasama@kajima.com.sg")
