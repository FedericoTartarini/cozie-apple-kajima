import requests
import json

# OneSignal credentials
token = "NDRkODliNWUtZjdlMy00YmU1LWI2M2YtN2I1MTAzOTg5ZjU3"  # Provided by OneSignal. Can be found on the Keys & IDs page on the OneSignal Dashboard for this particular app
app_id = "17d346bf-bfe5-4422-be96-2a8e4ae4cc3d"  # master

notification_headings = "Test heading"  # Can be empty string
notification_subtitle = "Test subtitle"  # Can be empty string
notification_message = "Test message from Google Colab"

user_ids = ["74d4aa23-43f2-4174-9e41-a9f3b814917d"]  # federico iPhone
header = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": "Basic " + token,
}

payload = {
    "app_id": app_id,
    "include_player_ids": user_ids,
    "contents": {"en": notification_message},
    "headings": {"en": notification_headings},
    "subtitle": {"en": notification_subtitle},
    "buttons": [
        {"id": "not_helpful", "text": "Not helpful"},
        {"id": "helpful", "text": "Helpful"},
    ],
}

req = requests.post(
    "https://onesignal.com/api/v1/notifications",
    headers=header,
    data=json.dumps(payload),
)

print("Response status code:", req.status_code)
print("Response reason: ", req.reason)
print("Response content: ", req.content)
content = json.loads(req.content)
print(content["recipients"])

# import requests
# import json
#
# token =  "YTVhY2NlOTMtY2Q3Zi00ZDY5LTg3NzAtMzNlYWJkMTQ4M2Jm" # Provided by OneSignal. Can be found on the Keys & IDs page on the OneSignal Dashboard for this particular app
# app_id = "4d2b287e-603c-47db-a2b8-80b2a5d93473" # Provided by OneSignal, needs to be implemented in the app
#
# notification_headings = "Test heading" # Can be empty string
# notification_subtitle = "Test subtitle" # Can be empty string
# notification_message = "Test message from Google Colab"
# user_ids = ["df9b27c4-79db-11ec-a062-e6dc1decf8dd"] # AW13:
# user_ids = ["5610c460-a103-11ec-86f3-ea3a56b367b9"] # AW14 / osk04 / Mario
# user_ids = ["ca716502-f03d-400b-ad26-18b7034eae54"] # AW14 / osk22 / Mario Cozie build 17
# user_ids = ["1a2ec8ba-2dfc-4247-ac6d-56c627780368"] # AW14 / osk23 / Mario Cozie build 18, attempt 2
# header = {"Content-Type": "application/json; charset=utf-8",
#           "Authorization": "Basic "+ token}
#
# payload = {"app_id": app_id,
#            "included_segments": ["All"],
#            "include_external_user_ids": user_ids,
#            "channel_for_external_user_ids": "push",
#            "contents": {"en": notification_message},
#            "headings": {"en": notification_headings},
#            "subtitle": {"en": notification_subtitle}
#            }
#
# req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
#
# print(req.status_code, req.reason)
# print(req.content)
