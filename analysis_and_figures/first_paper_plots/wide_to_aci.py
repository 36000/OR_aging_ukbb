import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import numpy as np
from tqdm import tqdm
import scipy.stats as st
from itertools import product


# for paper 2:
# dataset = "ukbb"
# use_age_bin = True
# use_another_bin = "glauc"
# filt = False
# low_node = 20
# high_node = 80
# only_all_bundles = False

# for paper 1:
dataset = "ukbb"
use_age_bin = True
use_another_bin = None
filt = True
low_node = 20
high_node = 80
only_all_bundles = False


filenames = {
    "hcp_roi": "output/hcp_data/tract_profiles_wide_roi.csv",
    "hcp_reco": "output/hcp_data/tract_profiles_wide_hcp.csv",
    "hcp_boot_old": "output/hcp_data/tract_profiles_wide_boot.csv",
    "hcp_boot": "output/hcp_data/tract_profiles_wide_ukbb.csv",
    "hcp_bootroi": "output/hcp_data/bootroi_wide.csv",
    "ukbb": "output/tract_profiles_wide.csv"}

if dataset == "hcp_boot_old":
    comparisons = [("L_OR", "R_OR")]
    bundles = ["L_OR", "R_OR", "L_OR_R_OR_aci"]
elif dataset == "ukbb":
    comparisons = [
        ("fov_L", "periph_L"),
        ("fov_L", "fov_R"),
        ("fov_R", "periph_R"),
        ("periph_L", "periph_R"),
        ("fov_L", "mac_L"),
        ("fov_R", "mac_R"),
        ("mac_L", "mac_R"),
        ("CST_L", "CST_R"),
        ("UNC_L", "UNC_R")]
    bundles = [
        "fov_L", "periph_L", "fov_R", "periph_R",
        "mac_L", "mac_R",
        "CST_L", "CST_R", "CST_L_CST_R_aci",
        "UNC_L", "UNC_R", "UNC_L_UNC_R_aci",
        "fov_L_periph_L_aci", "fov_R_periph_R_aci",
        "fov_L_fov_R_aci", "periph_L_periph_R_aci",
        "fov_L_mac_L_aci", "fov_R_mac_R_aci",
        "mac_L_mac_R_aci"]
else:
    comparisons = [
        ("foveal_L", "peripheral_L"),
        ("foveal_L", "foveal_R"),
        ("foveal_R", "peripheral_R"),
        ("peripheral_L", "peripheral_R")]
    bundles = [
        "foveal_L", "peripheral_L", "foveal_R", "peripheral_R",
        "foveal_L_peripheral_L_aci", "foveal_R_peripheral_R_aci",
        "foveal_L_foveal_R_aci", "peripheral_L_peripheral_R_aci"]

dataframe = pd.read_csv(filenames[dataset])
dataframe = dataframe[(dataframe.nodeID >= low_node) & (dataframe.nodeID < high_node)]

if filt:
    pheno = pd.read_csv("output/pheno.csv", low_memory=False)
    pheno = pheno[
        (pheno["6148-2.0"] == -7)
        | (pheno["6148-3.0"] == -7)]
    print(f"To start: {len(dataframe)//60}")
    dataframe = dataframe[dataframe.subjectID.isin(pheno.eid.unique())]
    print(f"After filtering to self-ID'd healthy eyes: {len(dataframe)//60}")
    pheno = pheno[(
        ((pheno["5208-0.0"] <= 0.3) & (pheno["5201-0.0"] <= 0.3)) |
        ((pheno["5208-1.0"] <= 0.3) & (pheno["5201-1.0"] <= 0.3)))]
    dataframe = dataframe[dataframe.subjectID.isin(pheno.eid.unique())]
    print(f"After filtering to logmar<0.3: {len(dataframe)//60}")

if only_all_bundles:
    for bundle in bundles:
        if "aci" not in bundle:
            dataframe = dataframe[~dataframe[f'dki_fa_{bundle}'].isna()]
    print(f"After filtering to all bundles found: {len(dataframe)//60}")

if "acuity_l" in dataframe:
    dataframe = dataframe[~np.isnan(dataframe.acuity_l)]
    bin_split = np.median(dataframe.acuity_l.to_numpy())
    bin_split = round(bin_split, 2)
    print(f"logMAR split: {bin_split}")
    for acuity_bin in [(None, bin_split), (bin_split, None)]:
        if acuity_bin[0] is None:
            dataframe.loc[dataframe.acuity_l <= acuity_bin[1], "acuity_l"] = -1
        elif acuity_bin[1] is None:
            dataframe.loc[dataframe.acuity_l > acuity_bin[0], "acuity_l"] = 1
        else:
            dataframe.loc[
                (dataframe.acuity_l < acuity_bin[1]) &
                (dataframe.acuity_l >= acuity_bin[0]), "acuity_l"] = acuity_bin[0]
    # dataframe.acuity_l.replace({
    #     -0.2:"-0.34,-0.15", -0.15:"-0.15,-0.1",
    #     -0.1:"-0.1,0.0", 0.0:"0.0,0.1", 0.1:"0.1,1.2"}, inplace=True)
    dataframe.acuity_l.replace({
        -1:f"Low logMAR (<={bin_split})", 1:f"High logMAR (>{bin_split})"}, inplace=True)

