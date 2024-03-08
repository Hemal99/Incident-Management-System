import json
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

elk_url = os.getenv("ELK_URL")
elk_size = os.getenv("ELK_SIZE")
elk_range_gte = os.getenv("ELK_RANGE_GTE")
elk_range_lte = os.getenv("ELK_RANGE_LTE")
elk_query = os.getenv("ELK_QUERY")
elk_must_not = os.getenv("ELK_MUST_NOT")
elk_log_file_path = os.getenv("ELK_LOG_FILE_PATH")
elk_track_total_hits = os.getenv("ELK_TRACK_TOTAL_HITS")


def fetch_messages_from_elasticsearch():
    url = elk_url

    payload = {
        "track_total_hits": elk_track_total_hits,
        "size": elk_size,
        "query": {
            "bool": {
                "must": [],
                "filter": [
                    {
                        "multi_match": {
                            "type": "best_fields",
                            "query": elk_query,
                            "lenient": True,
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "format": "strict_date_optional_time",
                                "gte": elk_range_gte,
                                "lte": elk_range_lte,
                            }
                        }
                    },
                ],
                "should": [],
                "must_not": [{"match_phrase": {"log.file.path": elk_log_file_path}}],
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
