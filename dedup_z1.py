import re
import unidecode
from collections import defaultdict
import pandas as pd
from tqdm import tqdm

name_index = 1 

# Aliases for replacements
aliases = {
    'panasonic': ['pansonic'],
    'notebook': ['notebooks'],
    'tablet': ['tablets'],
    'pavilion': ['pavillion'],
    'duo': ['core2duo', 'core 2 '],
    'hp': ['hewlett-packard'],
    'used ': ['use '],
    ' ': ['cheapest', 'cheap', 'portable', 'laptop', 'kids', ';']
}

# Regular expression patterns
patterns = {
    'clean': re.compile(r'quality|new|good|best|kids|product[s]*|(?<=\s)buy\s|computer[s]*|\s[-]|(?<=i[357])-|[|;:/,‰+©\(\)\\][psn]*|(?<=usb)[\s](?=[m23][.\s])|(?<=[a-z])[\s]+gb|(?<=gen)[\s_](?=[134\s][0]*)'),
    'intel_cpu': re.compile(r'\b([i][357][-\s]*)|((?<=[\w+\d])*duo)|\b(pentium|atom|centrino|celeron|xeon|[-]*a8[-]*|radeon|athlon|turion|phenom|a6-?[0-9]*)'),
    'intel_cpu_specific': re.compile(r'([0-9]{4}[mqu]m?)'),
    'intel_or_amd': re.compile(r'\b(intel|amd)'),
    'brands': re.compile(r'\b(acer|panasonic|toshiba|hp|sony|lenovo|asus|dell|msi|xmg|targus|apple|macbook|aoson|gateway|microsoft|ibm|tandberg|tecra)\b'),
    'models': re.compile(r'\b((?!note|\snet|\smac)[\w]+book|(?!think)[\w]+pad|(?<=aspire )e\s|via8850|aspire|dominator-89|vostro|precision|compaq|raid|vaio|satellite|swift|envy|pavilion|voodoo|3000|flex|legion|miix|skylight|yoga|z60m|ultrabay|rog|xps|inspiron|adamo|latitude|e[67]240|[ns][0-9]{4}|g[\s]*15|[0-9]{4}p|studio|rog|zephyrus|aficio|carbon|precision|[0-9]{4}dx|x[12][23]0|x[12]|(?<=elitebook\s)[0-9]{4}[mp]|[et][54][3421]0[sp]*|alienware|travelmate|gateway|edge|thinkcentre|thinkserver|proone)\b'),
    'model_nums': re.compile(r'\b([\w]+[\d]+[-][\w]+[\d]+|[\d]+[\w]+[-][\d]+[\w]+|[\w]+[\d]+[-][\d]+[\w]+|[\d]+[\w]+[-][\w]+[\d]+|[\(][0-9a-z]+[\)])\b'),
    'mems': re.compile(r'[\s][1-9]{1,2}[\s]*?gb[\s]*?((sdram)|(ddr3)|(ram)|(memory))*'),
    'seller': re.compile(r'\b(firstshop|alibaba|ebay|mygofer|walmart|bestbuy|miniprice|softwarecity|thenerds|hoh.de|buy.net|topendelectronics|techbuy|schenker|overstock|tigerdirect|amazon|vology|paypal)'),
    'location': re.compile(r'\b(china|johannes|india|russia|usa|uk|australia|japan|shenzhen)'),
    'long_pattern': re.compile(r'\b(g75[\w]+-[\w]+|l-[0-9]{6}|e[135]-[0-9]{3}|e[56][0-9]{3}|bx[0-9]+|nq[0-9]{4}|10a[a-z][0-9]+|9s7-[\w\d]+|[\w\d]+(?=#aba)|[sc]55[d]*[-][a-z][0-9]+|[a-z]{2,3}?[0-9]+[a-z]+|np[0-9]+[\w]|alw[0-9]{2}-[0-9]+slv|bx[\w]+|cf-[\w\d]+|20[abcd][\w\d]+|20[abc][0a][0-9a-z]+|ux[\w\d]+|v11h[0-9]+|v3-[0-9]+|mg[\w\d]+\s|[um][0-9]{4}\b)'),
    'colors': re.compile(r'silver|white|black|blue|purple|red|green'),
    'features': re.compile(r'(phenom[2]*|ssd|hdd|backlit|android|dvd|bluetooth|nvidia|refurbished|webcam|switching|used|reconditioned|wifi|camera|lcd|led|office|sata)'),
    'thinkpad': re.compile(r'\b(x1 carbon|x[12][023][0-3][e]?)')
}

