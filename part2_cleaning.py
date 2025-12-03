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
    "'Propulsive Phase(s)', "
    "'Braking Phase(s)'"
)

# Create a dataframe for each of the selected metrics

jump_height_df = pd.read_sql(f"SELECT * FROM research_experiment_refactor_test WHERE metric = 'Jump Height(m)';", conn)
braking_force_df = pd.read_sql(f"SELECT * FROM research_experiment_refactor_test WHERE metric = 'Avg. Braking Force(N)';", conn)
propulsive_force_df = pd.read_sql(f"SELECT * FROM research_experiment_refactor_test WHERE metric = 'Avg. Propulsive Force(N)';", conn)
propulsive_phase_df = pd.read_sql(f"SELECT * FROM research_experiment_refactor_test WHERE metric = 'Propulsive Phase(s)';", conn)
braking_phase_df = pd.read_sql(f"SELECT * FROM research_experiment_refactor_test WHERE metric = 'Braking Phase(s)';", conn)

### IGNORE ###
"""
# export jump height dataframe to csv
jump_height_df.to_csv('jump_height_data.csv', index=False)

# export braking force dataframe to csv
braking_force_df.to_csv('braking_force_data.csv', index=False)

# export propulsive force dataframe to csv
propulsive_force_df.to_csv('propulsive_force_data.csv', index=False)

# export propulsive phase dataframe to csv
propulsive_phase_df.to_csv('propulsive_phase_data.csv', index=False)

# export braking phase dataframe to csv
braking_phase_df.to_csv('braking_phase_data.csv', index=False)
"""

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

# For the metrics listed above, create separate tables showing all measurements for each athlete

metric_names = [
    'Jump Height(m)',
    'Avg. Braking Force(N)',
    'Avg. Propulsive Force(N)',
    'Propulsive Phase(s)',
    'Braking Phase(s)'
]

# Dictionary to store dataframes
athletes_dfs = {}

for metric in metric_names:
    # Create variable name from metric (replace special chars with underscore)
    var_name = metric.replace('(', '').replace(')', '').replace(' ', '_').replace('.', '').lower()
    
    # SQL query to fetch data for this metric
    sql_query = f"""
    SELECT playername, team, timestamp, metric, value
    FROM research_experiment_refactor_test
    WHERE metric = '{metric}'
    ORDER BY playername, timestamp;
    """
    
    # Read SQL into dataframe
    df = pd.read_sql(sql_query, conn)
    
    # Store in dictionary
    athletes_dfs[var_name] = df
    
    # Also create as individual variable for backwards compatibility
    globals()[f"{var_name}_athletes_df"] = df

# Define each dataframe variable for easier access
jump_height_athletes_df = athletes_dfs['jump_heightm']
braking_force_athletes_df = athletes_dfs['avg_braking_forcen']
propulsive_force_athletes_df = athletes_dfs['avg_propulsive_forcen']
propulsive_phase_athletes_df = athletes_dfs['propulsive_phases']
braking_phase_athletes_df = athletes_dfs['braking_phases']

# Calculate the percent of athletes that have at least 5 measurements for each metric

# Get total athlete counts per team (once, reuse for all metrics)
total_athletes_sql = """
  SELECT team, COUNT(DISTINCT playername) AS total_athlete_count
  FROM research_experiment_refactor_test
  GROUP BY team;
  """

total_athletes = pd.read_sql(total_athletes_sql, conn)

total_athletes

# Dictionary to store percentage results for each metric
percentage_dfs = {}

