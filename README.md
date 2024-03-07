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


## ShieldMaster API

This API allows for log retrieval, parsing (pre-processing), and analysis capabilities.

## Folder Structure 

    .
    ├── app.py                   # To check the app is up and running
    ├── elastic_utils            # Retrieve data periodically from the ElasticSearch API 
    ├── Shield_ML                # Contains unsupervised ML models such as clustering and random forest to detect anomalies from the retrieved logs
    ├── shield_Parser            # Work as log pre-processesor 
    ├── extracted_data           # Saves pre-processed data to this csv


## elastic_utils 


    





