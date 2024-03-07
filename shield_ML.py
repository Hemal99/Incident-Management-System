# Import necessary libraries
import pandas as pd
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import seaborn as sns


def read_data(file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    return df


def detect_anomalies(df_norm, contamination=0.05):
    # Train Isolation Forest model
    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(df_norm)

    # Predict anomalies
    anomalies = model.predict(df_norm)
    return anomalies


def visualize_anomalies(df):
    plt.figure(figsize=(12, 8))

    # Get the top 5 IP addresses based on the total count of occurrences
    top5_ips = df["ip"].value_counts().nlargest(5).index

    # Filter the DataFrame to include only the top 5 IPs
    df_top5 = df[df["ip"].isin(top5_ips)]

    # Plot counts of clustering results
    # sns.countplot(x="ip", hue="result", data=df_top5, palette="Set1")

    # Highlight anomalies in red
    sns.countplot(x="ip", hue="anomaly", data=df_top5, palette="Reds", alpha=0.7)

    plt.title("Results and Anomalies for Top 5 IPs")
    plt.xlabel("IP")
    plt.ylabel("Count")
    plt.legend(title="Legend", loc="upper right", labels={1: "Normal", -1: "Anomaly"})
    plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
    plt.show()


def visualize_clusters(df, top_n=5):
    # Plotting the clusters using a scatter plot
    plt.figure(figsize=(10, 6))
    top_ips = df["ip"].value_counts().nlargest(top_n)
    top_ips.plot(kind="barh", color=sns.color_palette("Dark2"))
    plt.gca().spines[["top", "right"]].set_visible(False)
    plt.xlabel("Count")
    plt.ylabel("IP")
    plt.title(f"Top {top_n} Occurrence Count by IP")
    plt.show()


def data_preprocessing(df):
    # Drop unnecessary columns
    df.drop(["timestamp", "referrer", "request"], axis=1, inplace=True)

    # Remove rows with clientip as "127.0.0.1"
    df = df[df.clientip != "127.0.0.1"]

    # Fill missing values
    df["geoip.country_code3"].fillna("unknown", inplace=True)
    df["httpversion"].fillna("error", inplace=True)

    # Update geoip.country_code3 based on frequency
    freq = df["geoip.country_code3"].value_counts()
    cond = freq < 300
    mask_obs = freq[cond].index
    mask_dict = dict.fromkeys(mask_obs, "others")
    df["geoip.country_code3"] = df["geoip.country_code3"].replace(mask_dict)

    # Update useragent.device based on frequency
    freq = df["useragent.device"].value_counts()
    cond = freq < 300
    mask_obs = freq[cond].index
    mask_dict = dict.fromkeys(mask_obs, "others")
    df["useragent.device"] = df["useragent.device"].replace(mask_dict)

    return df


def one_hot_encoding(df):
    # Perform one-hot encoding
    df = pd.get_dummies(
        df,
        columns=[
            "geoip.country_code3",
            "httpversion",
            "response",
            "useragent.device",
            "verb",
        ],
        drop_first=True,
    )
    return df


def normalize_data(df):
    # Exclude non-numeric columns from normalization
    non_numeric_cols = ["clientip"]
    numeric_cols = [col for col in df.columns if col not in non_numeric_cols]

    # Normalize the data for numeric columns
    x = df[numeric_cols].values
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)

    # Create a DataFrame with the normalized values
    df_norm = pd.DataFrame(x_scaled, columns=numeric_cols)

    return df_norm


def perform_kmeans(df_norm, n_clusters=4):
    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(df_norm)
    return kmeans.predict(df_norm)


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

    # Display the results
    # print(result_df[result_df["result"] == 1])
    # print(result_df[result_df["result"] == 0])


if __name__ == "__main__":
    main()
