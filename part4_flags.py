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
    "Avg. Propulsive Force(N)"
]

# Apply filter
df = df[df["metric"].isin(selected_metrics)]

# Convert timestamp to datetime and sort by player, metric, timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(["playername", "metric", "timestamp"])

# Keep latest value per player per metric
latest_df = df.groupby(["playername", "metric"]).last().reset_index()

# Calculate baseline
baseline_df = df.groupby(["playername", "metric"])["value"].first().reset_index().rename(columns={"value": "baseline"})
latest_df = latest_df.merge(baseline_df, on=["playername", "metric"], how="left")


# Calculate team mean and std (based on all data)
team_stats = df.groupby(["team", "metric"])["value"].agg(["mean", "std"]).reset_index()
team_stats = team_stats.rename(columns={"mean": "team_mean", "std": "team_std"})
latest_df = latest_df.merge(team_stats, on=["team", "metric"], how="left")

# Flagging conditions
latest_df["decline_flag"] = latest_df["value"] < (latest_df["baseline"] * (1 - JUMP_DECLINE_PCT))
latest_df["team_sd_flag"] = latest_df["value"] < (latest_df["team_mean"] - TEAM_LOW_SD * latest_df["team_std"])
latest_df["days_since_test"] = (today - latest_df["timestamp"]).dt.days
latest_df["no_test_30_flag"] = latest_df["days_since_test"] > MAX_DAYS

# Combine all flags
latest_df["RED_FLAG"] = latest_df[["decline_flag", "team_sd_flag", "no_test_30_flag"]].any(axis=1)

# Output red flags
red_flags = latest_df[latest_df["RED_FLAG"]]
red_flags.to_csv("athlete_metric_red_flags.csv", index=False)

# Print summary
num_players = red_flags["playername"].nunique()
print(f"Red flag file created: athlete_metric_red_flags.csv")
print(f"Total Players Identified with Red Flags: {num_players}")