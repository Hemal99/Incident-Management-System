import re
from datetime import datetime
import csv

from elasticData import fetch_messages_from_elasticsearch

def extract_information_from_message(log_message):
    log_pattern = re.compile(r'(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[error\] \d+#\d+: \*(?P<error_code>\d+) .*?client: (?P<client_ip>[\d\.]+), server: (?P<server_name>\S+), request: "(?P<request_method>\S+) (?P<request_uri>\S+) HTTP/\d\.\d", upstream: "(?P<upstream>.*?)", host: "(?P<host>\S+)"')
    match = log_pattern.search(log_message)

    if match:
        timestamp_str = match.group('timestamp')
        timestamp = datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S')
        error_code = match.group('error_code')
        client_ip = match.group('client_ip')
        server_name = match.group('server_name')
        request_method = match.group('request_method')
        request_uri = match.group('request_uri')
        upstream = match.group('upstream')
        host = match.group('host')

        return {
            "Timestamp": timestamp,
            "Error Code": error_code,
            "Client IP": client_ip,
            "Server Name": server_name,
            "Request Method": request_method,
            "Request URI": request_uri,
            "Upstream": upstream,
            "Host": host
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

    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(extracted_data)

    print(f"CSV file '{csv_file_path}' created successfully.")
else:
    print("Failed to fetch messages from Elasticsearch.")
