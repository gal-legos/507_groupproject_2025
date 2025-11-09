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

sql_toexecute = """
  select *
  from research_experiment_refactor_test
  limit 50;
  """

response = pd.read_sql(sql_toexecute, conn)
response.head()

## 1.2 Data Quality Assessment (Group)
# How many unique athletes are in the database?
unique_athletes_query = """
    SELECT COUNT(id) AS unique_athlete_count
    FROM research_experiment_refactor_test;
"""
unique_athletes_response = pd.read_sql(unique_athletes_query, conn)
unique_athlete_count = unique_athletes_response['unique_athlete_count'][0]
print(f"Number of unique athletes in the database: {unique_athlete_count}")

# How many different sports/teams are represented?
sports_teams_query = """SELECT COUNT(DISTINCT team) AS unique_team_count
FROM research_experiment_refactor_test;
"""
sports_teams_response = pd.read_sql(sports_teams_query, conn)
unique_team_count = sports_teams_response['unique_team_count'][0]
print(f"Number of different sports/teams represented: {unique_team_count}")

# What is the date range of available data?
sql = """
SELECT 
    MIN(`timestamp`) AS start_date,
    MAX(`timestamp`) AS end_date
FROM research_experiment_refactor_test;
"""
response = pd.read_sql(sql, conn)
print(response)

# Which data source (Hawkins/Kinexon/Vald) has the most records?
data_source_query = """
    SELECT data_source, COUNT(*) AS record_count
    FROM research_experiment_refactor_test
    GROUP BY data_source
    ORDER BY record_count DESC;
"""
data_source_response = pd.read_sql(data_source_query, conn)
print("Data source record counts:")
print(data_source_response)
most_records_source = data_source_response.iloc[0]
print(f"Data source with the most records: {most_records_source['data_source']} ({most_records_source['record_count']} records)")

# Are there any athletes with missing or invalid names?
missing_names_query = """
    SELECT *
    FROM research_experiment_refactor_test
    WHERE playername IS NULL OR playername = '';
"""
missing_names_response = pd.read_sql(missing_names_query, conn)
num_missing_names = len(missing_names_response)
print(f"Number of athletes with missing or invalid names: {num_missing_names}")
if num_missing_names > 0:
    print("Records with missing or invalid names:")
    print(missing_names_response)

# How many athletes have data from multiple sources (2 or 3 systems)?
multi_source_athletes_query = """
    SELECT playername, COUNT(DISTINCT data_source) AS data_source
    FROM research_experiment_refactor_test
    GROUP BY playername
    HAVING data_source >= 2;
"""
multi_source_athletes_response = pd.read_sql(multi_source_athletes_query, conn)
num_multi_source_athletes = len(multi_source_athletes_response)
print(f"Number of athletes with data from multiple sources: {num_multi_source_athletes}")
if num_multi_source_athletes > 0:
    print("Athletes with data from multiple sources:")
    print(multi_source_athletes_response)

## 1.3 Metric Discovery & Selection (Group)
# Lists the top 10 most common metrics for Hawkins data (filter by data_source = 'Hawkins')
top_hawkins_metrics_query = """
    SELECT metric, COUNT(*) AS metric_count
    FROM research_experiment_refactor_test
    WHERE data_source = 'Hawkins'
    GROUP BY metric
    ORDER BY metric_count DESC
    LIMIT 10;
"""
top_hawkins_metrics_response = pd.read_sql(top_hawkins_metrics_query, conn)
print("Top 10 most common metrics for Hawkins data:")
print(top_hawkins_metrics_response)

# Lists the top 10 most common metrics for Kinexon data (filter by data_source = 'Kinexon')
top_kinexon_metrics_query = """
    SELECT metric, COUNT(*) AS metric_count
    FROM research_experiment_refactor_test
    WHERE data_source = 'Kinexon'
    GROUP BY metric
    ORDER BY metric_count DESC
    LIMIT 10;
""" 
top_kinexon_metrics_response = pd.read_sql(top_kinexon_metrics_query, conn)
print("Top 10 most common metrics for Kinexon data:")
print(top_kinexon_metrics_response)

# Lists the top 10 most common metrics for Vald data (filter by data_source = 'Vald')
top_vald_metrics_query = """
    SELECT metric, COUNT(*) AS metric_count
    FROM research_experiment_refactor_test
    WHERE data_source = 'Vald'
    GROUP BY metric
    ORDER BY metric_count DESC
    LIMIT 10;
"""
top_vald_metrics_response = pd.read_sql(top_vald_metrics_query, conn)
print("Top 10 most common metrics for Vald data:")
print(top_vald_metrics_response)

# Identifies how many unique metrics exist across all data sources
unique_metrics_query = """
    SELECT COUNT(DISTINCT metric) AS unique_metric_count
    FROM research_experiment_refactor_test;
"""
unique_metrics_response = pd.read_sql(unique_metrics_query, conn)
unique_metric_count = unique_metrics_response['unique_metric_count'][0]
print(f"Number of unique metrics across all data sources: {unique_metric_count}")

