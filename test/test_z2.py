import pytest
import pandas as pd
from collections import defaultdict
from dedup_z2 import generate_blocking_key_name, create_blocks, generate_matches
from main import evaluate

# Beispiel Daten für Tests
sample_data_2 = {
    'id': [172465, 1013447, 861311, 872146, 407909, 1179386, 763069, 952626, 266834, 291742, 
           70559, 496987, 583367, 988646, 478036, 764047, 622954, 1094594, 634147, 1078676, 
           112282, 945203, 302931, 724592, 245272, 341556, 457176, 1056147, 466923, 892699,
           266166, 706199, 158654, 902740, 276098, 283733, 601268, 856719],
    'name': [
        "Carte - Memoria DataTraveler 32 Class - microSDHC - up File U3, ?erná",
        "CARTE - MEMORIA DATATRAVELER 32 CLASS - MICROSDHC - UP FILE U3, ?ERNÁ",
        "sandisk extreme sdxc 128gb, 90mb/s v30, uhs-i u3",
        "Karta pami?ci SANDISK Extreme SDXC 128GB",
        "samsung pro mb-mg32da/eu - tarjeta de memoria micro sdhc de 32 gb (uhs -i grade 1, clase 10, con adaptador sd): amazon.es: informática",
        "Samsung microSDHC 32GB Pro 90MB/s + adapter",
        "SANDISK N°282 GB, MEDIA - SDHC 64 16 CLASS X-SERIES TRAVELER",
        "SanDisk n°282 Traveler Class - SDHC 64 16 Media X-series GB,",
        "Memoria Lexar microSDHC High Speed 32GB sin adaptador",
        "Lexar High-Performance 32GB Class 10 UHS-I 300x Speed (45MB/s) MicroSDHC Flash Memory Card with SD Card Adapter",
        "Kingston Technology Secure Digital Memory Card 32GB SDHC Class 4 SD4/32GB",
        "Kingston - carte mémoire flash - 32 Go - SDHC",
        "SanDisk Ultra A1 MicroSD 64GB 100MB/s UHS-I Memory Card with Adapter",
        "SanDisk Ultra 64GB microSDXC + adapter SD",
        "SanDisk Cruzer Glide 64 GB USB-Stick",
        "SANDISK Cruzer® Glide™ SDCZ60-064G-B35 64 GB USB Flash-Laufwerk",
        "SANDISK Cruzer Blade, USB-Stick, USB 2.0, 32 GB",
        "Sandisk Cruzer Blade (32GB) USB-Speicherstick",
        "SANDISK microSDHC 32GB bis zu 80 MB/Sek., UHS-I/Class 10",
        "Tarjeta de memoria SanDisk Ultra MicroSDHC Clase 10 con adaptador de 32 GB",
        "Sony Extra PRO SDXC UHS-II U3 64GB",
        "sony sf64m, sd full size sd speicherkarte, gb, 260 mb/s",
        "Pendrive direct: SDXC X GB PRO SD 2.0 Sddd3-128G-G46 MINIPRICE",
        "PENDRIVE DIRECT: SDXC X GB PRO 2.0 SDDD3-128G-G46 MINIPRICE",
        "sandisk sdsqxxg-128g-gn6ma 128gb microsdxc uhs-i 3 memoria flash - memoria flash en fnac.es",
        "Sandisk 128GB Extreme PRO microSDXC + SD Adapter | Wex Photo Video",
        "LEXAR MICRO XQD 1000X ULTRA UHS - RDR 128 U3 UHS",
        "Lexar micro XQD 1000x ultra UHS - RDR 128 U3 UHS",
        "MEMORIA DE 64GB 8GB, 1000X 2.0 MEMORY",
        "Memoria de 64GB 8GB, 1000x 2.0 GB Memory",
        "SanDisk Extreme PRO 16 GB SDHC UHS-I Memory Card - Frustation-Free Packaging",
        "Sandisk CARTM EXTPRO SDHC16G (1321854)",
        "kingston pami?ci flair, gb 32 gb (3.1 sd sdhc r130",
        "Kingston SDHC Flair, 32 GB (3.1 SD pami?ci R130",
        "toshiba transmemory u202 flash drive 16 gb (vit) - minneskort",
        "PENDRIVE BLANCO TOSHIBA WHITE, U202 16GB TRANSMEMORY 2.0, USB",
        "Sandisk Cruzer Blade - Memoria USB de 2.0 de 64 GB, negro,SanDisk,SDCZ50-064G-B35",
        "Clé USB Sandisk Cruzer Blade 64GB 64Go USB 2.0 Type A Noir, Rouge lecteur USB flash (MK179474152)"
    ],
    'price': [17.29, 11.99, 387.99, 219.0, 22.99, 119.0, 8.99, 11.14, 17.99, None, 
              None, 150.0, 24.99, 159.99, 23.27, 29.99, 10.99, 15.99, 19.99, 16.9, 
              99.9, 100.99, 24.9, 15.99, None, 67.95, 4.99, 4.99, 22.99, 22.97, 
              None, None, 42.99, 39.99, 132.99, None, 20.94, 30.85],
    'brand': [None, None, "SANDISK", "Karta", None, None, "SanDisk", "SanDisk", None, None, 
              None, "Kingston", None, None, "Sandisk", None, None, None, None, "SanDisk", 
              None, None, None, None, None, "Sandisk", "Lexar", "Lexar", None, None, 
              None, None, "Kingston", "Kingston", None, None, None, None],
    'description': [None, None, None, None, None, None, None, None, None, None, 
                    None, "Kingston - carte mémoire flash - 32 Go - SDHC. Carte SD. Remise 5% pour les adhérents. Achetez vos produits high-tech (ordinateur, ipad, accessoires informatique) en ligne et retirez-les en magasin.", 
                    None, None, None, None, None, None, None, None, 
                    None, None, None, None, None, None, None, None, 
                    None, None, None, None, None, None, None, None, None, None],
    'category': [None, None, "Startsida > Foto & Drönare > Minneskort", None, None, None, None, None, None, None, 
                 None, None, None, None, None, None, None, None, None, None, 
                 None, None, None, None, None, None, None, None, 
                 None, None, None, None, None, None, None, None, None, None]
}

