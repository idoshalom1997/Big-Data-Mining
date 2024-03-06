#!/bin/bash

for i in {1..10}; do cat "stackoverflow_javascript_python_qa.csv" >> "stackoverflow_javascript_python_qa_x10.csv"; done
sort stackoverflow_javascript_python_qa_x10.csv > stackoverflow_javascript_python_qa_x10_sorted.csv
echo "Original files size:"
echo -e "Size\tFile"
for file in stackoverflow_javascript_python_qa*.csv; do du -h $file; done
for file in stackoverflow_javascript_python_qa*.csv; do echo -e " \ntimes to compress $file"; time gzip $file; done
echo -e "\nCompressed files size:\nSize\tFile"
for file in stackoverflow_javascript_python_qa*.csv; do du -h $file".gz"; done
