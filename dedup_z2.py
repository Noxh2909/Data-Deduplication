import time
from collections import defaultdict
from tqdm import tqdm
import pandas as pd
import re
import unidecode

name_column_index = 1

patterns = {
    'clean_1': r'&(nbsp|amp|reg|[a-z]?acute|quot|trade);?|[|;:/,‰+©\(\)\\][psn]*|(?<=usb)[\s][m]*(?=[23][\.\s])|(?<=usb)-[\w]+\s(?=[23][\.\s])|(?<=[a-z])[\s]+gb|(?<=data|jump)[t\s](?=trave|drive)|(?<=extreme|exceria)[\s](?=pro[\s]|plus)|(?<=class)[\s_](?=10|[234]\b)|(?<=gen)[\s_](?=[134\s][0]*)',
    'class10': r'(10 class|class 10|class(?=[\w]+10\b)|cl\s10)',
    'memory_clean': r'\b(msd|microvault|sd-karte|speicherkarte|minneskort|memóriakártya|flashgeheugenkaart|geheugenkaart|speicherkarten|memoriakartya|[-\s]+kaart|memory|memoria|memoire|mémoire|mamoria|tarjeta|carte|karta)',
    'usb_clean': r'\b(flash[\s-]*drive|flash[\s-]*disk|pen[\s]*drive|micro-usb|usb-flashstation|usb-flash|usb-minne|usb-stick|speicherstick|flashgeheugen|flash|vault)',
    'adapter': r'\b(adapter|adaptateur|adaptador|adattatore)',
    'colors': r'silver|white|black|blue|purple|burgundy|red|green',
    'speedrw': r'\b[0-9]{2,3}r[0-9]{2,3}w',
    'model_num': r'\b([\(]*[\w]+[-]*[\d]+[-]*[\w]+[-]*[\d+]*|[\d]+[\w]|[\w][\d]+)',
    'brand': r'\b(intenso|lexar|logilink|pny|samsung|sandisk|kingston|sony|toshiba|transcend)\b',
    'model': r'\b(datatraveler|extreme[p]?|exceria[p]?|dual[\s]*(?!=sim)|evo|xqd|ssd|cruzer[\w+]*|glide|blade|basic|fit|force|basic line|jump\s?drive|hxs|rainbow|speed line|premium line|att4|attach|serie u|r-serie|beast|fury|impact|a400|sd[hx]c|uhs[i12][i1]*|note\s?9|ultra)',
    'tv_phone': r'\b(tv|(?<=dual[\s-])*sim|lte|[45]g\b|[oq]*led_[u]*hd|led|galaxy|iphone|oneplus|[0-9]{1,2}[.]*[0-9]*(?=[-\s]*["inch]+))',
    'memory': r'([1-9]{1,3})[-\s]*[g][bo]?',
    'modelnum_long': r'(thn-[a-z][\w]+|ljd[\w+][-][\w]+|ljd[sc][\w]+[-][\w]+|lsdmi[\d]+[\w]+|lsd[0-9]{1,3}[gb]+[\w]+|ljds[0-9]{2}[-][\w]+|usm[0-9]{1,3}[\w]+|sdsq[a-z]+[-][0-9]+[a-z]+[-][\w]+|sdsd[a-z]+[-][0-9]+[\w]+[-]*[\w]*|sdcz[\w]+|mk[\d]+|sr-g1[\w]+)',
    'modelnum_short': r'\b(c20[mc]|sda[0-9]{1,2}|g1ux|s[72][05]|[unm][23]02|p20|g4|dt101|se9|[asm][0-9]{2})',
    'features': r'\b(usb[23]|type-c|uhs[i]{1,2}|class[0134]{1,2}|gen[1-9]{1,2}|u[23](?=[\s\.])|sd[hx]c|otg|lte|[45]g[-\s]lte|[0-9]+(?=-inch)|[0-9]{2,3}r[0-9]{2,3}w|[0-9]{2,3}(?=[\smbo/p]{3}))'
}

aliases = {
    'class': ['classe', 'clase', 'clas ', 'klasse', 'cl '],
    'uhsi': ['uhs1', 'uhs-i', 'ultra high-speed'],
    'type-c': ['typec', 'type c', 'usb-c', 'usbc'],
    'intenso premium line': ['3534490'],
    'kingston hxs ': ['hyperx', 'savage'],
    'sony g1ux': ['serie ux'],
    ' kingston dt101 ': ['dtig4', ' 101 ', 'dt101g2'],
    ' kingston ultimate ': ['sda10', 'sda3'],
    'extreme ': ['extrem '],
    'att4': ['attach']
}