known_key = ['sandisk sdxc', 'sandisk 128 extreme sdxc', 'sandisk 128gb', 'samsung 32', 'sdhc 64', 'sandisk sdhc', 'sandisk 282', 'sandisk 282 sdhc', 
             'sandisk 16 64 ndeg282', 'sandisk ', 'sandisk  sdhc', 'speed 32', 'lexar ', 'lexar 32', 'lexar 32 ', 'lexar 32gb', 
             'class 10 i 300 performance 32', 'lexar 45 class10 uhsi', 'lexar 32 uhsi', '4 sd4 card 32', 'kingston class4 sdhc', 'kingston 32 432', 
             'kingston 32 432 sdhc', 'kingston 32gb sd432gb', 'kingston sdhc', 'kingston 32', 'kingston 32 sdhc', 'gb 100 microsd 64 ultra a1', 
             'sandisk 100 uhsi', 'sandisk 64', 'sandisk 64 uhsi ultra', 'sandisk 100mb 64gb a1', '+ 64gb adapter microsdxc sandisk sd ultra', 
             'ultra 64', 'sandisk 64 ultra', 'sandisk 64gb', 'glide 64', 'sandisk 64 cruzer glide', 'sandisk 32gb', 'sandisk 80 uhsi', 'sandisk 32 uhsi', 
             'sandisk 32 class10', 'ii u3', 'sony sdxc u3 uhsii', 'sony 64', 'sony 64 sdxc uhsii', 'sony 64gb u3', 
             'gn6ma 128', 'sandisk uhsi', 'sdsqxxg-128g-gn6ma', 'sandisk 128 uhsi', 'rdr 128 xqd 1000', 'lexar u3', 'lexar  ultra xqd', 
             'pro 16', 'extpro sdhc16', 'sandisk 16 sdhc', 'kingston 32 r130', 'ci r130', 
             'drive 16 transmemory u202', 'toshiba ', 'u202', 'toshiba 16', 'toshiba 16' ]

