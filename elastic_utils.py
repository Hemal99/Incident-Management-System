import json
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

elk_url = os.getenv("ELK_URL")


def fetch_messages_from_elasticsearch():
    url = elk_url

    payload = {
        "track_total_hits": False,
        "size": 10000,
        "query": {
            "bool": {
                "must": [],
                "filter": [
                    {
                        "multi_match": {
                            "type": "best_fields",
                            "query": "wp-content",
                            "lenient": True,
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "format": "strict_date_optional_time",
                                "gte": "2023-11-23T18:30:00.000Z",
                                "lte": "2023-12-24T03:34:24.736Z",
                            }
                        }
                    },
                ],
                "should": [],
                "must_not": [{"match_phrase": {"log.file.path": "/var/log/syslog"}}],
            }
        },
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        json_response = json.loads(response.text)
        hits = json_response.get("hits", {}).get("hits", [])
        messages = [hit["_source"]["message"] for hit in hits]
        return messages
    else:
        print(f"Error: {response.status_code}\n{response.text}")
        return None
