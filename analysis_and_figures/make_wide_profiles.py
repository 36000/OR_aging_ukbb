import pandas as pd
import os.path as op
from tqdm import tqdm

pheno = pd.read_csv("output/pheno.csv", low_memory=False)

if True or not op.exists("output/deriv_csvs/sorted_subs.csv"):
    profiles = pd.read_csv("output/tract_profiles.csv")
    age_bins = []
    profiles["age_bin"] = ""
    profiles["age"] = 0
    for _, row in pheno.iterrows():
        age_bin = int(row["21003-2.0"])
        age_bin = age_bin - age_bin % 4
        if age_bin >= 72:
            age_bin = "72-81"
        elif age_bin < 52:
            age_bin = "45-51"
        else:
            age_bin = f"{age_bin}-{age_bin+3}"
        age_bins.append(age_bin)
        profiles.loc[profiles["subjectID"] == row["eid"], "age_bin"] = age_bin
        profiles.loc[profiles["subjectID"] == row["eid"], "age"] = int(row["21003-2.0"])
    profiles.sort_values("age", kind="mergesort", inplace=True)
    profiles.to_csv("output/deriv_csvs/sorted_subs.csv")

bundle_spec = {0:"CST_L", 1:"CST_R", 2:"UNC_L", 3:"UNC_R", 4:"fov_L", 5:"fov_R", 6:"mac_L", 7:"mac_R", 8:"periph_L", 9:"periph_R"}

rel_vals = ["dki_fa", "dki_md", "dki_mk"]

profiles = pd.read_csv("output/deriv_csvs/sorted_subs.csv")
for bundle_name in profiles["tractID"].unique():
    if bundle_name not in [*bundle_spec.values(), "perip_L", "perip_R"]:
        raise ValueError(bundle_name)

age_bins = profiles[["subjectID", "age_bin", "age"]].drop_duplicates()
pheno_df = pd.DataFrame(columns=["subjectID", "sex", "acuity_l", "acuity_r", "site"])
for subject in tqdm(age_bins.subjectID.unique()):
    sex = pheno[pheno.eid == subject]["31-0.0"].iloc[0]
    acuity_l = pheno[pheno.eid == subject]["5201-0.0"].iloc[0]
    acuity_r = pheno[pheno.eid == subject]["5208-0.0"].iloc[0]
    site = pheno[pheno.eid == subject]["54-2.0"].iloc[0]
    pheno_df = pheno_df.append({
        "subjectID": subject, "sex": sex,
        "acuity_l": acuity_l,
        "acuity_r": acuity_r,
        "site": site}, ignore_index=True)

profiles = profiles.loc[:, ~profiles.columns.str.contains('^Unnamed')]
profiles = profiles.pivot_table(index=["subjectID", "nodeID"], columns=["tractID"], values=rel_vals).reset_index()
print(profiles)

# for bundle in bundle_spec.values():
#     for scalar in rel_vals:
#         profiles.loc[:, (scalar, bundle)] = profiles[scalar, bundle].fillna(profiles[scalar, bundle].mean())

profiles.to_csv("output/tract_profiles_wide.csv", index=False)
profiles = pd.read_csv("output/tract_profiles_wide.csv").iloc[1: , :]

profiles = profiles.merge(age_bins, on="subjectID")
profiles = profiles.merge(pheno_df, on="subjectID")
print(profiles)

dtypes = {}
for key, bundle_name in bundle_spec.items():
    for scalar in rel_vals:
        if key == 0:
            profiles = profiles.rename(columns={scalar: f"{scalar}_{bundle_name}"})
        else:
            profiles = profiles.rename(columns={f"{scalar}.{key}": f"{scalar}_{bundle_name}"})

profiles.to_csv("output/tract_profiles_wide.csv", index=False)
