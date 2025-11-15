from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine, text
import pymysql
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats 
from sqlalchemy.exc import OperationalError, ProgrammingError 
from datetime import datetime, timedelta


load_dotenv('test.env')
load_dotenv('test.env', override=True)

sql_username = os.getenv('DB_USER')
sql_password = os.getenv('DB_PASSWORD')
sql_host = os.getenv('DB_HOST')
sql_database = os.getenv('DB_NAME')

sql_username

# with SSL off

url_string = f"mysql+pymysql://{sql_username}:{sql_password}@{sql_host}:3306/{sql_database}"

conn = create_engine(url_string)

# query by selected metric 

query = text(f"""SELECT playername, team, timestamp, metric, value
FROM research_experiment_refactor_test
WHERE metric LIKE '%Avg. Propulsive Force(N)%'
ORDER BY playername, timestamp;
""")

query_response = pd.read_sql(query, conn)
query_response['value'] = pd.to_numeric(query_response['value'], errors='coerce')
print(query_response) 

# pivot table to see info
df = pd.read_sql(query, conn)
pivot_df = pd.pivot_table(
    df,
    values='value',
    index=['playername', 'team'],
    columns='metric',
    aggfunc='first'
)
print(pivot_df)


# 2.1 Calculate missing data (including 0s & blanks) for selected metrics
metrics = (
    "'Jump Height(m)', "
    "'Avg. Braking Force(N)', "
    "'Avg. Propulsive Force(N)', "
    "'Peak Velocity(m/s)', "
    "'Peak Propulsive Force(N)'"
)

query_nulls = text(f"""
    SELECT 
        metric,
        SUM(CASE 
            WHEN value IS NULL OR value = 0 OR TRIM(value) = '' THEN 1 
            ELSE 0 
        END) AS null_like_count,
        COUNT(*) AS total_count,
        ROUND(
            SUM(CASE 
                WHEN value IS NULL OR value = 0 OR TRIM(value) = '' THEN 1 
                ELSE 0 
            END) / COUNT(*) * 100, 2
        ) AS percent_missing
    FROM research_experiment_refactor_test
    WHERE metric IN ({metrics})
    GROUP BY metric
    ORDER BY metric;
""")

null_counts_df = pd.read_sql(query_nulls, conn)

print("\n--- Missing Data Summary (including 0s & blanks) ---")
print(null_counts_df)


# 2.1 For each sport/team, calculate what percentage of athletes have at least 5 measurements for your selected metrics

# Selected metrics
metrics = [
    "Jump Height(m)",
    "Avg. Braking Force(N)",
    "Avg. Propulsive Force(N)",
    "Peak Velocity(m/s)",
    "Peak Propulsive Force(N)"
]

results = []

for metric in metrics:
    print(f"Processing: {metric}")

    # Query only the selected metric
    query = f"""
        SELECT playername
        FROM research_experiment_refactor_test
        WHERE metric = '{metric}';
    """

    df = pd.read_sql(query, conn)

    if df.empty:
        results.append([metric, 0, 0, 0])
        print(f"No data found for {metric}\n")
        continue

    # Count measurements per athlete
    counts = df.groupby("playername").size()

    # Number with at least 5 measurements
    num_eligible = (counts >= 5).sum()

    # Total number of athletes with any data
    total_ids = counts.size

    # Percentage
    percentage = (num_eligible / total_ids) * 100

    results.append([metric, num_eligible, total_ids, percentage])

# Convert to DataFrame for a clean table
results_df = pd.DataFrame(
    results,
    columns=["Metric", "Athletes ≥5 Measurements", "Total Athletes", "Percentage (%)"]
)

print("\n=== Percentage of Athletes With ≥5 Measurements Per Metric ===")
print(results_df)



# 2.1 Identify athletes who haven't been tested in the last 6 months (for your selected metrics)

# Selected metrics
metrics = (
    "'Jump Height(m)', "
    "'Avg. Braking Force(N)', "
    "'Avg. Propulsive Force(N)', "
    "'Peak Velocity(m/s)', "
    "'Peak Propulsive Force(N)'"
)

# Step 1: Pull only the selected metrics
query = f"""
    SELECT playername, timestamp, metric
    FROM research_experiment_refactor_test
    WHERE metric IN ({metrics})
"""

df = pd.read_sql(query, conn)

# Convert timestamp column to actual datetime
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# Step 2: Define the cutoff date (6 months ago) 
six_months_ago = datetime.now() - timedelta(days=180)

# Step 3: Find the most recent test date for each athlete 
last_test_dates = df.groupby("playername")["timestamp"].max()

# Step 4: Identify athletes NOT tested in the last 6 months
athletes_outdated = last_test_dates[last_test_dates < six_months_ago]

print("\n=== Athletes NOT Tested in the Last 6 Months ===")
print(athletes_outdated) 

# 2.1 Q4 will come back to this once we finalize metric list and research question(s)

# 2.2 Data transformation from long format to wide format for 3 athletes 
metrics = (
    "'Jump Height(m)', "
    "'Avg. Braking Force(N)', "
    "'Avg. Propulsive Force(N)', "
    "'Peak Velocity(m/s)', "
    "'Peak Propulsive Force(N)'"
)

