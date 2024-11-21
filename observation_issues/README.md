The python3 valid_true_ground_z1 script performs data cleaning and de-duplication on the dataset Z1. The script outputs two files:

- Z1_cleaned_sub_blocks:
    This file contains thousands of blocks that categorize entries based on applied regex patterns, grouping duplicates with high similarity. Data cleaning is performed to denoise the data, essential for the Z1 dataset. This process does not capture all duplicates but covers a vast majority. Entries that occur only once after applying the patterns are discarded, indicating no multiple entries (duplicates).

- z1_true_matches:
     This file contains collected and grouped IDs from each block. It avoids comparing each entry in Z1 individually, saving considerable computational time.

Issues and Observations
Precision Improvement Attempts: We tried to improve precision in dedup_z1. However, we observed that the ZY1.csv might be incomplete or incorrect. Through valid_true_ground_z1, it is evident that there are more duplicate blocks or pairs in Z1 than initially identified.

Incomplete True Matches: It is certain that z1_true_matches does not contain all possible duplicate pairs/blocks. There may be more duplicates than currently captured.

High Precision Limitation: Despite our efforts, achieving high precision is challenging. We found almost double the number of duplicates compared to the original ground truth, indicating that the dataset Z1 has more duplicates than initially expected.

To run the valid_true_ground_z1 script, change into the observation_issues directory and execute the script.

NOTE:
When executing, loading bar will appear in ca 1 min.