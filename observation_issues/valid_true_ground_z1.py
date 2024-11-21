import pandas as pd
import re
import os
from collections import defaultdict, Counter
from tqdm import tqdm

# Define patterns for various attributes
patterns = {
    'brand': re.compile(r'\b(acer|panasonic|toshiba|hp|sony|lenovo|asus|dell|msi|xmg|targus|apple|macbook|aoson|gateway|microsoft|ibm|tandberg|tecra)\b', re.IGNORECASE),
    'model': re.compile(r'\b((?!note|\snet|\smac)[\w]+book|(?!think)[\w]+pad|(?<=aspire )e\s|via8850|aspire|dominator|vostro|precision|compaq|raid|vaio|satellite|swift|envy|pavilion|voodoo|3000|flex|legion|miix|skylight|yoga|z60m|ultrabay|rog|xps|inspiron|adamo|latitude|e[67]240|[ns][0-9]{4}|g[\s]*15|[0-9]{4}p|studio|rog|zephyrus|aficio|carbon|precision|[0-9]{4}dx|x[12][23]0|x[12]|(?<=elitebook\s)[0-9]{4}[mp]|[et][54][3421]0[sp]*|alienware|travelmate|gateway|edge|thinkcentre|thinkserver|proone)\b', re.IGNORECASE),
    'nums': re.compile(r'\b([\w]+[\d]+[-][\w]+[\d]+|[\d]+[\w]+[-][\d]+[\w]+|[\w]+[\d]+[-][\d]+[\w]+|[\d]+[\w]+[-][\w]+[\d]+|[\(][0-9a-z]+[\)])\b', re.IGNORECASE),
    'memory': re.compile(r'[\s][1-9]{1,2}[\s]*?gb[\s]*?((sdram)|(ddr3)|(ram)|(memory))*', re.IGNORECASE),
    'seller': re.compile(r'\b(firstshop|alibaba|ebay|mygofer|walmart|bestbuy|miniprice|softwarecity|thenerds|hoh de|buy net|topendelectronics|techbuy|schenker|overstock|tigerdirect|amazon|vology|paypal)\b', re.IGNORECASE),
    'cpu': re.compile(r'\b([iI][357][-\s]*|pentium|atom|centrino|celeron|xeon|[-]*a8[-]*|radeon|athlon|turion|phenom|a6-?[0-9]*)\b', re.IGNORECASE),
    'specific_cpu': re.compile(r'([0-9]{4}[mqu]m?)', re.IGNORECASE),
    'intel_or_amd': re.compile(r'\b(intel|amd)\b', re.IGNORECASE),
    'gpu': re.compile(r'\b(nvidia|geforce|gtx|rtx|quadro|radeon|vega|rx|hd)\b', re.IGNORECASE),
    'os': re.compile(r'\b(windows|macos|linux|ubuntu|chromeos)\b', re.IGNORECASE),
    'screen_size': re.compile(r'\b(\d{2}\.?\d{0,1}["]?)\b', re.IGNORECASE),
    'features': re.compile(r'(phenom[2]*|ssd|hdd|backlit|android|dvd|bluetooth|nvidia|refurbished|webcam|switching|used|reconditioned|wifi|camera|lcd|led|office|sata)', re.IGNORECASE),
    'loc': re.compile(r'\b(china|johannes|india|russia|usa|uk|australia|japan|shenzhen)',re.IGNORECASE),
    'color': re.compile(r'\b(silver|white|black|blue|purple|red|green|yellow|gold|pink|purple|gray|grey|orange|brown)\b', re.IGNORECASE)
}

