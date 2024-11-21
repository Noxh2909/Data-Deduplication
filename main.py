import time
from collections import defaultdict
from tqdm import tqdm
import pandas as pd
import re
import dedup_z2 as ddp2
import ascii_key as ak
import dedup_z1 as ddp1

def evaluate(match_pairs: list, ground_truth: pd.DataFrame):

    gt = list(zip(ground_truth['lid'], ground_truth['rid']))
    tp = len(set(match_pairs).intersection(set(gt)))
    fp = len(set(match_pairs).difference(set(gt)))
    fn = len(set(gt).difference(set(match_pairs)))
    
    recall = 0 if (tp + fn) == 0 else tp / (tp + fn)
    precision = 0 if (tp + fp) == 0 else tp / (tp + fp)
    f1 = 0 if (precision + recall) == 0 else (2 * precision * recall) / (precision + recall)

    print(f'Reported # of Pairs: {len(match_pairs)}')
    print('TP: {}'.format(tp))
    print('FP: {}'.format(fp))
    print('FN: {}'.format(fn))
    print('Recal: {}'.format(recall))
    print('Precision: {}'.format(precision))
    print('F1: {}'.format(f1))

    return tp, fp, fn, recall, precision

if __name__ == "__main__":

  # read the datasets
  Z2 = pd.read_csv("./data/Z2.csv")
  Z1 = pd.read_csv("./data/Z1.csv")
  starting_time = time.time()

  # union the matches
  print('Pattern Matching Z1')
  candidates_pattern1 = ddp1.pattern_key(Z1)
  print('Pattern Matching Z2')
  candidates_pattern2 = ddp2.pattern_key(Z2)
  print('Ascii Matching Z1')
  candidates_ascii1 = ak.ascii_key(Z1, 1)
  print('Ascii Matching Z2')
  candidates_ascii2 = ak.ascii_key(Z2, 2)
  candidates1 = list(set(candidates_ascii1).intersection(set(candidates_pattern1)))
  candidates2 = list(set(candidates_ascii2 + candidates_pattern2 ))

  ending_time = time.time()

  # Evaluation
  print('------------- Evaluation Results --------------')
  print(f'Runtime: {ending_time - starting_time} Seconds')
  print('------------- First Dataset --------------')
  evaluate(candidates1, pd.read_csv('./data/ZY1.csv'))
  print('------------- Second Dataset --------------')
  evaluate(candidates2, pd.read_csv('./data/ZY2.csv'))
