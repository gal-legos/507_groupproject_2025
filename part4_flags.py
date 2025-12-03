from sqlalchemy import create_engine, text
import pandas as pd
import os
from dotenv import load_dotenv
import sqlalchemy
import pymysql
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from datetime import datetime

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

today = pd.to_datetime("today")

# Set threshold values 
JUMP_DECLINE_PCT = 0.10    # 10% decline
TEAM_LOW_SD = 1.5         # 1.5 SD below team avg
MAX_DAYS = 30             # 30 days since last test

# SQL query to pull needed data
query = """
SELECT
    id,
    playername,
    team,
    metric,
    value,
    timestamp
FROM research_experiment_refactor_test;
"""

df = pd.read_sql(query, conn)

# Filter to selected metrics
selected_metrics = [
    "Jump Height(m)",
    "Avg. Braking Force(N)",
    "Avg. Propulsive Force(N)",
    "Avg. Landing Force(N)",
    "Peak Propulsive Force(N)"
]

# Apply filter
df = df[df["metric"].isin(selected_metrics)]

# Convert timestamp to datetime and sort by player, metric, timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(["playername", "metric", "timestamp"])

# Calculate baseline
df["baseline"] = df.groupby(["playername", "metric"])["value"].transform("first")

# Calculate flag if value has declined more than 10% threshold from baseline
df["decline_flag"] = df["value"] < (df["baseline"] * (1 - JUMP_DECLINE_PCT))

# Calculate team mean and std dev for each metric
df["team_mean"] = df.groupby(["team", "metric"])["value"].transform("mean")
df["team_std"] = df.groupby(["team", "metric"])["value"].transform("std")

# Calculate flag if value is below team mean
df["team_sd_flag"] = df["value"] < (df["team_mean"] - TEAM_LOW_SD * df["team_std"])

# Calculate days since last test for each athlete and metric
last_test = df.groupby(["playername", "metric"])["timestamp"].transform("max")
df["days_since_test"] = (today - last_test).dt.days

# Flag if days since last test exceeds 30 days
df["no_test_30_flag"] = df["days_since_test"] > MAX_DAYS

# Combine flags to create a red flag indicator
df["RED_FLAG"] = (
    df["decline_flag"] |
    df["team_sd_flag"] |
    df["no_test_30_flag"]
)

# Output red flags to CSV
red_flags = df[df["RED_FLAG"] == True]
red_flags.to_csv("athlete_metric_red_flags.csv", index=False)

# Print confirmation message 
print("Red flag file created: athlete_metric_red_flags.csv")

# Summary of red flags
num_players = red_flags["playername"].nunique()

# Print total number of players with red flags
print(f" Total Players Identified with Red Flags: {num_players}")