long_to_wide_query = f"""SELECT timestamp, metric, value, device, session_type
FROM research_experiment_refactor_test
WHERE playername = 'PLAYER_001'
AND metric IN ({metrics})
ORDER BY timestamp, metric;
"""

long_to_wide_df = pd.read_sql(long_to_wide_query, conn) 
print("Long format data for PLAYER_001:")
print(long_to_wide_df)

# creating wide format 
wide_df = long_to_wide_df.pivot_table(
    index='timestamp',
    columns='metric',
    values='value',
    aggfunc='first'
)

print(wide_df)

# repeat for PLAYER_050
metrics = (
    "'Jump Height(m)', "
    "'Avg. Braking Force(N)', "
    "'Avg. Propulsive Force(N)', "
    "'Peak Velocity(m/s)', "
    "'Peak Propulsive Force(N)'"
)

long_to_wide_query_2 = f"""SELECT timestamp, metric, value, device, session_type
FROM research_experiment_refactor_test
WHERE playername = 'PLAYER_050'
AND metric IN ({metrics})
ORDER BY timestamp, metric;
"""

long_to_wide_2_df = pd.read_sql(long_to_wide_query_2, conn) 
print("Long format data for PLAYER_050:")
print(long_to_wide_2_df)

# creating wide format 
wide_2_df = long_to_wide_2_df.pivot_table(
    index='timestamp',
    columns='metric',
    values='value',
    aggfunc='first'
)

print(wide_2_df)


# repeat for PLAYER_100

metrics = (
    "'Jump Height(m)', "
    "'Avg. Braking Force(N)', "
    "'Avg. Propulsive Force(N)', "
    "'Peak Velocity(m/s)', "
    "'Peak Propulsive Force(N)'"
)

long_to_wide_query_3 = f"""SELECT timestamp, metric, value, device, session_type
FROM research_experiment_refactor_test
WHERE playername = 'PLAYER_100'
AND metric IN ({metrics})
ORDER BY timestamp, metric;
"""

long_to_wide_3_df = pd.read_sql(long_to_wide_query_3, conn) 
print("Long format data for PLAYER_100:")
print(long_to_wide_3_df)

# creating wide format 
wide_3_df = long_to_wide_3_df.pivot_table(
    index='timestamp',
    columns='metric',
    values='value',
    aggfunc='first'
)

print(wide_3_df)

# 2.3
######
# step 1 testing with selected metric 
query_jump = f"""
SELECT playername, team, metric, value
FROM research_experiment_refactor_test
WHERE metric = 'Jump Height(m)';
"""

df = pd.read_sql(query_jump, conn)

# Clean team names
df["clean_team"] = (
    df["team"]
    .astype(str)                                 
    .str.extract(r"Team:\s*([^,]+)")             
    [0]                                          
    .fillna("Unknown")
    .str.strip()
)


# Calculate mean per clean team
team_means_jump = df.groupby("clean_team")["value"].mean().reset_index()
team_means_jump.rename(columns={"value": "team_mean"}, inplace=True)

# Merge
df = df.merge(team_means_jump, on="clean_team", how="left")

# Percent difference
df["percent_diff"] = ((df["value"] - df["team_mean"]) / df["team_mean"]) * 100

print(df[["playername", "clean_team", "metric", "value", "team_mean", "percent_diff"]].head())

# step 4: find top 5 and bottom 5 performers 
# Sort by percent difference
df_sorted_jump = df.sort_values("percent_diff", ascending=False)

top_5_jump = df_sorted_jump.head(5)
bottom_5_jump = df_sorted_jump.tail(5)

print("Team Means jump:")
print(team_means_jump)

print("\nTop 5 Performers (Relative to Team Mean):")
print(top_5_jump[["playername", "team", "value", "percent_diff"]])

print("\nBottom 5 Performers (Relative to Team Mean):")
print(bottom_5_jump[["playername", "team", "value", "percent_diff"]])

# 2.3 repeating for other metrics 
query_braking_force = f"""
SELECT playername, team, metric, value
FROM research_experiment_refactor_test
WHERE metric = 'Avg. Braking Force(N)';
"""

df = pd.read_sql(query_braking_force, conn)

# Clean team names
df["clean_team"] = (
    df["team"]
    .astype(str)                                 
    .str.extract(r"Team:\s*([^,]+)")             
    [0]                                          
    .fillna("Unknown")
    .str.strip()
)


# Calculate mean per clean team
team_means_bf = df.groupby("clean_team")["value"].mean().reset_index()
team_means_bf.rename(columns={"value": "team_mean"}, inplace=True)

# Merge
df = df.merge(team_means_bf, on="clean_team", how="left")

# Percent difference
df["percent_diff"] = ((df["value"] - df["team_mean"]) / df["team_mean"]) * 100

print(df[["playername", "clean_team", "metric", "value", "team_mean", "percent_diff"]].head())

# step 4: find top 5 and bottom 5 performers 
# Sort by percent difference
df_sorted_bf = df.sort_values("percent_diff", ascending=False)

