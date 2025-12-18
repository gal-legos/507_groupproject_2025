# 507 Group Project 
This project analyzes real-world collegiate athletics performance data using Python, SQL, and data visualization techniques. The dataset integrates metrics from three athlete monitoring systems—Hawkins force plates, Kinexon GPS/accelerometry, and Vald strength testing—into a single relational database. The goal of this project is to explore, clean, transform, and analyze longitudinal performance data to answer a research-driven question grounded in sports science literature and to translate findings into practical performance-monitoring tools for coaches and trainers.


## Team member names and roles 

#### Ezzah Asad

#### Huma Babar
Responsible for developing `part1_exploration.py` and creating `part1_summary.pdf`. Also responsible for analyzing Jump Height (m) data and conducting background research to support the literature review and research report. Additionally, wrote the results section of the final report and coordinated meeting times with group members to support collaboration and project completion. 

#### Patrick Brennan
Responsible for creating and fixing errors in the `part2_cleaning.py` file and participated in checking the `part1_exploration.py` file. Researched and gathered sources regarding the propulsive phase(s) metric, wrote the portion of the literatture review regarding the metric. Finally, wrote the methods section of the synthesis paper and created extra tables using scatter plots for the presentation (outside scope of project assignment).

#### Avion Christie
Responsible for selecting and analyzing the Average Braking Force metric and helping develop the data cleaning and flagging logic used in the project. Wrote and tested Python code in Google Colab to filter athlete data, calculate individual baselines, compare performance to team averages, and identify potential performance flags. When some metrics did not consistently appear across environments, worked with teammates to adapt the analysis to the finalized group code. Also contributed to the written report by writing the Average Braking Force literature section and the Limitations section, focusing on data constraints and interpretation, as well as helping explain performance monitoring and flagging results in the slides.

#### Emily Gallegos
Responsible for the `part3_viz_dashboard` and `part3_viz_comparison` notebook files. Other major responsibilities included the results section of the Sports Analytics Presentation and the Discussion portion of the synthesis paper. Minor responsibilities included compiling the part 1 summary and screenshots into a pdf file to make it readable for readers to access, as well as attaching the synthesis paper and literature review PDFs to the GitHub repository. 

## Setup Instructions (How to install dependencies)
1. Create a GitHub Repository
2. Set up a virtual environment (cmd+shift+P on Mac)
3. Either manually input dependencies or use the command 'pip3 install -r requirements.txt' to install dependencies from the requirements file
4. Add the virtual environment to the gitignore file
5. Configure environment variables
6. Ensure no secrets are being committed to the repository 


## Database connection instructions 
1. Use the .env.example file to copy and paste the database connection structure  
2. Fill in database credentials 
4. Use a connection string to connect to the MySQL Database using SQLAlchemy
 "from sqlalchemy import create_engine
import pandas as pd
import os

engine = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)"



## How to run each script 
### Part 1 
1. Open a new terminal 
2. Type 'python part1_exploration.py' into the terminal 
3.  

### Part 2 
1. Set up .env with proper variables
2. Install modules from requirements.txt
If running whole file
3. Run part2_cleaning.py in terminal
If running specific sections
3. Import all dependencies
4. Establish connection to database
5. Run necessary code from top to bottom, ensuring all previous requirements are defined (strings, lists, dictionaries)


### Part 3 
2. 


### Part 4 
3. 



## Project Structure overview
The sports analytics project used the folder structure provided in the assignment guidelines, with slight modifications. Specifically, the dashboard and comparison components of Part 3 were separated, as shown below.

```
507_groupproject_2025/
├── 507_presentation.pdf
├── README.md
├── athlete_metric_red_flags.csv
├── part1_exploration.py
├── part1_summary.pdf
├── part2_cleaning.py
├── part3_viz_comparison.ipynb
├── part3_viz_dashboard.ipynb
├── part3_viz_individual.ipynb
├── part4_flags.py
├── refernces.md
├── requirements.txt
├── screenshots
├── literature_review.pdf
├── part4_research_synthesis.pdf
├── 
├── 
├── 
├── 

```