# Lenovo ThinkPad model numbers
lenovo_tp_modelnums = {
    'x230': r'(232[045]|343[0-9])',
    'x130e': r'(062|233)(?=[2789])',
    'x201': r'3[06][0-9]{2}',
    'x1 carbon': r'(34[46][048])'
}

# Aspire CPU mappings
aspire_cpu_map = {
    '6484': 'i34010u', '3401': 'i34010u', '2957': 'celeron2957u', '6458': 'i33110m', '6607': 'i32348m', '3234': 'i32348m',
    '5420': 'i54200u', '6870': 'i54200u', '767j': 'i74510u', '78s3': 'i7-4510U', '3311': 'i33110m', '6479': 'i54200u',
    '5842': 'i54200u', '30f1': 'i34005u', '38kj': 'i34005u', '6496': 'i53230m'
}

# Compile Lenovo ThinkPad model number regexes
lenovo_tp_regs = {key: re.compile(pattern) for key, pattern in lenovo_tp_modelnums.items()}

# Function to clean dataset
def clean_data(name: str) -> str:
    name = unidecode.unidecode(name.lower())
    for key, vals in aliases.items():
        for val in vals:
            name = name.replace(val, key)
    name = patterns['clean'].sub('', name)
    name = name.replace("  ", " ")
    return name

# Function to find single occurrence using compiled regex
def find_single_occurrence(pattern, text: str) -> str:
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
    match = pattern.search(text)
    return match.group() if match else ''

# Function to get Lenovo key
def get_lenovo_key(text: str) -> str:
    model = find_single_occurrence(patterns['thinkpad'], text)
    if model in lenovo_tp_modelnums:
        model_num = find_single_occurrence(lenovo_tp_regs[model], text)
        if 'x230' in model and model_num == '2320':
            model_num = '3435'
        return model + model_num
    return ''

# Function to find CPU
def find_cpu(text: str) -> str:
    cpu_search = patterns['intel_cpu'].search(text)
    cpu_search_specific = patterns['intel_cpu_specific'].findall(text)
    
    if not cpu_search:
        cpu_search = patterns['intel_or_amd'].search(text)
    
    cpu_res = [cpu_search.group()] if cpu_search else []
    if cpu_search_specific:
        cpu_res.extend(set(cpu_search_specific))
    
    return "".join(re.sub('[^0-9a-z]', '', i) for i in cpu_res).strip()

# Functions to find specific attributes
def find_brands(text: str) -> str:
    return " ".join(sorted(set(patterns['brands'].findall(text)))) if patterns['brands'].findall(text) else ''

def find_models(text: str) -> str:
    return " ".join(sorted(set(patterns['models'].findall(text)))) if patterns['models'].findall(text) else ''

def find_model_nums(text: str) -> str:
    return " ".join(sorted(set(patterns['model_nums'].findall(text)))) if patterns['model_nums'].findall(text) else ''

def find_memory(text: str) -> str:
    match = patterns['mems'].search(text)
    return re.sub('[^0-9a-z]+', '', match.group()[:5]) if match else ''

def find_sellers(text: str) -> str:
    return " ".join(sorted(set(patterns['seller'].findall(text)))) if patterns['seller'].findall(text) else ''

def find_location(text: str) -> str:
    match = patterns['location'].search(text)
    return match.group() if match else ''

def find_features(text: str) -> str:
    return " ".join(sorted(set(patterns['features'].findall(text)))) if patterns['features'].findall(text) else ''