df = pd.DataFrame(sample_data_2)

ground_truth_data_2 = {
    'lid': [172465, 861311, 407909, 763069, 266834, 70559, 583367, 478036, 622954, 634147, 112282, 302931, 245272, 457176, 466923],
    'rid': [1013447, 872146, 1179386, 952626, 291742, 496987, 988646, 764047, 1094594, 1078676, 945203, 724592, 341556, 1056147, 892699]
}

ground_truth = pd.DataFrame(ground_truth_data_2)

# Test für generate_blocking_key_name
def test_generate_blocking_key_name():
    row = df.iloc[0]
    _, pattern2id_2 = generate_blocking_key_name(row)
    assert ' u3' in pattern2id_2

# Test für create_blocks
def test_create_blocks():
    blocks = create_blocks(df)
    assert isinstance(blocks, defaultdict)
    assert len(blocks) > 0
    # Überprüfen ob bestimmte Block-Schlüssel existieren
    keys = list(blocks.keys())
    print(keys)
    for key in known_key:
        assert key in keys

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
    assert (172465, 1013447) in matches

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





# import pytest
# import pandas as pd
# from collections import defaultdict
# from dedup_z2 import (
#     generate_blocking_key_name, create_blocks, generate_matches, 
#     x2_clean_data, x2_find_model_num, x2_find_brand, x2_find_models_and_type, x2_find_memcapacity
# )
# from main import evaluate

