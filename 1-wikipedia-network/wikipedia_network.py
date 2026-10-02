"""What holds Wikipedia together? Network analysis of the 2002 English Wikipedia link graph.

Code exported from wikipedia_network.ipynb; see the notebook for outputs and charts.
"""

# %%
# General code
import csv
from operator import itemgetter
import networkx as nx  # networkx - python library for dealing with graphs
from networkx.algorithms import community # This part of networkx, for community detection, needs to be imported separately.

from google.colab import drive
drive.mount('/content/drive/', force_remount=True)

# %%
import requests  # Needed to download files from the web
import gzip  # Used to handle compressed files
import pandas as pd  # Useful for data manipulation and analysis
import networkx as nx  # Helps with network structures like graphs
from operator import itemgetter  # Useful for sorting data
import matplotlib.pyplot as plt  # Used for creating visualizations

# Download the dataset from the internet and save it locally
dataset_url = 'https://zenodo.org/records/2539424/files/enwiki.wikilink_graph.2002-03-01.csv.gz?download=1'
response = requests.get(dataset_url)
with open('downloaded_dataset.csv.gz', 'wb') as file:
    file.write(response.content)

# Load the dataset from the file into a table format for easier handling
with gzip.open('downloaded_dataset.csv.gz', 'rt', encoding='utf-8') as gz_file:
    data_frame = pd.read_csv(gz_file, delimiter='\t')

# Convert the data into a directed graph format to analyze connections
directed_graph = nx.from_pandas_edgelist(data_frame, 'page_id_from', 'page_id_to', create_using=nx.DiGraph())

# Compute how many connections go into and out of each page
node_in_degrees = dict(directed_graph.in_degree())
node_out_degrees = dict(directed_graph.out_degree())

# Identify and list the top pages based on their number of incoming and outgoing connections
top_in_degree_nodes = sorted(node_in_degrees.items(), key=itemgetter(1), reverse=True)[:5]
top_out_degree_nodes = sorted(node_out_degrees.items(), key=itemgetter(1), reverse=True)[:5]

# Print the top pages by number of incoming and outgoing connections
print("Top 5 Nodes by In-Degree:")
for rank, (node_id, in_degree) in enumerate(top_in_degree_nodes, start=1):
    print(f"{rank}. Node ID: {node_id} with In-Degree: {in_degree}")

print("\nTop 5 Nodes by Out-Degree:")
for rank, (node_id, out_degree) in enumerate(top_out_degree_nodes, start=1):
    print(f"{rank}. Node ID: {node_id} with Out-Degree: {out_degree}")

# Analyze and visualize how common different connection counts are among the pages
max_degree_in = max(node_in_degrees.values())
max_degree_out = max(node_out_degrees.values())

in_degree_dist = [list(node_in_degrees.values()).count(i) / float(nx.number_of_nodes(directed_graph)) for i in range(max_degree_in + 1)]
out_degree_dist = [list(node_out_degrees.values()).count(i) / float(nx.number_of_nodes(directed_graph)) for i in range(max_degree_out + 1)]

# Plot the distribution of incoming and outgoing connections
plt.figure(figsize=(14, 7))
plt.subplot(1, 2, 1)
plt.plot(in_degree_dist, color="green")
plt.xscale('log')
plt.yscale('log')
plt.title('In-Degree Distribution')
plt.xlabel('Degree')
plt.ylabel('Frequency')

plt.subplot(1, 2, 2)
plt.plot(out_degree_dist, color="purple")
plt.xscale('log')
plt.yscale('log')
plt.title('Out-Degree Distribution')
plt.xlabel('Degree')
plt.ylabel('Frequency')

plt.tight_layout()
plt.show()

# %%
# Transform the directed graph from Q1 to undirected
network_undirected = directed_graph.to_undirected()

# Configuration for an Erdos-Renyi graph equivalent
total_nodes = network_undirected.number_of_nodes()
total_edges = network_undirected.number_of_edges()
probability_for_edges = 2 * total_edges / (total_nodes * (total_nodes - 1))

# Create a random graph using the Erdos-Renyi model
randomized_graph = nx.gnp_random_graph(total_nodes, probability_for_edges)

# Calculation of degree distributions
degree_undirected = dict(network_undirected.degree())
degree_randomized = dict(randomized_graph.degree())
peak_degree = max(max(degree_undirected.values()), max(degree_randomized.values()))

