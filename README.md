# ShieldMaster 

**ShieldMaster is a machine learning-based incident management framework for securing small to medium-scale enterprise applications**. 

## Framework


![Proporsed HigheLevel Architecture of the System - Research drawio](https://github.com/Hemal99/Incident-Management-System/assets/58929178/3304e5bf-907b-427c-90cb-97b5d4e91b7f)

The ShieldMaster framework for incidents usually comprises the following components:


1. **Source Application:** Logs are generated at runtime of the application. 
2. **Log Shipper:** Using Filebeat as the log shipper.
3. **Elastic Search:** Indexing Logs and searching. 
4. **ShieldMaster API:**
      - API endpoint to retrieve the latest data periodically (as a cron job)
      - Log Parser (Pre-Processor)
      - Shield Master Intelligence - Detect anomalies and clustering algorithm to cluster IPs
  
(Note - Grafana is used as a synthetic user generation tool - HTTP monitoring)

## Install
```bash
git clone https://github.com/Hemal99/Incident-Management-System.git
cd Incident-Management-System
pip install -r requirements.txt
```

## ShieldMaster API

This API allows for log retrieval, parsing (pre-processing), and analysis capabilities.

## Folder Structure 

    .
    ├── app.py                   # To check the app is up and running
    ├── elastic_utils            # Retrieve data periodically from the ElasticSearch API 
    ├── Shield_ML                # Contains unsupervised ML models such as clustering and random forest to detect anomalies from the retrieved logs
    ├── shield_Parser            # Work as log pre-processor 
    ├── extracted_data           # Saves pre-processed data to this csv


## elastic_utils.py

This file contains functions to connect with Elastic Search and fetch the data we want to train our ML model.
Anyone using this repo can customize this query accordingly based on their requirement.
All the Environment variables are mentioned in the .env.example

```python
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
```

## shield_Parser

This will turn your logs into a usable format.

```python
# Retrieve the log pattern from environment variable
log_pattern_str = os.getenv("LOG_PATTERN")

# Compile the pattern
log_pattern = re.compile(log_pattern_str)
```
You can edit the "LOG_PATTERN" as required from the .env file 


## shield_ML

This file contains the ML models which is used to clustering and detecting anomalies from the pre processed logs 
The main function in here is structured as follows,

```python
def main():
    # Define the file path
    file_path = "extracted_data.csv"

    # Step 1: Read data
    df = read_data(file_path)

    # Step 2: Data Preprocessing
    df = data_preprocessing(df)

    # Step 3: One-Hot Encoding
    df = one_hot_encoding(df)

    # Step 4: Normalize Data
    df_norm = normalize_data(df)

    # Step 5: Perform KMeans Clustering
    clusters = perform_kmeans(df_norm)

    # Create a DataFrame with IP addresses and corresponding cluster results
    result_df = pd.DataFrame({"ip": df["clientip"].values, "result": clusters})

    # Assuming df_norm is your normalized DataFrame
    anomalies = detect_anomalies(df_norm)

    # Add the anomaly results to the result_df DataFrame
    result_df["anomaly"] = anomalies

    # Display instances identified as anomalies
    anomalies_df = result_df[result_df["anomaly"] == -1]
    print(anomalies_df)

    # Assuming result_df contains the clustering and anomaly results

    # visualize_anomalies(result_df)

    # Visualize the clustering results
    visualize_clusters(result_df, top_n=10)
```


1. `read_data(file_path)`: This function reads data from the specified file path (`file_path`). It likely uses a method from a library like pandas to read CSV data into a DataFrame.

2. `data_preprocessing(df)`: This function performs preprocessing on the DataFrame `df`. This could include tasks such as handling missing values, converting data types, filtering out irrelevant columns, or any other necessary data cleaning steps specific to the dataset.

3. `one_hot_encoding(df)`: This function performs one-hot encoding on categorical variables in the DataFrame `df`. One-hot encoding converts categorical variables into a binary matrix representation, where each category becomes a binary feature column. This is often done before applying machine learning algorithms that require numerical input.

4. `normalize_data(df)`: This function normalizes the numerical data in the DataFrame `df`. Normalization scales the numerical features to a uniform range, typically between 0 and 1 or -1 and 1, to ensure that features with larger scales do not dominate during model training.

5. `perform_kmeans(df_norm)`: This function performs K-means clustering on the normalized DataFrame `df_norm`. K-means clustering is an unsupervised machine learning algorithm that partitions data into `k` clusters based on similarity. It iteratively assigns data points to the nearest cluster centroid and updates the centroids until convergence.

6. `detect_anomalies(df_norm)`: This function detects anomalies in the normalized DataFrame `df_norm`. Anomalies are data points that deviate significantly from the rest of the data and may indicate unusual behavior or errors. The specific method for detecting anomalies depends on the nature of the data and the problem domain.

7. `visualize_clusters(result_df, top_n=10)`: This function visualizes the clustering results stored in the DataFrame `result_df`. It likely uses a visualization library such as matplotlib or seaborn to create visualizations such as scatter plots or cluster plots. The `top_n` parameter specifies the number of top clusters to visualize.


## Future Works

1. I am attempting to leverage the functionalities available at https://logpai.com/.
2. I am planning to integrate a data lake for storage purposes (ex - Snowflakes).
3. The repository for future work can be found at https://github.com/Hemal99/Shield-Master.


    