compiled_patterns = {key: re.compile(pattern) for key, pattern in patterns.items()}

def clean_name(name):
    name = unidecode.unidecode(name.lower())
    for main_key, alt_keys in aliases.items():
        for alt_key in alt_keys:
            name = name.replace(alt_key, main_key)
    name = compiled_patterns['clean_1'].sub('', name)
    name = compiled_patterns['class10'].sub('class10', name)
    name = name.replace('class 4 ', 'class4 ')
    name = name.replace('class 3 ', 'class3 ')
    return name.replace('  ', ' ')

def extract_match(pattern, text):
    match = pattern.search(text)
    return match.group() if match else ''

def extract_all_matches(pattern, text):
    matches = pattern.findall(text)
    return ' '.join(sorted(set(matches))) if matches else ''

def find_single_occurence_compreg(compiled_reg, name):
    return extract_match(compiled_reg, name)

def find_all_occurences_sorted_unique_compreg(compiled_reg, name):
    return extract_all_matches(compiled_reg, name)

def generate_blocking_key_name(row):
    model_nums, brands, model_types, mems, features = [], [], [], [], []
    pattern2id_1, pattern2id_2 = defaultdict(list), defaultdict(list)

    if pd.notna(row['name']):
        title = str(row['name']).lower()
        pattern_1 = title
        pattern2id_1[" ".join(sorted(pattern_1.split()))].append(row.name)

        pattern_2 = re.findall(r"\w+\s\w+\d+", title)
        if pattern_2:
            pattern_2 = list(sorted(pattern_2))
            pattern2id_2[" ".join([str(it).lower() for it in pattern_2])].append(row.name)

        pattern_1 = clean_name(pattern_1)
        model_nums.append(extract_all_matches(compiled_patterns['model_num'], pattern_1))
        brands.append(extract_all_matches(compiled_patterns['brand'], pattern_1))
        model_types.append(extract_all_matches(compiled_patterns['model'], pattern_1))
        mems.append(extract_all_matches(compiled_patterns['memory'], pattern_1))
        features.append(extract_all_matches(compiled_patterns['features'], pattern_1))
        
        long_pattern = extract_match(compiled_patterns['modelnum_long'], pattern_1)
        short_pattern = extract_all_matches(compiled_patterns['modelnum_short'], pattern_1)
        
        if features:
            pattern2id_2[" ".join([brands[-1], features[-1]])].append(row.name)
        pattern2id_2[long_pattern].append(row.name)
        pattern2id_2[short_pattern].append(row.name)
        pattern2id_2[" ".join([brands[-1], mems[-1]])].append(row.name)
        pattern2id_2[" ".join([brands[-1], mems[-1], model_types[-1]])].append(row.name)
        pattern2id_2[" ".join([brands[-1], model_nums[-1]])].append(row.name)
    
    return pattern2id_1, pattern2id_2

def create_blocks(df):
    blocks = defaultdict(list)
    for rowid in tqdm(range(df.shape[0])):
        pattern2id_1, pattern2id_2 = generate_blocking_key_name(df.iloc[rowid, :])
        for key, indices in pattern2id_1.items():
            blocks[key].extend(indices)
        for key, indices in pattern2id_2.items():
            blocks[key].extend(indices)
    return blocks

def generate_matches(blocks, df):
    candidate_pairs = []
    for key in tqdm(blocks):
        row_ids = sorted(blocks[key])
        if len(row_ids) < 100:
            candidate_pairs.extend((row_ids[i], row_ids[j]) for i in range(len(row_ids)) for j in range(i + 1, len(row_ids)))

    similarity_threshold = 0.75
    final_pairs = []
    for id1, id2 in tqdm(candidate_pairs):
        id1, id2 = sorted([id1, id2])
        product_id1, product_id2 = df['id'][id1], df['id'][id2]
        name1, name2 = df.iloc[id1, name_column_index].lower(), df.iloc[id2, name_column_index].lower()
        jaccard_index = len(set(name1.split()).intersection(set(name2.split()))) / max(len(name1.split()), len(name2.split()))
        if jaccard_index >= similarity_threshold:
            final_pairs.append((product_id1, product_id2))
    return final_pairs

def pattern_key(df):
    blocks = create_blocks(df)
    return generate_matches(blocks, df)