# Calculate the proportion of nodes for each connection count
degree_dist_undirected = [list(degree_undirected.values()).count(i) / float(total_nodes) for i in range(peak_degree + 1)]
degree_dist_randomized = [list(degree_randomized.values()).count(i) / float(total_nodes) for i in range(peak_degree + 1)]

# Plotting degree distributions
plt.figure(figsize=(14, 7))
plt.loglog(degree_dist_undirected, color='navy', label='Undirected Network')
plt.loglog(degree_dist_randomized, color='orange', label='Erdos-Renyi Graph')
plt.title('Comparison of Degree Distributions')
plt.xlabel('Degree')
plt.ylabel('Frequency')
plt.legend()
plt.show()

# %%
import random  # For the 10% random sampling

# Run PageRank on the directed graph from Q1
page_rank_scores = nx.pagerank(directed_graph, alpha=0.85, tol=1e-6)

# Report the ten pages with the highest PageRank values
top_ten = sorted(page_rank_scores.items(), key=lambda pair: pair[1], reverse=True)[:10]
print("Ten pages with the highest PageRank values:")
for page_id, pr_score in top_ten:
    print(f"Node: {page_id}, PageRank Score: {pr_score}")

# Prepare data for scatter plots, taking a 10% random sample of nodes
nodes_sample = random.sample(list(directed_graph.nodes()), k=int(0.1 * directed_graph.number_of_nodes()))
in_degree_scores = dict(directed_graph.in_degree())
out_degree_scores = dict(directed_graph.out_degree())

sampled_page_rank_in_degree = [(in_degree_scores[node], page_rank_scores[node]) for node in nodes_sample]
sampled_page_rank_out_degree = [(out_degree_scores[node], page_rank_scores[node]) for node in nodes_sample]

# Scatter Plot of In-Degree vs. PageRank
plt.figure(figsize=(14, 7))
plt.subplot(1, 2, 1)
plt.scatter(*zip(*sampled_page_rank_in_degree), alpha=0.5, color='blue')
plt.xscale('log')
plt.yscale('log')
plt.ylabel('PageRank Score')
plt.xlabel('In-Degree')
plt.title('In-Degree vs. PageRank (10% sample)')
plt.annotate('10% sample', xy=(0.05, 0.95), xycoords='axes fraction', fontsize=10, color='red')

# Scatter Plot of Out-Degree vs. PageRank
plt.subplot(1, 2, 2)
plt.scatter(*zip(*sampled_page_rank_out_degree), alpha=0.5, color='green')
plt.xscale('log')
plt.yscale('log')
plt.ylabel('PageRank Score')
plt.xlabel('Out-Degree')
plt.title('Out-Degree vs. PageRank (10% sample)')
plt.annotate('10% sample', xy=(0.05, 0.95), xycoords='axes fraction', fontsize=10, color='red')

plt.tight_layout()
plt.show()

# %%
from operator import itemgetter # Useful for sorting data

# Identifying teleport sets with case insensitivity
sports_teleport_set = {row['page_id_from'] for index, row in data_frame.iterrows() if 'Sports'.lower() in row['page_title_from'].lower()}
history_teleport_set = {row['page_id_from'] for index, row in data_frame.iterrows() if 'History' in row['page_title_from']}

# Executing Topic-Specific PageRank for "Sports" and "History" with specified alpha and tolerance
sports_pagerank_scores = nx.pagerank(directed_graph, alpha=0.85, tol=0.00001, personalization={node: 1.0 if node in sports_teleport_set else 0.0 for node in directed_graph.nodes()})
history_pagerank_scores = nx.pagerank(directed_graph, alpha=0.85, tol=0.00001, personalization={node: 1.0 if node in history_teleport_set else 0.0 for node in directed_graph.nodes()})

# Utility function for retrieving page titles based on their IDs
def get_page_title(page_id):
    title_series = data_frame[data_frame['page_id_from'] == page_id]['page_title_from']
    return title_series.iloc[0] if not title_series.empty else "404 Title not found"

# Finding top 10 pages for each category and filtering by title inclusion
top_sports = [(node, score) for node, score in sorted(sports_pagerank_scores.items(), key=itemgetter(1), reverse=True) if 'Sports'.lower() in get_page_title(node).lower()][:10]
top_history = [(node, score) for node, score in sorted(history_pagerank_scores.items(), key=itemgetter(1), reverse=True) if 'History' in get_page_title(node)][:10]

