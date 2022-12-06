import pandas as pd
import numpy as np
from tqdm import tqdm

glauc = False
if glauc:
    suf = "_glauc"
else:
    suf = ""

subjects = pd.read_csv(f"output/tract_profiles{suf}.csv", dtype={"subjectID": int}, skipinitialspace=True, usecols=["subjectID"])["subjectID"].unique()

pheno = pd.read_csv("pheno/ukb41257.csv", low_memory=False, chunksize=10000)
print("Unique subjects: " + str(subjects))
print(len(subjects))
filtered_pheno = pheno.get_chunk(0).iloc[0:0,:].copy()
for chunk in tqdm(pheno):
    _, inter_loc, _ = np.intersect1d(chunk['eid'].astype(int), subjects.astype(int), assume_unique=True, return_indices=True)
    if len(inter_loc) > 0:
        filtered_pheno = filtered_pheno.append(chunk.iloc[inter_loc])
filtered_pheno.to_csv(f"output/pheno{suf}.csv")
print(filtered_pheno)