# # Example data for testing
# sample_data_2 = {
#     'id': [172465, 1013447, 861311, 872146, 407909, 1179386, 763069, 952626, 266834, 291742, 
#            70559, 496987, 583367, 988646, 478036, 764047, 622954, 1094594, 634147, 1078676, 
#            112282, 945203, 302931, 724592, 245272, 341556, 457176, 1056147, 466923, 892699,
#            266166, 706199, 158654, 902740, 276098, 283733, 601268, 856719],
#     'name': [
#         "Carte - Memoria DataTraveler 32 Class - microSDHC - up File U3, ?erná",
#         "CARTE - MEMORIA DATATRAVELER 32 CLASS - MICROSDHC - UP FILE U3, ?ERNÁ",
#         "sandisk extreme sdxc 128gb, 90mb/s v30, uhs-i u3",
#         "Karta pami?ci SANDISK Extreme SDXC 128GB",
#         "samsung pro mb-mg32da/eu - tarjeta de memoria micro sdhc de 32 gb (uhs -i grade 1, clase 10, con adaptador sd): amazon.es: informática",
#         "Samsung microSDHC 32GB Pro 90MB/s + adapter",
#         "SANDISK N°282 GB, MEDIA - SDHC 64 16 CLASS X-SERIES TRAVELER",
#         "SanDisk n°282 Traveler Class - SDHC 64 16 Media X-series GB,",
#         "Memoria Lexar microSDHC High Speed 32GB sin adaptador",
#         "Lexar High-Performance 32GB Class 10 UHS-I 300x Speed (45MB/s) MicroSDHC Flash Memory Card with SD Card Adapter",
#         "Kingston Technology Secure Digital Memory Card 32GB SDHC Class 4 SD4/32GB",
#         "Kingston - carte mémoire flash - 32 Go - SDHC",
#         "SanDisk Ultra A1 MicroSD 64GB 100MB/s UHS-I Memory Card with Adapter",
#         "SanDisk Ultra 64GB microSDXC + adapter SD",
#         "SanDisk Cruzer Glide 64 GB USB-Stick",
#         "SANDISK Cruzer® Glide™ SDCZ60-064G-B35 64 GB USB Flash-Laufwerk",
#         "SANDISK Cruzer Blade, USB-Stick, USB 2.0, 32 GB",
#         "Sandisk Cruzer Blade (32GB) USB-Speicherstick",
#         "SANDISK microSDHC 32GB bis zu 80 MB/Sek., UHS-I/Class 10",
#         "Tarjeta de memoria SanDisk Ultra MicroSDHC Clase 10 con adaptador de 32 GB",
#         "Sony Extra PRO SDXC UHS-II U3 64GB",
#         "sony sf64m, sd full size sd speicherkarte, gb, 260 mb/s",
#         "Pendrive direct: SDXC X GB PRO SD 2.0 Sddd3-128G-G46 MINIPRICE",
#         "PENDRIVE DIRECT: SDXC X GB PRO 2.0 SDDD3-128G-G46 MINIPRICE",
#         "sandisk sdsqxxg-128g-gn6ma 128gb microsdxc uhs-i 3 memoria flash - memoria flash en fnac.es",
#         "Sandisk 128GB Extreme PRO microSDXC + SD Adapter | Wex Photo Video",
#         "LEXAR MICRO XQD 1000X ULTRA UHS - RDR 128 U3 UHS",
#         "Lexar micro XQD 1000x ultra UHS - RDR 128 U3 UHS",
#         "MEMORIA DE 64GB 8GB, 1000X 2.0 MEMORY",
#         "Memoria de 64GB 8GB, 1000x 2.0 GB Memory",
#         "SanDisk Extreme PRO 16 GB SDHC UHS-I Memory Card - Frustation-Free Packaging",
#         "Sandisk CARTM EXTPRO SDHC16G (1321854)",
#         "kingston pami?ci flair, gb 32 gb (3.1 sd sdhc r130",
#         "Kingston SDHC Flair, 32 GB (3.1 SD pami?ci R130",
#         "toshiba transmemory u202 flash drive 16 gb (vit) - minneskort",
#         "PENDRIVE BLANCO TOSHIBA WHITE, U202 16GB TRANSMEMORY 2.0, USB",
#         "Sandisk Cruzer Blade - Memoria USB de 2.0 de 64 GB, negro,SanDisk,SDCZ50-064G-B35",
#         "Clé USB Sandisk Cruzer Blade 64GB 64Go USB 2.0 Type A Noir, Rouge lecteur USB flash (MK179474152)"
#     ],
#     'price': [17.29, 11.99, 387.99, 219.0, 22.99, 119.0, 8.99, 11.14, 17.99, None, 
#               None, 150.0, 24.99, 159.99, 23.27, 29.99, 10.99, 15.99, 19.99, 16.9, 
#               99.9, 100.99, 24.9, 15.99, None, 67.95, 4.99, 4.99, 22.99, 22.97, 
#               None, None, 42.99, 39.99, 132.99, None, 20.94, 30.85],
#     'brand': [None, None, "SANDISK", "Karta", None, None, "SanDisk", "SanDisk", None, None, 
#               None, "Kingston", None, None, "Sandisk", None, None, None, None, "SanDisk", 
#               None, None, None, None, None, "Sandisk", "Lexar", "Lexar", None, None, 
#               None, None, "Kingston", "Kingston", None, None, None, None],
#     'description': [None, None, None, None, None, None, None, None, None, None, 
#                     None, "Kingston - carte mémoire flash - 32 Go - SDHC. Carte SD. Remise 5% pour les adhérents. Achetez vos produits high-tech (ordinateur, ipad, accessoires informatique) en ligne et retirez-les en magasin.", 
#                     None, None, None, None, None, None, None, None, 
#                     None, None, None, None, None, None, None, None, 
#                     None, None, None, None, None, None, None, None, None, None],
#     'category': [None, None, "Startsida > Foto & Drönare > Minneskort", None, None, None, None, None, None, None, 
#                  None, None, None, None, None, None, None, None, None, None, 
#                  None, None, None, None, None, None, None, None, 
#                  None, None, None, None, None, None, None, None, None, None]
# }


# df_2 = pd.DataFrame(sample_data_2)

# ground_truth_data_2 = {
#     'lid': [172465, 861311, 407909, 763069, 266834, 70559, 583367, 478036, 622954, 634147, 112282, 302931, 245272, 457176, 466923],
#     'rid': [1013447, 872146, 1179386, 952626, 291742, 496987, 988646, 764047, 1094594, 1078676, 945203, 724592, 341556, 1056147, 892699]
# }

# ground_truth_2 = pd.DataFrame(ground_truth_data_2)

