-- Stack Overflow: JavaScript vs Python. SQL queries on BigQuery's public Stack Overflow dataset.
-- Authors: Daniel Rodan, Ido Shalom. Results: sql_results.txt

-- Query 1
SELECT id, title, tags, answer_count, score
FROM `bigquery-public-data.stackoverflow.posts_questions` 
WHERE LOWER(tags) LIKE '%javascript%'
ORDER BY score DESC
LIMIT 5;

-- Query 2
SELECT 
    CASE WHEN LOWER(tags) LIKE '%javascript%' THEN 'javascript'
    WHEN (LOWER(tags) LIKE '%java%' AND LOWER(tags) NOT LIKE '%javascript%') THEN 'java'
    ELSE 'Other'
    END AS Description,
    COUNT(id) AS total_posts,
    COUNT(CASE WHEN answer_count > 0 THEN 1 END) AS posts_with_answers,
    AVG(answer_count) AS avg_answers,
    AVG(view_count) AS avg_views,
    AVG(score) AS avg_score
FROM
    bigquery-public-data.stackoverflow.posts_questions
GROUP BY Description 
HAVING Description NOT IN ('Other')
ORDER BY Description DESC;

-- Query 3
-- Question number 3
SELECT 
    CASE EXTRACT(DAYOFWEEK FROM creation_date)
    WHEN 1 THEN 'Sunday'
    WHEN 2 THEN 'Monday'
    WHEN 3 THEN 'Tuesday'
    WHEN 4 THEN 'Wednesday'
    WHEN 5 THEN 'Thursday'
    WHEN 6 THEN 'Friday'
    WHEN 7 THEN 'Saturday'
    END AS day_of_week,
    COUNT(id) AS total_posts,
    COUNT(CASE WHEN answer_count > 0 THEN 1 END) AS posts_with_answers,
    AVG(answer_count) AS avg_answers,
    AVG(view_count) AS avg_views,
    AVG(score) AS avg_score
FROM
    `bigquery-public-data.stackoverflow.posts_questions`
WHERE LOWER(tags) LIKE '%javascript%'
GROUP BY day_of_week 
ORDER BY total_posts DESC;

-- Query 4
SELECT A.tags, 
       A.title, 
       A.id AS question_id,
       A.creation_date AS question_date,
       REPLACE(A.body,'\n',' ') AS question_body, 
       B.id AS answer_id,
       B.creation_date AS answer_date,
       REPLACE(B.body,'\n',' ') AS answer_body
FROM `bigquery-public-data.stackoverflow.posts_questions` AS A
INNER JOIN 
`bigquery-public-data.stackoverflow.posts_answers` AS B
ON A.id = B.parent_id
WHERE LOWER(A.title) LIKE '%javascript%'
AND LOWER(A.title) LIKE '%python%'
ORDER BY question_id
LIMIT 5 ;

-- Query 5
WITH MYCTE 
AS 
(
SELECT
id,
display_name,
location,
reputation,
about_me,
website_url,
ROW_NUMBER() OVER (PARTITION BY SPLIT(LOWER(TRIM(location)), ',')[OFFSET(0)] ORDER BY reputation DESC) AS rn,
SPLIT(LOWER(TRIM(location)), ',')[OFFSET(0)] AS city_chopped,
FROM
`bigquery-public-data.stackoverflow.users`
WHERE
LOWER(location) LIKE '%, us%'
AND LOWER(about_me) LIKE '%javascript%'
AND SPLIT(LOWER(TRIM(location)), ',')[OFFSET(0)] IN ('new york', 'san francisco', 'los angeles', 'chicago', 'houston', 'alabama', 'alaska', 'arizona', 'california', 'colorado', 'florida', 'georgia', 'maryland', 'louisiana', 'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'west virginia', 'wisconsin', 'wyoming')
)
SELECT
id,
display_name,
city_chopped AS location,
reputation,
about_me,
website_url
FROM MYCTE
WHERE rn = 1
ORDER BY reputation DESC
LIMIT 5;

-- Query 6
-- Questions
WITH CTE1
AS 
(
SELECT C.id, 
       C.reputation,
CASE WHEN COUNT(C.id) < 1000 THEN '0-999'
WHEN COUNT(C.id) >= 1000 AND COUNT(C.id) < 2000 THEN '1000-1999'
WHEN COUNT(C.id) >= 2000 AND COUNT(C.id) < 3000 THEN '2000-2999'
END AS num_of_questions
FROM `bigquery-public-data.stackoverflow.users` C
LEFT JOIN `bigquery-public-data.stackoverflow.posts_questions` A
ON C.id = A.owner_user_id
GROUP BY C.id, C.reputation
)
SELECT num_of_questions, AVG(reputation) AS reputation_avg
FROM CTE1
GROUP BY num_of_questions
ORDER BY num_of_questions;

-- Answers

WITH CTE2
AS 
(
SELECT C.id, 
       C.reputation,
CASE WHEN COUNT(C.id) < 1000 THEN '0-999'
WHEN COUNT(C.id) >= 1000 AND COUNT(C.id) < 2000 THEN '1000-1999'
WHEN COUNT(C.id) >= 2000 AND COUNT(C.id) < 3000 THEN '2000-2999'
WHEN COUNT(C.id) >= 3000 AND COUNT(C.id) < 4000 THEN '3000-3999'
WHEN COUNT(C.id) >= 4000 AND COUNT(C.id) < 5000 THEN '4000-4999'
WHEN COUNT(C.id) >= 5000 AND COUNT(C.id) < 6000 THEN '5000-5999'
WHEN COUNT(C.id) >= 6000 AND COUNT(C.id) < 7000 THEN '6000-6999'
WHEN COUNT(C.id) >= 7000 AND COUNT(C.id) < 8000 THEN '7000-7999'
WHEN COUNT(C.id) >= 8000 AND COUNT(C.id) < 9000 THEN '8000-8999'
WHEN COUNT(C.id) >= 9000 AND COUNT(C.id) < 10000 THEN '9000-9999'
WHEN COUNT(C.id) >= 10000 THEN 'above 10000'
END AS num_of_answers
FROM `bigquery-public-data.stackoverflow.users` C
LEFT JOIN `bigquery-public-data.stackoverflow.posts_answers` B
ON C.id = B.owner_user_id
GROUP BY C.id, C.reputation
)
SELECT num_of_answers, AVG(reputation) AS reputation_avg
FROM CTE2
GROUP BY num_of_answers
ORDER BY num_of_answers;