# Run analysis for each metric
for metric in metric_names:
    # Create sanitized name for storage
    var_name = metric.replace('(', '').replace(')', '').replace(' ', '_').replace('.', '').lower()
    
    # Query: count players with >=5 measurements for this metric, aggregated per team
    metric_athletes_sql = f"""
      SELECT team, COUNT(*) AS players_with_5plus
      FROM (
        SELECT team, playername, COUNT(*) AS cnt
        FROM research_experiment_refactor_test
        WHERE metric = '{metric}'
        GROUP BY team, playername
        HAVING COUNT(*) >= 5
      ) AS sub
      GROUP BY team;
      """
    
    # Read query results
    metric_athletes = pd.read_sql(metric_athletes_sql, conn)
    
    # Merge team-level counts and compute percentage
    metric_percentage = pd.merge(
        total_athletes,
        metric_athletes,
        on='team',
        how='left'
    )
    
    # Fill teams with zero qualifying players
    metric_percentage['players_with_5plus'] = metric_percentage['players_with_5plus'].fillna(0).astype(int)
    
    # Percentage (rounded to 2 decimals)
    metric_percentage['percentage_with_5_measurements'] = (
        metric_percentage['players_with_5plus'] / metric_percentage['total_athlete_count'] * 100
    ).round(2)
    
    # Sort by percentage from largest to smallest
    metric_percentage = metric_percentage.sort_values('percentage_with_5_measurements', ascending=False).reset_index(drop=True)
    
    # Store in dictionary and as global variable
    percentage_dfs[var_name] = metric_percentage
    globals()[f"{var_name}_percentage"] = metric_percentage

# Define each percentage dataframe variable for easier access
jump_heightm_percentage = percentage_dfs['jump_heightm']
avg_braking_forcen_percentage = percentage_dfs['avg_braking_forcen']
avg_propulsive_forcen_percentage = percentage_dfs['avg_propulsive_forcen']
propulsive_phases_percentage = percentage_dfs['propulsive_phases']
braking_phases_percentage = percentage_dfs['braking_phases']

jump_heightm_percentage.head()

# Identify athletes who haven't been tested in the last 6 months (for your selected metrics)

six_months_ago = pd.Timestamp.now() - pd.DateOffset(months=6)

athletes_not_tested_sql = f"""
SELECT team, COUNT(DISTINCT playername) AS athletes_not_tested
FROM research_experiment_refactor_test
WHERE (playername, metric) IN (
  SELECT playername, metric
  FROM research_experiment_refactor_test
  WHERE metric IN ({metrics})
  GROUP BY playername, metric
  HAVING MAX(timestamp) < '{six_months_ago}'
)
GROUP BY team;
"""

athletes_not_tested_df = pd.read_sql(athletes_not_tested_sql, conn)

athletes_not_tested_df

# Is there enough data to compare the selected metrics across teams?

# Group athletes by team
athletes_by_team = propulsive_phase_athletes_df.groupby('team')
# View each team's athletes
for team_name, group in athletes_by_team:
    print(f"\n{team_name}:")
    print(group)

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
create_wide_df('PLAYER_741')

create_wide_df('PLAYER_469')

create_wide_df('PLAYER_1244')

# Create a df that lists the mean of each metric by team

metric_columns = {
    'Jump Height(m)': 'avg_jump_height',
    'Avg. Braking Force(N)': 'avg_braking_force',
    'Avg. Propulsive Force(N)': 'avg_propulsive_force',
    'Propulsive Phase(s)': 'avg_propulsive_phase',
    'Braking Phase(s)': 'avg_braking_phase'
}

# Dictionary to store each metric's team means
team_means_by_metric = {}

for metric, col_name in metric_columns.items():
    metric_sql = f"""
    SELECT team, AVG(value) AS {col_name}
    FROM research_experiment_refactor_test
    WHERE metric = '{metric}'
    GROUP BY team;
    """
    metric_team_mean = pd.read_sql(metric_sql, conn)
    team_means_by_metric[metric] = metric_team_mean
    print(metric_team_mean.head())

# Create individual variables for each metric's team means
team_means_jh = team_means_by_metric['Jump Height(m)']
team_means_bf = team_means_by_metric['Avg. Braking Force(N)']
team_means_pf = team_means_by_metric['Avg. Propulsive Force(N)']
team_means_pp = team_means_by_metric['Propulsive Phase(s)']
team_means_bp = team_means_by_metric['Braking Phase(s)']
team_means_jh.head()

# Calculate mean for individual athletes for each metric
metric_to_df = {
    'Jump Height(m)': jump_height_athletes_df,
    'Avg. Braking Force(N)': braking_force_athletes_df,
    'Avg. Propulsive Force(N)': propulsive_force_athletes_df,
    'Propulsive Phase(s)': propulsive_phase_athletes_df,
    'Braking Phase(s)': braking_phase_athletes_df,
}