# # Test for x2_clean_data
# def test_x2_clean_data():
#     name = "SanDisk 64GB Ultra USB 3.0 Flash Drive"
#     cleaned_name = x2_clean_data(name)
#     assert cleaned_name == "sandisk 64gb ultra usb3.0 flash drive"

# # Test for x2_find_model_num
# def test_x2_find_model_num():
#     name = "Lexar High-Performance 32GB Class 10 UHS-I 300x Speed (45MB/s) MicroSDHC Flash Memory Card with SD Card Adapter",
#     # name = "SanDisk 64GB Ultra USB 3.0 Flash Drive"
#     cleaned_name = x2_clean_data(name)
#     model_num = x2_find_model_num(cleaned_name)
#     assert model_num == "class10"

# # Test for x2_find_brand
# def test_x2_find_brand():
#     name = "SanDisk 64GB Ultra USB 3.0 Flash Drive"
#     cleaned_name = x2_clean_data(name)
#     brand = x2_find_brand(cleaned_name)
#     assert brand == "sandisk"

# # Test for x2_find_models_and_type
# def test_x2_find_models_and_type():
#     name = "SanDisk 64GB Ultra USB 3.0 Flash Drive"
#     cleaned_name = x2_clean_data(name)
#     model_type = x2_find_models_and_type(cleaned_name)
#     assert model_type == "ultra"

# # Test for x2_find_memcapacity
# def test_x2_find_memcapacity():
#     name = "SanDisk 64GB Ultra USB 3.0 Flash Drive"
#     cleaned_name = x2_clean_data(name)
#     mem_capacity = x2_find_memcapacity(cleaned_name)
#     assert mem_capacity == "64"

# # Test for generate_blocking_key_name
# def test_generate_blocking_key_name():
#     row = df_2.iloc[0]
#     pattern2id_1, pattern2id_2 = generate_blocking_key_name(row)
#     assert len(pattern2id_1) > 0
#     assert len(pattern2id_2) > 0

# # Test for create_blocks
# def test_create_blocks():
#     blocks = create_blocks(df_2)
#     assert isinstance(blocks, defaultdict)
#     assert len(blocks) > 0

# # Test for create_blocks with empty DataFrame
# def test_create_blocks_empty():
#     empty_df = pd.DataFrame(columns=['id', 'name'])
#     blocks = create_blocks(empty_df)
#     assert isinstance(blocks, defaultdict)
#     assert len(blocks) == 0

# # Test for generate_matches
# def test_generate_matches():
#     blocks = create_blocks(df_2)
#     matches = generate_matches(blocks, df_2)
#     assert isinstance(matches, list)
#     assert len(matches) > 0
#     # Check if certain pairs are in the results
#     assert (172465, 1013447) in matches
#     assert(457176, 1056147) in matches

# # Test for generate_matches with empty DataFrame
# def test_generate_matches_empty():
#     empty_df = pd.DataFrame(columns=['id', 'name'])
#     blocks = create_blocks(empty_df)
#     matches = generate_matches(blocks, empty_df)
#     assert isinstance(matches, list)
#     assert len(matches) == 0

# # Test for evaluate
# def test_evaluate():
#     blocks = create_blocks(df_2)
#     matches = generate_matches(blocks, df_2)
#     tp, fp, fn, recall, precision = evaluate(matches, ground_truth_2)
#     assert tp >= 0
#     assert fp >= 0
#     assert fn >= 0
#     assert 0 <= recall <= 1
#     assert 0 <= precision <= 1

# # Test for evaluate with empty DataFrame
# def test_evaluate_empty():
#     empty_df = pd.DataFrame(columns=['id', 'name'])
#     ground_truth_empty = pd.DataFrame(columns=['lid', 'rid'])
#     blocks = create_blocks(empty_df)
#     matches = generate_matches(blocks, empty_df)
#     tp, fp, fn, recall, precision = evaluate(matches, ground_truth_empty)
#     assert tp == 0
#     assert fp == 0
#     assert fn == 0
#     assert recall == 0
#     assert precision == 0

# if __name__ == '__main__':
#     pytest.main()
