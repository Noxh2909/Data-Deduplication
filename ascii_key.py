import time
from collections import defaultdict
from tqdm import tqdm
import pandas as pd
import re


# Global parameters
name_column_index = 1
def sum_ascii_values(string):
    #sum the ASCII values of the characters in the string
    return sum(ord(char) for char in string)

def clean_words(words: list):
    # Remove words that contain a question mark
    words = [word for word in words if '?' not in word]
    # Remove words that end with .com
    words = [word for word in words if not word.endswith('.com')]
    # Remove special characters
    words = [re.sub(r'[^\w\s]', '', word) for word in words]
    # Remove words that contain 'ebay'
    words = [word for word in words if 'ebay' not in word]
    # Remove words that contain 'amazon'
    words = [word for word in words if 'amazon' not in word]
    # Remove empty words
    words = [word for word in words if word != '']
    return words

# Generate statistics on word frequency
def generate_statistic(df: pd.DataFrame):
    statistic = {}
    for rowid in tqdm(range(df.shape[0])):
        row = df.iloc[rowid,1]
        row = row.lower()
        words = clean_words(row.split())
        key = [sum_ascii_values(word) for word in words]
        for word in key:
            if word in statistic:
                statistic[word] += 1
            else:
                statistic[word] = 1
    return statistic

# Generate the blocking key
def generate_blocking_key(row: pd.Series):
    # Split the string into words
    key = []
    row = row.lower()
    words = clean_words(row.split())

    key = [sum_ascii_values(word) for word in words]
    key = sorted(set(key))
    return key

# Create the blocks
def create_blocks(df: pd.DataFrame, threshold: int):
    blocks = defaultdict(list)  
    statistic = {}
    statistic = generate_statistic(df)
    for rowid in tqdm(range(df.shape[0])):
        blocking_key = generate_blocking_key(df.iloc[rowid,1])
        blocking_key = [word for word in blocking_key if statistic[word] < threshold]
        blocking_key = str(blocking_key)
        if blocking_key != '':
            blocks[blocking_key].append(rowid)

    return blocks

# Generate the duplicate pairs
def generate_matches(blocks: defaultdict, df: pd.DataFrame, similarity_threshold: int):

    candidate_pairs = []
    for key in tqdm(blocks):
        row_ids = list(sorted(blocks[key]))
        if len(row_ids) < 500:  # Skip keys that are too common
            for i in range(len(row_ids)):
                for j in range(i + 1, len(row_ids)):
                    candidate_pairs.append((row_ids[i], row_ids[j]))

    jaccard_similarities = []
    candidate_pairs_product_ids = []
    for it in tqdm(candidate_pairs):
        id1, id2 = it

        # Get product ids
        product_id1 = df['id'][id1]
        product_id2 = df['id'][id2]
        if product_id1 < product_id2:  # NOTE: This is to make sure in the final candidates, for a pair id1 and id2 (assume id1<id2), we only include (id1,id2) but not (id2, id1)
            candidate_pairs_product_ids.append((product_id1, product_id2))
        else:
            candidate_pairs_product_ids.append((product_id2, product_id1))

        # Compute Jaccard similarity
        name1 = str(df[df.columns.values[name_column_index]][id1])
        name2 = str(df[df.columns.values[name_column_index]][id2])
        s1 = set(name1.lower().split())
        s2 = set(name2.lower().split())
        jaccard_similarities.append(len(s1.intersection(s2)) / max(len(s1), len(s2)))
    candidate_pairs_product_ids = [x for s, x in sorted(zip(jaccard_similarities, candidate_pairs_product_ids), reverse=True) if s >= similarity_threshold]
    return candidate_pairs_product_ids


def ascii_key(Z: pd.DataFrame, case: int):
    # Perform blocking
    if case == 2:
        threshold = 100000
        similarity_threshold = 0.75
    else:  
        threshold = 50000
        similarity_threshold = 0.87

    blocks_Z = create_blocks(Z, threshold)
    # Generate candidates
    candidates_Z = generate_matches(blocks_Z, Z, similarity_threshold)
    return candidates_Z