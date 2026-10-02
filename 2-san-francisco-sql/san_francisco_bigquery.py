"""San Francisco in data: films, police incidents and fire calls, queried with SQL on Google BigQuery.

Code exported from san_francisco_bigquery.ipynb; see the notebook for outputs and charts.
"""

# %%
import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import bigquery
from sqlite3 import connect

# %%
# Construct a BigQuery client
my_project_name = "your-gcp-project-id" # fill in your project's name
client = bigquery.Client(project=my_project_name)

# %%
san_fan_films_locs = "bigquery-public-data.san_francisco.film_locations"
san_fan_service_reqs = "bigquery-public-data.san_francisco.311_service_requests"
san_fan_pd_incidents = "bigquery-public-data.san_francisco.sfpd_incidents"
san_fan_fd_incidents = "bigquery-public-data.san_francisco.sffd_service_calls"

# %%
# Define the SQL query for Q1.a
QUERY_1A = """
    SELECT * 
    FROM `bigquery-public-data.san_francisco.film_locations` 
    LIMIT 1000
"""

# Execute the query.
query_job_1a = client.query(QUERY_1A)
results_1a = query_job_1a.result()

# Print the first two rows of the results with a headline and a space below.
for index, row in enumerate(list(results_1a)[:2], start=1):
    print(f"Row {index} Output")
    print()  # Add an empty line for spacing.
    # Print each column in a row on a new line for clarity:
    for column, value in row.items():
        print(f"{column}: {value}")
    print("-----")  # Separator for clarity between rows

# %%
# Retrieve the schema from the query results for better understanding
results_1a = query_job_1a.result()
schema_data_1b = [field.name for field in results_1a.schema]

# Initialize an empty list to hold row data
rows_data_1b = []

# Iterate over the list of query results
for row in list(results_1a):
    # Create a dictionary for each row
    row_data = {}
    for feature in schema_data_1b:
        row_data[feature] = getattr(row, feature)
    rows_data_1b.append(row_data)

# Create a DataFrame from the list of dictionaries
df_1b = pd.DataFrame(rows_data_1b, columns=schema_data_1b)


df_1b[:5]

# %%
# Define the SQL query for Q1.c
QUERY_1C = """
SELECT release_year, COUNT(DISTINCT title) AS num_of_films
FROM bigquery-public-data.san_francisco.film_locations
GROUP BY release_year
ORDER BY release_year DESC
"""
# Execute the query
query_job_1c = client.query(QUERY_1C)
results_1c = query_job_1c.result()

# Convert the query results to a list of dictionaries
rows_data_1c = [{'release_year': row.release_year, 'num_of_films': row.num_of_films} for row in query_job_1c.result()]

# Convert the list of dictionaries to a DataFrame
df_1c = pd.DataFrame(rows_data_1c)

# Find the maximum number of films and the corresponding year
max_num_of_films = df_1c['num_of_films'].max()
max_films_year = df_1c[df_1c['num_of_films'] == max_num_of_films]['release_year'].values[0]

# Assign a different color for the maximum bar
colors = ['red' if num_of_films == max_num_of_films else 'green' for num_of_films in df_1c['num_of_films']]

# Plot the bar chart
ax_1c = df_1c.plot(kind='bar', x='release_year', y='num_of_films', color=colors, figsize=(13, 6), title='Number of Films Released in San Francisco by Year')
ax_1c.set_xlabel('Release Year')
ax_1c.set_ylabel('Number of Films')
ax_1c.get_legend().remove()  # Remove the legend

# Rotate x-axis labels for better readability
ax_1c.set_xticklabels(df_1c['release_year'], rotation=90)

# Tight layout for better spacing
plt.tight_layout()

# Show plot
plt.show()

# Print a nice sentence about the year with the most films released
print(f"The year with the most films released in San Francisco is {max_films_year}, with a total of {max_num_of_films} films.")

# %%
# Define the SQL query for Q1.d
QUERY_1D = """
  SELECT locations, COUNT(*) AS num_of_films
  FROM bigquery-public-data.san_francisco.film_locations
  WHERE locations <> ""
  GROUP BY locations
  ORDER BY num_of_films DESC
  LIMIT 20
"""

# Execute the query
query_job_1d = client.query(QUERY_1D)
results_1d = query_job_1d.result()

# Convert the query results to a list of tuples
rows_data_1d = [(row.locations, row.num_of_films) for row in results_1d]

# Convert the list of tuples to a DataFrame
df_1d = pd.DataFrame(rows_data_1d, columns=["locations", "num_of_films"])