top_5_bf = df_sorted_bf.head(5)
bottom_5_bf = df_sorted_bf.tail(5)

print("Team Means BF:")
print(team_means_bf)

print("\nTop 5 Performers (Relative to Team Mean):")
print(top_5_bf[["playername", "team", "value", "percent_diff"]])

print("\nBottom 5 Performers (Relative to Team Mean):")
print(bottom_5_bf[["playername", "team", "value", "percent_diff"]])

# Avg. Propulsive Force(N)
query_avg_prop_force = f"""
SELECT playername, team, metric, value
FROM research_experiment_refactor_test
WHERE metric = 'Avg. Propulsive Force(N)';
"""

df = pd.read_sql(query_avg_prop_force, conn)

# Clean team names
df["clean_team"] = (
    df["team"]
    .astype(str)                                 
    .str.extract(r"Team:\s*([^,]+)")             
    [0]                                          
    .fillna("Unknown")
    .str.strip()
)


# Calculate mean per clean team
team_means_apf = df.groupby("clean_team")["value"].mean().reset_index()
team_means_apf.rename(columns={"value": "team_mean"}, inplace=True)

# Merge
df = df.merge(team_means_apf, on="clean_team", how="left")

# Percent difference
df["percent_diff"] = ((df["value"] - df["team_mean"]) / df["team_mean"]) * 100

print(df[["playername", "clean_team", "metric", "value", "team_mean", "percent_diff"]].head())

# step 4: find top 5 and bottom 5 performers 
# Sort by percent difference
df_sorted_apf = df.sort_values("percent_diff", ascending=False)

top_5_apf = df_sorted_apf.head(5)
bottom_5_apf = df_sorted_apf.tail(5)

print("Team Means APF:")
print(team_means_apf)

print("\nTop 5 Performers (Relative to Team Mean):")
print(top_5_apf[["playername", "team", "value", "percent_diff"]])

print("\nBottom 5 Performers (Relative to Team Mean):")
print(bottom_5_apf[["playername", "team", "value", "percent_diff"]])


# Peak Velocity(m/s)
query_peak_vel = f"""
SELECT playername, team, metric, value
FROM research_experiment_refactor_test
WHERE metric = 'Peak Velocity(m/s)';
"""

df = pd.read_sql(query_peak_vel, conn)

# Clean team names
df["clean_team"] = (
    df["team"]
    .astype(str)                                 
    .str.extract(r"Team:\s*([^,]+)")             
    [0]                                          
    .fillna("Unknown")
    .str.strip()
)


# Calculate mean per clean team
team_means_pv = df.groupby("clean_team")["value"].mean().reset_index()
team_means_pv.rename(columns={"value": "team_mean"}, inplace=True)

# Merge
df = df.merge(team_means_pv, on="clean_team", how="left")

# Percent difference
df["percent_diff"] = ((df["value"] - df["team_mean"]) / df["team_mean"]) * 100

print(df[["playername", "clean_team", "metric", "value", "team_mean", "percent_diff"]].head())

# step 4: find top 5 and bottom 5 performers 
# Sort by percent difference
df_sorted_pv = df.sort_values("percent_diff", ascending=False)

top_5_pv = df_sorted_pv.head(5)
bottom_5_pv = df_sorted_pv.tail(5)

print("Team Means PV:")
print(team_means_pv)

print("\nTop 5 Performers (Relative to Team Mean):")
print(top_5_pv[["playername", "team", "value", "percent_diff"]])

print("\nBottom 5 Performers (Relative to Team Mean):")
print(bottom_5_pv[["playername", "team", "value", "percent_diff"]])



# Peak Velocity(m/s)
query_peak_prop_f = f"""
SELECT playername, team, metric, value
FROM research_experiment_refactor_test
WHERE metric = 'Peak Velocity(m/s)';
"""

df = pd.read_sql(query_peak_prop_f, conn)

# Clean team names
df["clean_team"] = (
    df["team"]
    .astype(str)                                 
    .str.extract(r"Team:\s*([^,]+)")             
    [0]                                          
    .fillna("Unknown")
    .str.strip()
)


# Calculate mean per clean team
team_means_ppf = df.groupby("clean_team")["value"].mean().reset_index()
team_means_ppf.rename(columns={"value": "team_mean"}, inplace=True)

# Merge
df = df.merge(team_means_ppf, on="clean_team", how="left")

# Percent difference
df["percent_diff"] = ((df["value"] - df["team_mean"]) / df["team_mean"]) * 100

print(df[["playername", "clean_team", "metric", "value", "team_mean", "percent_diff"]].head())

# step 4: find top 5 and bottom 5 performers 
# Sort by percent difference
df_sorted_ppf = df.sort_values("percent_diff", ascending=False)

top_5_ppf = df_sorted_ppf.head(5)
bottom_5_ppf = df_sorted_ppf.tail(5)

print("Team Means PPF:")
print(team_means_ppf)

print("\nTop 5 Performers (Relative to Team Mean):")
print(top_5_ppf[["playername", "team", "value", "percent_diff"]])

print("\nBottom 5 Performers (Relative to Team Mean):")
print(bottom_5_ppf[["playername", "team", "value", "percent_diff"]])