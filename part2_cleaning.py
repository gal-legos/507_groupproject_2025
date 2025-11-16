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

load_dotenv()

sql_username = os.getenv('DB_USER')
sql_password = os.getenv('DB_PASSWORD')
sql_host = os.getenv('DB_HOST')
sql_database = os.getenv('DB_NAME')

url_string = f"mysql+pymysql://{sql_username}:{sql_password}@{sql_host}:3306/{sql_database}"

conn = create_engine(url_string)

# Define metrics of interest
metrics = (
    "'Jump Height(m)', "
    "'Avg. Braking Force(N)', "
    "'Avg. Propulsive Force(N)', "
    "'Avg. Landing Force(N)', "
    "'Peak Propulsive Force(N)'"
)

# Create a dataframe for each of the selected metrics

jump_height_df = pd.read_sql(f"SELECT * FROM research_experiment_refactor_test WHERE metric = 'Jump Height(m)';", conn)
braking_force_df = pd.read_sql(f"SELECT * FROM research_experiment_refactor_test WHERE metric = 'Avg. Braking Force(N)';", conn)
propulsive_force_df = pd.read_sql(f"SELECT * FROM research_experiment_refactor_test WHERE metric = 'Avg. Propulsive Force(N)';", conn)
landing_force_df = pd.read_sql(f"SELECT * FROM research_experiment_refactor_test WHERE metric = 'Avg. Landing Force(N)';", conn)
peak_propulsive_force_df = pd.read_sql(f"SELECT * FROM research_experiment_refactor_test WHERE metric = 'Peak Propulsive Force(N)';", conn)

landing_force_df

# export landing force dataframe to csv
landing_force_df.to_csv('landing_force_data.csv', index=False)

# Identify which of your selected metrics have the most NULL or zero values

null_metric_sql = f"""
SELECT metric, SUM(CASE WHEN value IS NULL OR value = 0 OR TRIM(value) = '' THEN 1 ELSE 0 END) AS null_count
FROM research_experiment_refactor_test
WHERE metric IN ({metrics})
GROUP BY metric
ORDER BY null_count DESC;
"""

null_metric_df = pd.read_sql(null_metric_sql, conn)

null_metric_df

# Table for 'Avg. Landing Force(N)'

landing_force_athletes_df = """
SELECT playername, team, timestamp, metric, value
FROM research_experiment_refactor_test
WHERE metric IN ('Avg. Landing Force(N)')
ORDER BY playername, timestamp;
"""

landing_force_athletes_df = pd.read_sql(landing_force_athletes_df, conn)

landing_force_athletes_df

# Calculate the percent of athletes that have at least 5 measurements for 'Avg. Landing Force' for each sports team

# Query: count players with >=5 landing-force measurements, aggregated per team
landing_force_athletes_sql = """
  SELECT team, COUNT(*) AS players_with_5plus
  FROM (
    SELECT team, playername, COUNT(*) AS cnt
    FROM research_experiment_refactor_test
    WHERE metric = 'Avg. Landing Force(N)'
    GROUP BY team, playername
    HAVING COUNT(*) >= 5
  ) AS sub
  GROUP BY team;
  """

landing_force_athletes = pd.read_sql(landing_force_athletes_sql, conn)

landing_force_athletes

# Get total athlete counts per team
total_athletes_sql = """
  SELECT team, COUNT(DISTINCT playername) AS total_athlete_count
  FROM research_experiment_refactor_test
  GROUP BY team;
  """

total_athletes = pd.read_sql(total_athletes_sql, conn)

# Merge team-level counts and compute percentage
landing_force_percentage = pd.merge(
    total_athletes,
    landing_force_athletes,
    on='team',
    how='left'
)

# Fill teams with zero qualifying players
landing_force_percentage['players_with_5plus'] = landing_force_percentage['players_with_5plus'].fillna(0).astype(int)

# Percentage (rounded to 2 decimals)
landing_force_percentage['percentage_with_5_measurements'] = (
    landing_force_percentage['players_with_5plus'] / landing_force_percentage['total_athlete_count'] * 100
).round(2)

landing_force_percentage


# Identify athletes who haven't been tested in the last 6 months (for your selected metrics)

six_months_ago = pd.Timestamp.now() - pd.DateOffset(months=6)

athletes_not_tested_sql = f"""
SELECT team, COUNT(DISTINCT playername) AS athletes_not_tested
FROM research_experiment_refactor_test
WHERE timestamp < '{six_months_ago}'
AND metric IN ({metrics})
GROUP BY team;
"""

athletes_not_tested_df = pd.read_sql(athletes_not_tested_sql, conn)

athletes_not_tested_df

# Is there enough data to compare the selected metrics across teams?

# Group athletes by team
athletes_by_team = landing_force_athletes.groupby('team')
# View each team's athletes
for team_name, group in athletes_by_team:
    print(f"\n{team_name}:")
    print(group)

# Create wide dataframe using SQL pivot

# Function to create wide dataframe from long format for specific player
def create_wide_df(player_name):

  wide_df_sql = f"""
  SELECT timestamp, metric, value
  FROM research_experiment_refactor_test
  WHERE metric IN ({metrics})
  AND playername = '{player_name}'
  ORDER BY timestamp, metric;
  """
  wide_df = pd.read_sql(wide_df_sql, conn)
  wide_player_df = wide_df.pivot(index='timestamp', columns='metric', values='value').reset_index()
  wide_player_df = wide_player_df.interpolate(method='linear')
  return wide_player_df

# Example usage for a specific player
create_wide_df('PLAYER_1208')

create_wide_df('PLAYER_570')

create_wide_df('PLAYER_338')

# get full table for landing force

landing_force_full_sql = """
SELECT *
FROM research_experiment_refactor_test
WHERE metric = 'Avg. Landing Force(N)';
"""

landing_force_full = pd.read_sql(landing_force_full_sql, conn)

landing_force_full

# Calculate mean by team
team_summary = landing_force_full.groupby('team').agg({
    'value': 'mean'  # Average landing force per team
}).rename(columns={'value': 'avg_landing_force'})

# Get rid of NaN values
team_summary = team_summary.dropna()

team_summary

# Calculate mean for individual athletes
athlete_summary = landing_force_full.groupby(['playername', 'team']).agg({
    'value': 'mean'  # Average landing force per athlete
}).rename(columns={'value': 'avg_landing_force'}).reset_index()

# Get rid of NaN values
athlete_summary = athlete_summary.dropna()

athlete_summary

# Join team and athlete summaries to compare individuals to team averages
athlete_team_comparison = pd.merge(
    athlete_summary,
    team_summary,
    on='team',
    how='left',
    suffixes=('_athlete', '_team')
)

athlete_team_comparison

# Calculate percent difference from team average
athlete_team_comparison['percent_diff_from_team'] = (
    (athlete_team_comparison['avg_landing_force_athlete'] - athlete_team_comparison['avg_landing_force_team']) /
    athlete_team_comparison['avg_landing_force_team']
) * 100

# Identify top 5 and bottom 5 performers relative to team mean
top_5 = athlete_team_comparison.nlargest(5, 'percent_diff_from_team')
bottom_5 = athlete_team_comparison.nsmallest(5, 'percent_diff_from_team')

# Combine results
performance_results = pd.concat([top_5, bottom_5])

performance_results

# Create z-scores for athlete landing forces within their teams
athlete_team_comparison['z_score'] = athlete_team_comparison.groupby('team')['avg_landing_force_athlete'].transform(
    lambda x: stats.zscore(x, nan_policy='omit')
)

athlete_team_comparison