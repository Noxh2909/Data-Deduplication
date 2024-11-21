import pytest
import pandas as pd
from collections import defaultdict
from dedup_z1 import generate_blocking_key_name, create_blocks, generate_matches
from main import evaluate

# Beispiel Daten für Tests
sample_data = {
    'id': [244752, 562970, 479324, 1165063, 626847, 980490, 407600, 686329, 1160737, 1165529, 79618, 958621, 580720, 989923, 160698, 840632],
    'title': [
        "Miniprice.ca Pavilion ThinkPad S149 6885 14 -",
        "Miniprice.ca Pavilion ThinkPad S149 6885 14 -",
        "LENOVO ELITEBOOK G510 B GOBOOK - 3 COMPUTERS K1100M 128GB 50 DVD | 15 | (4X40E77322) EBAY EBAY W8.1",
        "LENOVO ELITEBOOK G510 B GOBOOK - 3 COMPUTERS K1100M 128GB 50 DVD | 15 | (4X40E77322) EBAY EBAY W8.1",
        "HP 8460p EliteBook Core i5 2520M 2 5GHz 4GB 500GB Webcam Win 7 Aluminium Laptop | eBay",
        "HP 8460p EliteBook Core i5 2520M 2 5GHz 4GB 500GB Webcam Win 7 Aluminium Laptop | eBay",
        "Gateway NXY1UAA045 15.6\" LED (UltraBright) Notebook - Celeron 1005M 1.90 TheNerds.net NE56R52u-10054G50Mnks - - Laptops & Notebooks Notebooks ACER Laptops & - - GHz",
        "Gateway NXY1UAA045 15.6\" LED (UltraBright) Notebook - Celeron 1005M 1.90 TheNerds.net NE56R52u-10054G50Mnks - - Laptops & Notebooks Notebooks ACER Laptops & - - GHz",
        "HP 8440p Laptop Notebook Core i5 2 4GHz 4GB 250GB Win 7 64bit Office Webcam | eBay",
        "HP 8440p Laptop Notebook Core i5 2 4GHz 4GB 250GB Win 7 64bit Office Webcam | eBay",
        "WEBCAM 2 8760W 17 3\" 4GB LAPTOP HP 2620M | EBAY 7GHZ 320GB BLUETOOTH ELITEBOOK CORE I7",
        "WEBCAM 2 8760W 17 3\" 4GB LAPTOP HP 2620M | EBAY 7GHZ 320GB BLUETOOTH ELITEBOOK CORE I7",
        "Lenovo ThinkPad X230 Tablet 3435 - 12.5\" - Core i7 3520M - Windows 7 Pro 64-bit - 4 GB RAM - 500 GB HDD - with UltraBase Series 3 - Vology",
        "Lenovo ThinkPad X230 Tablet 3435 - 12.5\" - Core i7 3520M - Windows 7 Pro 64-bit - 4 GB RAM - 500 GB HDD - with UltraBase Series 3 - Vology",
        "Lenovo ThinkPad X1 Carbon 3460 - 14\" - Core i7 3667U - Windows 8 Pro 64-bit / Windows 7 Pro 64-bit downgrade - 8 GB RAM - 180 GB SSD - Vology",
        "Lenovo ThinkPad X1 Carbon 3460 - 14\" - Core i7 3667U - Windows 8 Pro 64-bit / Windows 7 Pro 64-bit downgrade - 8 GB RAM - 180 GB SSD - Vology"
    ]
}

df = pd.DataFrame(sample_data)

ground_truth_data = {
    'lid': [244752, 479324, 626847, 407600, 1160737, 79618, 580720, 160698],
    'rid': [562970, 1165063, 980490, 686329, 1165529, 958621, 989923, 840632]
}
ground_truth = pd.DataFrame(ground_truth_data)

# Test für generate_blocking_key_name
def test_generate_blocking_key_name():
    row = df.iloc[0]
    _, pattern2id_2 = generate_blocking_key_name(row)
    assert 'pavilion' in pattern2id_2
    assert 's149' in pattern2id_2

# Test für create_blocks
def test_create_blocks():
    blocks = create_blocks(df)
    assert isinstance(blocks, defaultdict)
    assert len(blocks) > 0
    # Überprüfen ob bestimmte Block-Schlüssel existieren
    keys = list(blocks.keys())
    assert '6885 14 thinkpad s149' in keys

# Test für create_blocks mit leerem DataFrame
def test_create_blocks_empty():
    empty_df = pd.DataFrame(columns=['id', 'title'])
    blocks = create_blocks(empty_df)
    assert isinstance(blocks, defaultdict)
    assert len(blocks) == 0

# Test für generate_matches
def test_generate_matches():
    blocks = create_blocks(df)
    matches = generate_matches(blocks, df)
    assert isinstance(matches, list)
    assert len(matches) > 0
    # Überprüfen ob bestimmte Paare in den Ergebnissen sind
    assert (244752, 562970) in matches
    assert (479324, 1165063) in matches

# Test für generate_matches mit leerem DataFrame
def test_generate_matches_empty():
    empty_df = pd.DataFrame(columns=['id', 'title'])
    blocks = create_blocks(empty_df)
    matches = generate_matches(blocks, empty_df)
    assert isinstance(matches, list)
    assert len(matches) == 0

# Test für evaluate
def test_evaluate():
    blocks = create_blocks(df)
    matches = generate_matches(blocks, df)
    tp, fp, fn, recall, precision = evaluate(matches, ground_truth)
    assert tp >= 0
    assert fp >= 0
    assert fn >= 0
    assert 0 <= recall <= 1
    assert 0 <= precision <= 1

# Test für evaluate mit leerem DataFrame
def test_evaluate_empty():
    empty_df = pd.DataFrame(columns=['id', 'title'])
    ground_truth_empty = pd.DataFrame(columns=['lid', 'rid'])
    blocks = create_blocks(empty_df)
    matches = generate_matches(blocks, empty_df)
    tp, fp, fn, recall, precision = evaluate(matches, ground_truth_empty)
    assert tp == 0
    assert fp == 0
    assert fn == 0
    assert recall == 0
    assert precision == 0

if __name__ == '__main__':
    pytest.main()
