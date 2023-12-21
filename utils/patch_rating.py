import os

import requests
import json

from requests.auth import HTTPBasicAuth

from zappa.asynchronous import task

from utils.get_rating_date import getratingdate

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@task
def patchrating(resno, line_no, rating, rest_api, uname, pswd):
    try:
        print("MODULE [patch_rating] RATING THE RESNO >>>>>>>>>>>>", resno)
        review_date = getratingdate()
        url = rest_api + resno
        if rating == "0":
            modified_rating = ""
        else:
            modified_rating = rating
        payload = json.dumps([
            {
                "path": "/customFieldGroups/r1hrmypad",
                "op": "ReplaceById",
                "value": {
                    "rowId": line_no,
                    "rating_fx": modified_rating,
                    "review_date_fx": review_date
                }
            }
        ])
        headers = {
            'Content-Type': 'application/json-patch+json'
        }
        response = requests.patch(url, headers=headers, data=payload, auth=HTTPBasicAuth(uname, pswd))
        print("MODULE [patch_rating] FUNCTION [patchrating] REVIEW DATE >>>>>>>>>>>>", review_date, "RESPONSE CODE >>>>>>>>>>>>", response.status_code)
        return response.status_code
    except BaseException as e:
        print("MODULE [patch_rating] EXCEPTION >>>>>>>>>>>>", e)
