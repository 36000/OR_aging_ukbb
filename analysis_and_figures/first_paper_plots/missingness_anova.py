import pandas as pd
import numpy as np
import os.path as op

import rpy2
from rpy2 import robjects
import rpy2.robjects as ro
from rpy2.robjects.conversion import localconverter
from rpy2.robjects import pandas2ri
pandas2ri.activate()  # make pyr2 accept and auto-convert pandas dataframes
from rpy2.robjects.packages import importr, data
base = importr('base')
ez = importr('ez')
lme4 = importr('lme4')
robjects.r['options'](warn=-1)


print(rpy2.__version__)

font_size = 20

bundles = ["fov_L", "fov_R",  "mac_L", "mac_R", "periph_L", "periph_R"]
bundle_names = ["FovOR", "FovOR",  "MacOR", "MacOR", "PerOR", "PerOR"]
hemi_names = ["Left", "Right",  "Left", "Right", "Left", "Right"]

tps = ["dki_fa", "dki_md", "dki_mk"]

if True or not op.exists("output/first_paper_plots/fi/missingness.csv"):
    dataframe = pd.read_csv("output/tract_profiles_filt.csv")

    dataframe = dataframe[dataframe["nodeID"] == 49]

    bundle_counts_df = pd.DataFrame()
    for _, row in dataframe.iterrows():
        these_counts = {
            "subjectID": 6*[row["subjectID"]],
            "age": 6*[row["age"]],
            "age_bin": 6*[row["age_bin"]],
        }
        these_counts["is_missing"] = []
        for bundle in bundles:
            these_counts["is_missing"].append(np.isnan(row[f"dki_fa_{bundle}"]))
        these_counts["subbundle"] = bundle_names.copy()
        these_counts["hemi"] = hemi_names.copy()
        bundle_counts_df = pd.concat([
            bundle_counts_df,
            pd.DataFrame(these_counts)], ignore_index=True)

    bundle_counts_df.to_csv("output/first_paper_plots/fi/missingness.csv")

bundle_counts_df = pd.read_csv("output/first_paper_plots/fi/missingness.csv")

bundle_counts_df["is_missing"] = bundle_counts_df["is_missing"].astype(int)
res = ez.ezANOVA(
    data=bundle_counts_df,
    dv=base.as_symbol("is_missing"),
    wid=base.as_symbol('subjectID'),
    within=[base.as_symbol("subbundle"), base.as_symbol("hemi")],
    between=base.as_symbol('age'))
print(res)