# Function to generate blocking key name
def generate_blocking_key_name(row: pd.Series) -> tuple:
    title = str(row['title'])
    low_title = title.lower()
    pattern2id_1 = defaultdict(list)
    pattern2id_2 = defaultdict(list)

    pattern2id_1[" ".join(sorted(low_title.split()))].append(row.name)

    pattern_2 = re.findall(r"\w+\s\w+\d+", title)
    if pattern_2:
        pattern2id_2[" ".join(sorted([str(it).lower() for it in pattern_2]))].append(row.name)

    low_title = clean_data(low_title)

    pattern_2 = re.findall(r'[\d\w]+[-][\d\w]+[\d\w]+|[a-z]+[0-9]+', low_title)
    if pattern_2:
        pattern2id_2[" ".join(sorted([str(it).lower() for it in pattern_2]))].append(row.name)

    brands = find_brands(low_title)

    if 'lenovo' in brands or 'thinkpad' in low_title:
        len_model = get_lenovo_key(low_title)
        if len_model:
            pattern2id_1[len_model].append(row.name)
            return pattern2id_1, pattern2id_2

    elif 'acer' in brands and 'aspire' in low_title:
        cpu_or_model = find_single_occurrence(patterns['intel_cpu_specific'], low_title)
        cpu_or_model = re.sub(r'[^0-9a-z]', '', cpu_or_model)
        if not cpu_or_model:
            cpu_or_model = find_single_occurrence(patterns['long_pattern'], low_title)
            if cpu_or_model and cpu_or_model[-4:] in aspire_cpu_map:
                cpu_or_model = aspire_cpu_map[cpu_or_model[-4:]]
        
        if cpu_or_model:
            pattern2id_1[''.join(['acer aspire ', cpu_or_model])].append(row.name)
            return pattern2id_1, pattern2id_2

    cpus = find_cpu(low_title)
    models = find_models(low_title)
    model_nums = find_model_nums(low_title)
    mems = find_memory(low_title)
    sellers = find_sellers(low_title)
    loc = find_location(low_title)
    features = find_features(low_title)

    if features:
        if models:
            pattern2id_2["".join([brands, models, features])].append(row.name)
        pattern2id_2["".join([brands, features, cpus])].append(row.name)

    p_type = find_single_occurrence(re.compile(r'tablet|notebook|netbook|capacitative|touch|gaming'), low_title)
    if p_type:
        pattern2id_2["".join([brands, models, p_type])].append(row.name)
        pattern2id_2["".join([brands, model_nums, p_type])].append(row.name)

    long_pattern = find_single_occurrence(patterns['long_pattern'], low_title)
    pattern2id_2[long_pattern].append(row.name)
    pattern2id_2["".join([brands, models, cpus, mems])].append(row.name)
    pattern2id_2["".join([models, cpus, mems])].append(row.name)
    pattern2id_2["".join([models, model_nums])].append(row.name)
    pattern2id_2["".join([brands, model_nums])].append(row.name)
    pattern2id_2["".join([sellers, loc, brands, models])].append(row.name)

    return pattern2id_1, pattern2id_2

# Function to create blocks
def create_blocks(df: pd.DataFrame) -> defaultdict:
    blocks = defaultdict(list)
    for rowid in tqdm(range(df.shape[0])):
        pattern2id_1, pattern2id_2 = generate_blocking_key_name(df.iloc[rowid, :])
        for key, indices in pattern2id_1.items():
            blocks[key].extend(indices)
        for key, indices in pattern2id_2.items():
            blocks[key].extend(indices)
    return blocks

# Function to generate matches
def generate_matches(blocks: defaultdict, df: pd.DataFrame) -> list:
    candidate_pairs = []
    for key in tqdm(blocks):
        row_ids = sorted(blocks[key])
        if len(row_ids) < 100:  # skip keys that are too common
            for i in range(len(row_ids)):
                for j in range(i + 1, len(row_ids)):
                    candidate_pairs.append((row_ids[i], row_ids[j]))

    similarity_threshold = 0.8
    jaccard_similarities = []
    candidate_pairs_product_ids = []
    
    for id1, id2 in tqdm(candidate_pairs):
        product_id1 = df['id'][id1]
        product_id2 = df['id'][id2]
        
        if product_id1 < product_id2:  # Ensure order
            candidate_pairs_product_ids.append((product_id1, product_id2))
        else:
            candidate_pairs_product_ids.append((product_id2, product_id1))  

        name1 = str(df.iloc[id1, name_index])
        name2 = str(df.iloc[id2, name_index])
        s1 = set(name1.lower().split())
        s2 = set(name2.lower().split())
        jaccard_similarities.append(len(s1.intersection(s2)) / max(len(s1), len(s2)))

    candidate_pairs_product_ids = [x for s, x in sorted(zip(jaccard_similarities, candidate_pairs_product_ids), reverse=True) if s >= similarity_threshold]
    
    return candidate_pairs_product_ids

# Main function to generate blocking keys and matches
def pattern_key(df: pd.DataFrame) -> list:
    blocks = create_blocks(df)
    candidates = generate_matches(blocks, df)
    return candidates
