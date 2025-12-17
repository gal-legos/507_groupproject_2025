# 507 Group Project 
This project analyzes real-world collegiate athletics performance data using Python, SQL, and data visualization techniques. The dataset integrates metrics from three athlete monitoring systems—Hawkins force plates, Kinexon GPS/accelerometry, and Vald strength testing—into a single relational database. The goal of this project is to explore, clean, transform, and analyze longitudinal performance data to answer a research-driven question grounded in sports science literature and to translate findings into practical performance-monitoring tools for coaches and trainers.


## Team member names and roles 

#### Ezzah Asad

#### Huma Babar

#### Patrick Brennan
Responsible for creating and fixing errors in the part2_cleaning.py file and participated in checking the part1_exploration.py file. Researched and gathered sources regarding the propulsive phase(s) metric, wrote the portion of the literatture review regarding the metric. Finally, wrote the methods section of the synthesis paper and created extra tables using scatter plots for the presentation (outside scope of project assignment).

#### Avion Christie
Responsible for selecting and analyzing the Average Braking Force metric and helping develop the data cleaning and flagging logic used in the project. Wrote and tested Python code in Google Colab to filter athlete data, calculate individual baselines, compare performance to team averages, and identify potential performance flags. When some metrics did not consistently appear across environments, worked with teammates to adapt the analysis to the finalized group code. Also contributed to the written report by writing the Average Braking Force literature section and the Limitations section, focusing on data constraints and interpretation, as well as helping explain performance monitoring and flagging results in the slides.

#### Emily Gallegos
Responsible for the part3_viz_dashboard and part3_viz_comparison notebook files. Other major responsibilities included the results section of the Sports Analytics Presentation and the Discussion portion of the synthesis paper. Minor responsibilities included compiling the part 1 summary and screenshots into a pdf file to make it readable for readers to access, as well as attaching the synthesis paper and literature review PDFs to the GitHub repository. 

## Setup Instructions (How to install dependencies)
1. Create a GitHub Repository
2. Set up a virtual environment (cmd+shift+P on Mac)
3. Either manually input dependencies or use the command 'pip3 install -r requirements.txt' to install dependencies from the requirements file.
4. Add the virtual environment to the gitignore file.
5. Configure environment variables
6. Ensure no secrets are being committed to the repository. 

## How to run each script 
script running steps needed 

## Database connection instructions 
1. Use the .env.examle file to copy and paste the database connection structure.  
2. Fill in database credentials 
3. 

## Project Structure overview
The sports analytics project followed the assignment folder structure that was provided to us in the project guidelines. Our project structure was adjusted and included splitting up the dashboard and comparison portion of part 3, as shown below.

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


