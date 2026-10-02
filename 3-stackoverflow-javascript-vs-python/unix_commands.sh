#!/bin/bash
# Stack Overflow: JavaScript vs Python. Unix text processing of the Stack Overflow Q&A export.
# Authors: Daniel Rodan, Ido Shalom. Results: unix_results.txt

# Preparation: replace the commas between fields with tabs (commas inside quoted text are kept)
awk -F'"' -v OFS='"' '{ for (i=2; i<=NF; i+=2) gsub(",", "COMMAINSIDEQUOTES", $i) } 1' data/stackoverflow_javascript_python_qa.csv | sed "s/\,/\t/g" | sed "s/COMMAINSIDEQUOTES/\,/g" > stackoverflow_javascript_python_qa_clean.csv

# Question 1
head stackoverflow_javascript_python_qa_clean.csv

wc stackoverflow_javascript_python_qa_clean.csv

# Question 2
egrep -i -c pandas\|numpy stackoverflow_javascript_python_qa_clean.csv

awk -F '\t' '{print $5}' stackoverflow_javascript_python_qa_clean.csv | uniq | egrep -c -i pandas\|numpy

# Question 3
awk -F '\t' 'NR>1 {year=substr($4, 1, 4); print > ("stackoverflow_javascript_python_qa_clean_" year ".csv")}' stackoverflow_javascript_python_qa_clean.csv

for file in stackoverflow_javascript_python_qa_clean_*.csv; do echo "=== $file ==="; head -n 1 "$file"; echo "================="; done

# Question 4 (count_top_diff_freq_words.py is a small helper script that is not included here)
for file in stackoverflow_javascript_python_qa_clean_*.csv; do python3 count_top_diff_freq_words.py $file stackoverflow_javascript_python_qa_clean.csv 5; echo "================="; done

# Question 5
sbatch duplicate_and_zip.sh
