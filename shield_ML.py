# Import necessary libraries
import pandas as pd
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt
from ip2geotools.databases.noncommercial import DbIpCity
import folium


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


def visualize_clusters_most_occured(df, top_n=5):
    # Plotting the clusters using a bar chart

    top_ips = df["ip"].value_counts().nlargest(top_n)

    # Return the most occurred IP address
    most_occurred_ip = top_ips.idxmax()
    most_occurred_count = top_ips.max()
    return most_occurred_ip, most_occurred_count


def visualize_clusters_most_occured_map(df, top_n=5):
    # Get the top 5 most occurred IP addresses
    top_ips = df["ip"].value_counts().nlargest(top_n)

    # Initialize lists to store IP addresses and their counts
    most_occurred_ips = []
    most_occurred_counts = []

    # Iterate over the top IPs and extract IP addresses and counts
    for ip, count in top_ips.items():
        most_occurred_ips.append(ip)
        most_occurred_counts.append(count)

    return most_occurred_ips, most_occurred_counts


def get_details(ip):
    res = DbIpCity.get(ip, api_key="free")
    return res.latitude, res.longitude


def display_map(ip_list, count_list, most_occurred_ip):
    # Create a base map
    m = folium.Map(location=[0, 0], zoom_start=2)

    # Add markers for each IP address
    for ip, count in zip(ip_list, count_list):
        lat, lon = get_details(ip)
        # Check if the current IP address is the most occurred one
        if ip == most_occurred_ip:
            # Use a different color for the marker
            folium.Marker(
                location=[lat, lon],
                popup=f"IP: {ip}, Count: {count}",
                icon=folium.Icon(color="red"),
            ).add_to(m)
        else:
            folium.Marker(
                location=[lat, lon], popup=f"IP: {ip}, Count: {count}"
            ).add_to(m)

    # Display the map
    m.save("map.html")  # Save the map as an HTML file
    return m


def visualize_clusters_chart(df, top_n=5):
    # Plotting the clusters using a bar chart
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


def visualize_geo_locations(df):
    # Assuming df contains IP addresses and their corresponding countries

    # Load the world map shapefile
    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

    # Group the DataFrame by IP addresses and count their occurrences
    top_ips = df["ip"].value_counts().nlargest(10).index

    # Filter the DataFrame to include only the top 10 IPs
    df_top10 = df[df["ip"].isin(top_ips)]

    # Merge with the world map data to get geometry information
    merged = world.merge(
        df_top10, left_on="iso_a3", right_on="geoip.country_code3", how="left"
    )

    # Plot the world map
    ax = merged.plot(
        column="ip", cmap="Blues", figsize=(15, 10), legend=True, edgecolor="gray"
    )

    # Highlight the most occurred IP address with a different color
    most_occurred_ip = df["ip"].value_counts().idxmax()
    most_occurred_country = df[df["ip"] == most_occurred_ip][
        "geoip.country_code3"
    ].iloc[0]
    merged[merged["geoip.country_code3"] == most_occurred_country].plot(
        ax=ax, color="red"
    )

    plt.title("Top 10 IP Addresses Geo-Locations")
    plt.show()


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
    # most_occured_ip = visualize_clusters_most_occured(result_df, top_n=10)
    # print(most_occured_ip)

    # visualize_clusters_chart(result_df, top_n=10)
    # print("Visualizing Geo Locations" + df.columns)
    most_occurred_ips, most_occurred_counts = visualize_clusters_most_occured_map(
        result_df, top_n=5
    )

    # Get the most occurred IP address
    most_occurred_ip = most_occurred_ips[
        0
    ]  # Assuming the most occurred IP is the first in the list

    # Display the map with markers for these IP addresses, highlighting the most occurred one
    display_map(most_occurred_ips, most_occurred_counts, most_occurred_ip)


if __name__ == "__main__":
    main()