metric_to_col = {
    'Jump Height(m)': 'avg_jump_height',
    'Avg. Braking Force(N)': 'avg_braking_force',
    'Avg. Propulsive Force(N)': 'avg_propulsive_force',
    'Propulsive Phase(s)': 'avg_propulsive_phase',
    'Braking Phase(s)': 'avg_braking_phase',
}

athlete_summaries = {}

for metric, df in metric_to_df.items():
    col_name = metric_to_col[metric]
    summ = (
        df.groupby(['playername', 'team'])
          .agg({'value': 'mean'})
          .rename(columns={'value': col_name})
          .reset_index()
    )
    # Drop rows with NaNs
    summ = summ.dropna(subset=[col_name])
    athlete_summaries[metric] = summ
    key = metric.replace('(', '').replace(')', '').replace(' ', '_').replace('.', '').lower()
    globals()[f"{key}_athlete_summary"] = summ

# Define individual athlete summary variables
athlete_summary_jh = athlete_summaries['Jump Height(m)']
athlete_summary_bf = athlete_summaries['Avg. Braking Force(N)']
athlete_summary_pf = athlete_summaries['Avg. Propulsive Force(N)']
athlete_summary_pp = athlete_summaries['Propulsive Phase(s)']
athlete_summary_bp = athlete_summaries['Braking Phase(s)']
athlete_summary_bp.head()

# Join team and athlete summaries to compare individuals to team averages

# Create dictionary to map metric names to athlete summary dataframes
metric_to_athlete_summary = {
    'Jump Height(m)': athlete_summary_jh,
    'Avg. Braking Force(N)': athlete_summary_bf,
    'Avg. Propulsive Force(N)': athlete_summary_pf,
    'Propulsive Phase(s)': athlete_summary_pp,
    'Braking Phase(s)': athlete_summary_bp,
}

metric_to_team_summary = {
    'Jump Height(m)': team_means_jh,
    'Avg. Braking Force(N)': team_means_bf,
    'Avg. Propulsive Force(N)': team_means_pf,
    'Propulsive Phase(s)': team_means_pp,
    'Braking Phase(s)': team_means_bp,
}

# Merge athlete-level means with combined team means

athlete_team_comparisons = {}

for metric in metric_names:
    athlete_df = metric_to_athlete_summary[metric]
    team_df = metric_to_team_summary[metric]
    
    merged_df = pd.merge(
        athlete_df,
        team_df,
        on='team',
        how='inner',
        suffixes=('_athlete', '_team')
    )
    
    athlete_team_comparisons[metric] = merged_df
    key = metric.replace('(', '').replace(')', '').replace(' ', '_').replace('.', '').lower()
    globals()[f"{key}_athlete_team_comparison"] = merged_df

# Define individual athlete-team comparison variables
athlete_team_comparison_jh = athlete_team_comparisons['Jump Height(m)']
athlete_team_comparison_bf = athlete_team_comparisons['Avg. Braking Force(N)']
athlete_team_comparison_pf = athlete_team_comparisons['Avg. Propulsive Force(N)']
athlete_team_comparison_pp = athlete_team_comparisons['Propulsive Phase(s)']
athlete_team_comparison_bp = athlete_team_comparisons['Braking Phase(s)']
athlete_team_comparison_bf.head()

# Using the individual athlete-team comparison tables, calculate percent difference from team mean for Jump Height



athlete_team_comparison_jh['percent_diff_from_team'] = (
    (athlete_team_comparison_jh['avg_jump_height_athlete'] - athlete_team_comparison_jh['avg_jump_height_team']) /
    athlete_team_comparison_jh['avg_jump_height_team']
) * 100

# Identify top 5 and bottom 5 performers relative to team mean
top_5 = athlete_team_comparison_jh.nlargest(5, 'percent_diff_from_team')
bottom_5 = athlete_team_comparison_jh.nsmallest(5, 'percent_diff_from_team')

# Combine results
performance_results = pd.concat([top_5, bottom_5])

performance_results

# Create z-scores for athlete propulsive forces within their teams
athlete_team_comparison_jh['z_score'] = athlete_team_comparison_jh.groupby('team')['avg_jump_height_athlete'].transform(
    lambda x: stats.zscore(x, nan_policy='omit')
)

athlete_team_comparison_jh