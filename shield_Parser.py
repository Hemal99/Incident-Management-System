import re
from datetime import datetime
import csv

from elastic_utils import fetch_messages_from_elasticsearch
from geo_utils import get_details

from dotenv import load_dotenv
import os

load_dotenv()

# Retrieve the log pattern from environment variable
log_pattern_str = os.getenv("LOG_PATTERN")

# Compile the pattern
log_pattern = re.compile(log_pattern_str)


def extract_information_from_message(log_message):

    match = log_pattern.search(log_message)

    if match:
        timestamp_str = match.group("timestamp")
        timestamp = datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S %z")
        clientip = match.group("client_ip")
        request_method = match.group("request_method")
        request_uri = match.group("request_uri")
        http_version = match.group("http_version")
        response_code = match.group("response_code")
        bytes_sent = match.group("bytes_sent")
        referrer = match.group("referrer")
        user_agent = match.group("user_agent")
        # country_code = get_details(clientip) if clientip else ""

        return {
            "timestamp": timestamp,
            "clientip": clientip,
            "verb": request_method,
            "request": request_uri,
            "httpversion": http_version,
            "response": response_code,
            "bytes": bytes_sent,
            "referrer": referrer,
            "useragent.device": user_agent,
            "geoip.country_code3": "US",
        }
    else:
        return None


# Call the function to get messages
messages = fetch_messages_from_elasticsearch()

# Check if messages were fetched successfully
if messages:
    # Create a list to store extracted information
    extracted_data = []

    # Loop through messages and extract information
    for message in messages:
        extracted_info = extract_information_from_message(message)
        if extracted_info:
            extracted_data.append(extracted_info)

    # Write the extracted data to a CSV file
    csv_columns = extracted_data[0].keys() if extracted_data else []
    csv_file_path = "extracted_data.csv"

    with open(csv_file_path, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(extracted_data)

    print(f"CSV file '{csv_file_path}' created successfully.")
else:
    print("Failed to fetch messages from Elasticsearch.")
