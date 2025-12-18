# 507 Group Project 
This project analyzes real-world collegiate athletics performance data using Python, SQL, and data visualization techniques. The dataset integrates metrics from three athlete monitoring systems—Hawkins force plates, Kinexon GPS/accelerometry, and Vald strength testing—into a single relational database. The goal of this project is to explore, clean, transform, and analyze longitudinal performance data to answer a research-driven question grounded in sports science literature and to translate findings into practical performance-monitoring tools for coaches and trainers.


## Team member names and roles 

#### Ezzah Asad
Responsible for writing the Introduction section of the literature review and contributing to the background synthesis of performance monitoring concepts. Developed the `part3_viz_individual.ipynb` notebook to visualize individual athlete longitudinal performance trends across multiple metrics. Contributed to the literature review and results interpretation related to the Average Propulsive Force metric. Additionally, assisted with coordinating meeting times and communication among group members to support collaboration and timely project completion.

#### Huma Babar
Responsible for developing `part1_exploration.py`,`part1_summary.pdf`,`part4_flags.py` and `part4_flag_justification.pdf`. Also responsible for analyzing Jump Height (m) data and conducting background research to support the literature review and research report. Additionally, wrote the results section of the final report and coordinated meeting times with group members to support collaboration and project completion. Also contributed to the README.md file by adding in key details of the project set up/instructions. 

#### Patrick Brennan
Responsible for creating and fixing errors in the `part2_cleaning.py` file and participated in checking the `part1_exploration.py` file. Researched and gathered sources regarding the propulsive phase(s) metric, wrote the portion of the literatture review regarding the metric. Finally, wrote the methods section of the synthesis paper and created extra tables using scatter plots for the presentation (outside scope of project assignment).

#### Avion Christie
Responsible for selecting and analyzing the Average Braking Force metric and helping develop the data cleaning and flagging logic used in the project. Wrote and tested Python code in Google Colab to filter athlete data, calculate individual baselines, compare performance to team averages, and identify potential performance flags. When some metrics did not consistently appear across environments, worked with teammates to adapt the analysis to the finalized group code. Also contributed to the written report by writing the Average Braking Force literature section and the Limitations section, focusing on data constraints and interpretation, as well as helping explain performance monitoring and flagging results in the slides.

#### Emily Gallegos
Responsible for developing the `part3_viz_dashboard` and `part3_viz_comparison` Jupyter notebooks. Additional responsibilities included contributing to the Results section of the Sports Analytics presentation and the Discussion section of the research synthesis paper. This role also involved researching the Braking Phase (s) metric and collecting relevant sources for both the literature review and synthesis paper. Minor contributions included compiling the Part 1 summary and screenshots into a single, reader-friendly PDF, as well as uploading the final synthesis paper and literature review PDFs to the GitHub repository. Also contributed to the README.md file by adding in key details of the project set up/instructions. 

## Setup Instructions (How to install dependencies)
1. Create a GitHub Repository
2. Set up a virtual environment (cmd+shift+P on Mac)
3. Either manually input dependencies or use the command 'pip3 install -r requirements.txt' to install dependencies from the requirements file
4. Add the virtual environment to the gitignore file
5. Configure environment variables
6. Ensure no secrets are being committed to the repository 
##### Required Dependencies 
`sqlalchemy
pandas
pymysql
dotenv
seaborn
matplotlib
numpy
scipy
datetime`

## Database connection instructions 
1. Use the .env.example file to copy and paste the database connection structure  
2. Fill in database credentials 
4. Use a connection string to connect to the MySQL Database using SQLAlchemy

```python
from sqlalchemy import create_engine
import pandas as pd
import os

url_string = f"mysql+pymysql://{sql_username}:{sql_password}@{sql_host}:3306/{sql_database}"
conn = create_engine(url_string) 
```


## How to run each script 
### Part 1 
1. Place proper .env variable in 'load_dotenv()'
2. Ensure the required dependencies are loaded
3. Run 'python `part1_exploration.py` in the terminal  

### Part 2 
1. Set up .env with proper variables
2. Install modules from requirements.txt
If running whole file
3. Run `part2_cleaning.py` in terminal
If running specific sections
3. Import all dependencies
4. Establish connection to database
5. Run necessary code from top to bottom, ensuring all previous requirements are defined (strings, lists, dictionaries)


### Part 3 
1. Place the proper .env file path in load_dotenv()
2. Ensure all required environment variables are defined (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DB_TABLE)
3. Install required dependencies if not already installed
4. Import all necessary libraries and modules
5. Establish a database connection using SQLAlchemy
6. Define the list of performance metrics to be analyzed
7. Load metric-specific data from the database into pandas DataFrames
8. Combine all metrics into a single dataset for analysis
9. Identify the athlete with the highest number of recorded tests
10. Generate longitudinal time-series plots with rolling averages
11. Run python part3_visualization.py in the terminal


### Part 4 
1. Place proper .env variable in 'load_dotenv()'
2. Ensure the required dependencies are loaded
3. Run 'python `part4_flags.py` in the terminal  


## Project Structure overview
The sports analytics project used the folder structure provided in the assignment guidelines, with slight modifications. Specifically, the dashboard and comparison components of Part 3 were separated, as shown below.

```
507_groupproject_2025/
├──  507_presentation.pdf
├──  README.md
├──  athlete_metric_red_flags.csv
├──  part1_exploration.py
├──  part1_literature_review.pdf
├──  part1_summary.pdf
├──  part2_cleaning.py
├──  part3_viz_comparison.ipynb
├──  part3_viz_dashboard.ipynb
├──  part3_viz_individual.ipynb
├──  part4_flag_justification.pdf
├──  part4_flags.py
├──  part4_research_synthesis.pdf
├──  references.md
├──  requirements.txt
├──  screenshots
│ ├──  avion_access.png
│ ├──  emily_access.png
│ ├──  ezzah_access.jpeg
│ ├──  huma_access.png
│ ├──  patrick_access.png

```