# Plot the results
ax_1d = df_1d.plot(kind='barh', x='locations', y='num_of_films', color='green', figsize=(13, 6), title='Most Popular Films Locations')
ax_1d.set_xlabel('Number of Films')
ax_1d.set_ylabel('Locations')
ax_1d.get_legend().remove()

# Show plot
plt.show()

# %%
# Define the SQL query using a CTE for ranking incident categories by frequency per day
QUERY_2A = """
WITH RankedIncidents AS (
  SELECT 
    dayofweek, 
    category,
    COUNT(*) AS num_of_incidents,
    ROW_NUMBER() OVER (PARTITION BY dayofweek ORDER BY COUNT(*) DESC) AS row_num
  FROM bigquery-public-data.san_francisco.sfpd_incidents
  GROUP BY dayofweek, category
  ORDER BY num_of_incidents DESC
)
SELECT dayofweek, category ,num_of_incidents 
FROM RankedIncidents
WHERE row_num = 1;
"""

# Execute the query
query_job_2a = client.query(QUERY_2A)
results_2a = query_job_2a.result()

# Print the results
for row in results_2a:
    print(f"Day of the Week: {row.dayofweek}, Category: {row.category}, Total incidents: {row.num_of_incidents} ")

# %%
# Define the SQL query using a CTE for ranking calls type by frequency per day
QUERY_2B = """
WITH RankedCalls 
AS 
(
SELECT COUNT(*) as num_of_call_types,
       ROW_NUMBER() OVER(PARTITION BY dayofweek ORDER BY COUNT(*) DESC) AS row_num,
       dayofweek,
       call_type
  FROM (
    SELECT  
       call_type,
       FORMAT_DATE('%A', DATE(call_date)) AS dayofweek
    FROM bigquery-public-data.san_francisco.sffd_service_calls
  )
  GROUP BY dayofweek, call_type
  ORDER BY num_of_call_types DESC
) 
SELECT dayofweek, call_type, num_of_call_types
FROM RankedCalls
WHERE row_num = 1;
"""

# Execute the query
query_job_2b = client.query(QUERY_2B)
results_2b = query_job_2b .result()

# Print the results
for row in results_2b:
    print(f"Day of the Week: {row.dayofweek}, Call type: {row.call_type}, Total call types: {row.num_of_call_types} ")

# %%
#SQL query calculates and compares the weekly number of incidents reported by San Francisco's Police and Fire Departments.
QUERY_2C = """
WITH FireDepartment
AS 
(
  SELECT COUNT(call_type) AS total_call_types,
  FORMAT_DATE('%A', DATE(call_date)) AS day_of_week
  FROM bigquery-public-data.san_francisco.sffd_service_calls
  GROUP BY FORMAT_DATE('%A', DATE(call_date))
),
PoliceDepartmet
AS
(
  SELECT COUNT(category) AS total_cases,
  dayofweek
  FROM bigquery-public-data.san_francisco.sfpd_incidents
  GROUP BY dayofweek
)
SELECT dayofweek, SUM(total_cases) AS police_incidents, SUM(total_call_types) AS fire_department_incidents
FROM FireDepartment F
JOIN PoliceDepartmet P
ON F.day_of_week = P.dayofweek
GROUP BY P.dayofweek
ORDER BY CASE
    WHEN dayofweek = 'Sunday' THEN 1
    WHEN dayofweek = 'Monday' THEN 2
    WHEN dayofweek = 'Tuesday' THEN 3
    WHEN dayofweek = 'Wednesday' THEN 4
    WHEN dayofweek = 'Thursday' THEN 5
    WHEN dayofweek = 'Friday' THEN 6
    WHEN dayofweek = 'Saturday' THEN 7
    END;
"""

# Execute the query
query_job_2c = client.query(QUERY_2C)
results__2c = query_job_2c.result()

# Create a list of tuples from the query results
row_data_2c = [(row.dayofweek, row.police_incidents, row.fire_department_incidents) for row in results__2c]

# Create a DataFrame from the list of tuples
df_2c = pd.DataFrame(row_data_2c, columns=["Day of Week", "Police Incidents", "Fire Department Incidents"])

# Plot the DataFrame with markers and custom colors
ax = df_2c.plot(kind='line', x='Day of Week', y='Police Incidents', marker='o', color='blue', figsize=(13, 6), label='Police Incidents')
df_2c.plot(kind='line', x='Day of Week', y='Fire Department Incidents', marker='^', color='red', ax=ax, label='Fire Department Incidents')

# Set the title and labels with the customized attributes
ax.set_title('Number of Incidents By Department for Each Weekday', fontsize=16)
ax.set_xlabel('Day of Week', fontsize=14)
ax.set_ylabel('Number of Incidents', fontsize=14)

# Customizing the legend
ax.legend()

# Show the plot
plt.grid(True)
plt.show()