# Output the results with page names using get_page_title
print("Top 10 'Sports' Pages by Topic-Specific PageRank:")
for node, score in top_sports:
    print(f"Node: {node}, Page Title: {get_page_title(node)}, Score: {score}")

print("\nTop 10 'History' Pages by Topic-Specific PageRank:")
for node, score in top_history:
    print(f"Node: {node}, Page Title: {get_page_title(node)}, Score: {score}")

# %%
from networkx.algorithms.community import louvain_communities, modularity # community detection and measuring their quality
import random  # generating random numbers and samples
import matplotlib.pyplot as plt  # plotting graphs and visualizations
import networkx as nx  # creating and manipulating complex networks

# Run the Louvain algorithm on the entire undirected graph to find communities
communities = louvain_communities(network_undirected)

# Report the number of communities and modularity for the entire network
print(f"Detected communities: {len(communities)}")
modularity_val = modularity(network_undirected, communities)
print(f"Modularity of the network: {modularity_val}")

# Unite small communities into one 'super community' if they have fewer than 100 nodes
super_community = set()
remaining_communities = []
for community in communities:
    if len(community) < 100:
        super_community = super_community.union(community)
    else:
        remaining_communities.append(community)
if super_community:
    remaining_communities.append(super_community)

# Visualization part
# Select a 10% random sample of nodes for visualization
nodes_sample = random.sample(list(network_undirected.nodes()), k=int(0.1 * network_undirected.number_of_nodes()))
sampled_graph = network_undirected.subgraph(nodes_sample)

# Assign colors based on community membership
color_map = {node: idx for idx, community in enumerate(remaining_communities) for node in community}
node_colors = [color_map.get(node, 0) for node in sampled_graph.nodes()]

# Layout for the visualization
pos = nx.spring_layout(sampled_graph)

# Draw the network with community coloring
plt.figure(figsize=(12, 8))
nx.draw_networkx(sampled_graph, pos, node_color=node_colors, with_labels=False, node_size=50, cmap=plt.cm.jet)
plt.annotate('10% sample', xy=(0.05, 0.95), xycoords='axes fraction', fontsize=10, color='red')
plt.title('Network Visualization with Community Detection (10% Sample)')
plt.show()

# %%
import matplotlib.pyplot as plt  # drawing charts and graphs
import networkx as nx  # working with networks and graphs
from collections import Counter  # Helps count items easily
from bs4 import BeautifulSoup  # For pulling data out of HTML
import requests  # Used for web requests
import nltk  # For processing language data
from nltk.corpus import stopwords  # Stop words that usually don't carry much meaning
from nltk.tokenize import word_tokenize  # To split text into words
from urllib.parse import quote  # safely create URLs

# Set up the necessary NLTK resources
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# Define a list of English words that aren't usually meaningful
stop_words = set(stopwords.words('english'))

# Extract and clean text from a webpage
def clean_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    words = word_tokenize(text)

    # Keep only meaningful words that are more than one letter long
    words = [
        word.lower() for word in words
        if word.isalpha() and word.lower() not in stop_words and len(word) > 1
    ]
    return words

# Get webpages by titles and clean their text
def fetch_and_clean(page_titles):
    base_url = "https://en.wikipedia.org/wiki/"
    all_words = []
    for title in page_titles:
        encoded_title = quote(title.replace(" ", "_"))   # Make the title URL-friendly
        try:
            response = requests.get(base_url + encoded_title)
            if response.status_code == 200:
                words = clean_text(response.text)
                all_words.extend(words)
        except Exception as e:
            print(f"Failed to fetch {title}: {str(e)}")
    return all_words


# Extract the 5 largest communitiesm from Q5
largest_communities = sorted(communities, key=len, reverse=True)[:5]

# Process each community
for idx, community in enumerate(largest_communities, start=1):
    # Mapping node IDs to page titles
    page_titles = [data_frame[data_frame['page_id_from'] == node]['page_title_from'].iloc[0] if not data_frame[data_frame['page_id_from'] == node].empty else "Unknown" for node in community]

    # Fetch and clean content from these pages
    words = fetch_and_clean(page_titles)

    # Count and plot the most common words
    word_counts = Counter(words)
    most_common = word_counts.most_common(25)
    words, frequencies = zip(*most_common)
    plt.figure(figsize=(15, 8))
    plt.bar(words, frequencies, color='magenta')
    plt.title(f'Community {idx} - Top 25 Most Frequent Words')
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45, fontsize=10)
    plt.tight_layout()
    plt.show()