# Define cleaning pattern
# x1_clean_pattern_1 = re.compile(r'\b(was|star|xe|labour|functi|twist|bare|nbd|quality|fi|touch|and|mini|led|for|test|home|hot|years|sas|cheap|call|whole|accessories|screen|desk|stables|quad|switch|cf|other|mhz|upgraded|comprar|color|customized|ii|inplane|gen|business|items|bulk|support|comparatif|tech|vs|install|use|inch|from|motherboard|oem|rdimm|state|hours|external|mb|kit|slim|elt|3m|ncs|popular|purchase|dock|cam|pentium|fessional|tower|great|fhd|ce|cn|presario|very|iconia|copy|helix|lot|est|laser|swappable|dongle|supply|listed|cessor|storage|officejet|ghost|displayport|dead|full|rw|nicaragua|embedded|bridge|yr|aten|gateway|giga|aseries|deals|wireless|wince|pricing|iii|branded|new|good|best|kids|product[s]*|buy|with|touchscreen|sale|rugged|extreme|warranty|capacitive|pro|bit)\b\s[-]|[|;:/,‰+©\(\)\\][psn]*|(?<=usb)[\s](?=[m23][.\s])|(?<=[a-z])[\s]+gb|(?<=gen)[\s_](?=[134\s][0]*)| \d+ ', re.IGNORECASE)
x1_clean_pattern_1 = re.compile(r'\b(?:bulk|shipping|was|star|xe|labour|functi|twist|bare|nbd|quality|fi|touch|and|mini|led|for|test|home|hot|years|sas|cheap|call|whole|accessories|screen|desk|stables|quad|switch|cf|other|mhz|upgraded|comprar|color|customized|ii|inplane|gen|business|items|bulk|support|comparatif|tech|vs|install|use|inch|from|motherboard|oem|rdimm|state|hours|external|mb|kit|slim|elt|3m|ncs|popular|purchase|dock|cam|pentium|fessional|tower|great|fhd|ce|cn|presario|very|iconia|copy|helix|lot|est|laser|swappable|dongle|supply|listed|cessor|storage|officejet|ghost|displayport|dead|full|rw|nicaragua|embedded|bridge|yr|aten|gateway|giga|aseries|deals|wireless|wince|pricing|iii|branded|new|good|best|kids|products*|buy|with|touchscreen|sale|rugged|extreme|warranty|capacitive|pro|bit)\b|\s[-]|[|;:/,‰+©\(\)\\][psn]*|(?<=usb)[\s](?=[m23][.\s])|(?<=[a-z])[\s]+gb|(?<=gen)[\s_](?=[134\s][0]*)| \d+', re.IGNORECASE)

# Function to clean the text using x1_clean_pattern_1
pattern_remove_numbers = re.compile(r'\b\d+\b')
# Define the regex pattern to remove standalone letters
pattern_remove_standalone_letters = re.compile(r'\b\w\b')
# Regex for letter repition
pattern_remove_more_similar_letters = re.compile(r'\b([a-zA-Z])\1{2,}\b')
# Define the regex pattern to remove two-letter words except for certain exceptions
pattern_remove_two_letter_words = re.compile(r'\b(?!uk\b|us\b)\w{2}\b', re.IGNORECASE)

def apply_clean_pattern(text):
    text = x1_clean_pattern_1.sub(' ', text)  # Remove the specified words and chars
    text = re.sub(pattern_remove_numbers, '', text)  # Remove standalone numbers
    text = re.sub(pattern_remove_standalone_letters, '', text)  # Remove standalone letters
    text = re.sub(pattern_remove_more_similar_letters, '', text)
    #text = re.sub(pattern_remove_two_letter_words, '', text)  # Remove two-letter words except for exceptions
    return text

# Function to clean the text
def clean_text(text):
    text = apply_clean_pattern(text)
    # Remove all non-alphanumeric characters except spaces
    text = re.sub(r'[^A-Za-z0-9\s]', '', text)
    # Convert to lowercase and remove specific characters
    cleaned_text = text.replace('-', '').replace('|', '').replace(',', '').replace('"', '').lower()
    # Remove duplicate words
    words = cleaned_text.split()
    words = list(dict.fromkeys(words))
    # Remove double spaces
    cleaned_text = ' '.join(words)
    return cleaned_text.strip()

# Functions to find various attributes in the text
def find_pattern(text, pattern):
    match = pattern.search(text)
    if match:
        return match.group().lower()
    return ''

def find_all_patterns(text):
    return {name: find_pattern(text, pattern) for name, pattern in patterns.items()}

# Function to generate blocking key
def generate_blocking_key_name(row):
    return "_".join([row[attr + '_group'] for attr in patterns.keys()])

# Function to create blocks for matching
def create_blocks(df):
    blocks = defaultdict(list)
    for rowid in tqdm(range(df.shape[0])):
        blocking_key = generate_blocking_key_name(df.iloc[rowid, :])
        if blocking_key != '':
            blocks[blocking_key].append(rowid)
    return blocks

# Function to clean blocks
def clean_blocks(blocks, df):
    cleaned_blocks = defaultdict(list)
    for key, row_ids in blocks.items():
        for row_id in row_ids:
            cleaned_blocks[key].append(row_id)
                
    # Sort the row_ids in each block
    for key in cleaned_blocks:
        cleaned_blocks[key] = sorted(cleaned_blocks[key], key=lambda x: df.at[x, 'cleaned_title'])
        
    return cleaned_blocks

# Function to create sub-blocks based on identical entries, removing those that occur only once
def create_sub_blocks(cleaned_blocks, df):
    sub_blocks = defaultdict(list)
    for block_key, row_ids in cleaned_blocks.items():
        entry_counts = defaultdict(list)
        for row_id in row_ids:
            cleaned_title = df.at[row_id, 'cleaned_title']
            entry_counts[cleaned_title].append(row_id)
        for cleaned_title, ids in entry_counts.items():
            if len(ids) > 1:  # Only keep entries that occur more than once
                sub_block_key = f"{block_key}_{cleaned_title}"
                sub_blocks[sub_block_key].extend(ids)
    return sub_blocks