dis_sub_dict = {
    "glauc": "output/pos_glauc_sub.txt"
}
ctrl_sub_dict = {
    "glauc": "output/matched_glauc_ctrl_sub.txt"
}
if use_another_bin in ["glauc"]:
    dis_subs = np.loadtxt(dis_sub_dict[use_another_bin])
    ctrl_subs = np.loadtxt(ctrl_sub_dict[use_another_bin])
    dataframe[use_another_bin] = 2
    dataframe.loc[dataframe.subjectID.isin(dis_subs), use_another_bin] = 1
    dataframe.loc[dataframe.subjectID.isin(ctrl_subs), use_another_bin] = 0
    dataframe = dataframe[dataframe[use_another_bin] < 2]
    print(dataframe)


for scalar in tqdm(["dki_fa", "dki_md", "dki_mk"]):
    for bundle_a, bundle_b in comparisons:
        column_a = dataframe[f"{scalar}_{bundle_a}"]
        column_b = dataframe[f"{scalar}_{bundle_b}"]
        dataframe[f"{scalar}_{bundle_a}_{bundle_b}_aci"] = 2*(column_a-column_b)/(np.abs(column_a)+np.abs(column_b))

def get_mean_ci(this_bundle):
    this_mean = np.mean(this_bundle)
    this_low, this_high = st.bootstrap(
        (this_bundle,), np.mean, axis=0,
        confidence_level=0.95, n_resamples=10000,
        method="BCa").confidence_interval
    this_low_iqr = np.percentile(this_bundle, 25)
    this_high_iqr = np.percentile(this_bundle, 75)
    return this_mean, this_low, this_high, this_low_iqr, this_high_iqr

new_dataframe = pd.DataFrame()
for nodeID in tqdm(range(low_node, high_node)):
    if use_age_bin:
        bin_ls = dataframe.age_bin.unique()
        if use_another_bin is not None:
            bin_ls = list(product(bin_ls, dataframe[use_another_bin].unique()))
    elif use_another_bin is not None:
        bin_ls = dataframe[use_another_bin].unique()
    else:
        bin_ls = [None]
    for this_bin in tqdm(bin_ls, leave=False):
        this_row = {"nodeID": nodeID}
        if use_age_bin:
            if use_another_bin is not None:
                this_row["age_bin"] = this_bin[0]
                this_row[use_another_bin] = this_bin[1]
            else:
                this_row["age_bin"] = this_bin
        elif use_another_bin is not None:
            this_row[use_another_bin] = this_bin
        for column in tqdm(bundles, leave=False):
            for scalar in tqdm(["dki_fa", "dki_md", "dki_mk"], leave=False):
                c_name = f"{scalar}_{column}"
                if this_bin is None:
                    this_bundle = dataframe[dataframe.nodeID == nodeID][c_name]
                elif use_another_bin is not None and use_age_bin:
                    this_bundle = dataframe[(dataframe.age_bin == this_bin[0]) & (dataframe.nodeID == nodeID) & (dataframe[use_another_bin] == this_bin[1])][c_name]
                elif use_another_bin is None and use_age_bin:
                    this_bundle = dataframe[(dataframe.age_bin == this_bin) & (dataframe.nodeID == nodeID)][c_name]
                else:
                    this_bundle = dataframe[(dataframe[use_another_bin] == this_bin) & (dataframe.nodeID == nodeID)][c_name]
                
                
                this_bundle = this_bundle.to_numpy()
                this_bundle = this_bundle[~np.isnan(this_bundle)]
                if len(this_bundle) > 1:
                    this_row[f"{c_name}_mean"], this_row[f"{c_name}_low_CI"], this_row[f"{c_name}_high_CI"], this_row[f"{c_name}_low_IQR"], this_row[f"{c_name}_high_IQR"] =\
                        get_mean_ci(this_bundle)
        new_dataframe = new_dataframe.append(this_row, ignore_index=True)

if "hcp" in dataset and use_age_bin:
    f_suf = "_binned"
else:
    f_suf = ""

if use_another_bin is not None:
    f_suf = f_suf + f"_{use_another_bin}_binned"

if filt:
    f_suf = f_suf + "_filt"

if only_all_bundles:
    f_suf = f_suf + "_oab"

new_dataframe.to_csv(f"output/aci_for_paper/profiles_w_aci_{dataset}{f_suf}.csv", index=False)