# Function to generate matches
def generate_matches(blocks, df):
    candidate_pairs = []
    for key in tqdm(blocks):
        row_ids = list(sorted(blocks[key]))
        if len(row_ids) < 100:  # skip keys that are too common
            for i in range(len(row_ids)):
                for j in range(i + 1, len(row_ids)):
                    candidate_pairs.append((row_ids[i], row_ids[j]))

    similarity_threshold = 0.87
    jaccard_similarities = []
    candidate_pairs_product_ids = []
    
    for id1, id2 in tqdm(candidate_pairs):
        # Jaccard similarity
        name1 = set(df['cleaned_title'][id1].split())
        name2 = set(df['cleaned_title'][id2].split())
        union_len = len(name1.union(name2))
        if union_len == 0:  # Avoid division by zero
            continue
        jaccard_sim = len(name1.intersection(name2)) / union_len
        
        if jaccard_sim >= similarity_threshold:
            jaccard_similarities.append(jaccard_sim)
            product_id1 = df['id'][id1]
            product_id2 = df['id'][id2]
            if product_id1 < product_id2:
                candidate_pairs_product_ids.append((product_id1, product_id2))
            else:
                candidate_pairs_product_ids.append((product_id2, product_id1))

    return candidate_pairs_product_ids

# Function to evaluate matches
def evaluate(match_pairs, ground_truth):
    gt = list(zip(ground_truth['lid'], ground_truth['rid']))
    tp = len(set(match_pairs).intersection(set(gt)))
    fp = len(set(match_pairs).difference(set(gt)))
    fn = len(set(gt).difference(set(match_pairs)))
    recall = tp / (tp + fn)
    precision = tp / (tp + fp)

    print(f'Reported # of Pairs: {len(match_pairs)}')
    print(f'TP: {tp}')
    print(f'FP: {fp}')
    print(f'FN: {fn}')
    print(f'Recall: {recall}')
    print(f'Precision: {precision}')
    print(f'F1: {(2 * precision * recall) / (precision + recall)}')

# Function to read blocks from CSV
def read_blocks_from_csv(filepath):
    blocks = defaultdict(list)
    current_block_key = None
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.endswith('{'):
                current_block_key = line.split(' {')[0]
            elif line.endswith(']'):
                pass
            elif line == '}\n' or line == '}':
                current_block_key = None
            elif current_block_key is not None and line:
                try:
                    entry_id = int(line.split(':')[0].strip())
                    blocks[current_block_key].append(entry_id)
                except ValueError:
                    print(f"Skipping invalid line: {line}")
    return blocks

# Load the input dataframe Z1
z1_path = '../data/Z1.csv'
z1 = pd.read_csv(z1_path)

# Add an ID column
z1['id'] = z1.index

# Clean the 'title' column
z1['cleaned_title'] = z1['title'].apply(clean_text)

# Apply the functions to classify the titles by various attributes
for name in patterns.keys():
    z1[name + '_group'] = z1['cleaned_title'].apply(lambda x: find_pattern(x, patterns[name]))

# Create blocks
blocks = create_blocks(z1)

# Clean blocks
cleaned_blocks = clean_blocks(blocks, z1)

# Create sub-blocks
sub_blocks = create_sub_blocks(cleaned_blocks, z1)

# Write the sub-blocks to a single CSV file 
output_path = '../observation_issues/Z1_cleaned_sub_blocks.csv'

# Ensure the directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    for block_key, row_ids in sub_blocks.items():
        f.write(f"{block_key} {{\n")
        for row_id in row_ids:
            entry_id = z1.at[row_id, 'id']
            cleaned_title = z1.at[row_id, 'cleaned_title']
            f.write(f"  {entry_id}: {cleaned_title}\n")
        f.write("}\n\n")

print(f"All cleaned sub-blocks saved to {output_path}")

# Read blocks from the saved CSV
cleaned_sub_blocks_z1 = read_blocks_from_csv(output_path)

# Generate candidates
candidates_z1 = generate_matches(cleaned_sub_blocks_z1, z1)

# Evaluation
evaluate(candidates_z1, pd.read_csv('../data/ZY1.csv'))

# Save all IDs in each block to a CSV file
true_matches_output_path = '../observation_issues/Z1_true_matches.csv'

# Ensure the directory exists
os.makedirs(os.path.dirname(true_matches_output_path), exist_ok=True)

with open(true_matches_output_path, 'w', encoding='utf-8') as f:
    f.write('Anzahl,true_duplicates\n')
    for block_id, (block_key, row_ids) in enumerate(cleaned_sub_blocks_z1.items(), start=1):
        if len(row_ids) > 1:
            ids = ','.join(map(str, row_ids))
            f.write(f"{block_id}: {ids}\n")

print(f"True matches saved to {true_matches_output_path}")