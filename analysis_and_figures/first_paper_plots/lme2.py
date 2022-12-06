import pandas as pd
import numpy as np
from tqdm import tqdm
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

scalars = ["mean_FA", "mean_MD", "mean_MK"]
subbundles = ["fov", "mac", "periph"]
do_oab = False

if do_oab:
    do_oab_suffix = "_oab"
else:
    do_oab_suffix = "" 

long_tp = pd.read_csv(f"/output/long_tract_profiles{do_oab_suffix}.csv")
long_tp = long_tp[long_tp.subbundle.isin(subbundles)]

if do_oab:
    sub_counts = long_tp["subjectID"].value_counts().values
    if not np.all(sub_counts == sub_counts[0]):
        raise ValueError("Unbalanced number of subjects")
else:
    if True or not op.exists(f"/output/long_tract_profiles_imputed.csv"):
        imputers = {}
        for subbundle in tqdm(subbundles):
            sb_tp = long_tp[long_tp.subbundle == subbundle]
            imputers[subbundle] = {}
            for hemi in ["L", "R"]:
                h_tp = sb_tp[sb_tp.side == hemi]
                imputers[subbundle][hemi] = {}
                for scalar in scalars:
                    imputers[subbundle][hemi][scalar] = np.nanmedian(h_tp[scalar].to_numpy())
        print(imputers)
        exists_series = list(long_tp[["subjectID", "subbundle", "side"]].apply(lambda row: '_'.join(row.values.astype(str)), axis=1))
        for subject in tqdm(long_tp.subjectID.unique()):
            age = long_tp[long_tp.subjectID == subject]["age"].iloc[0]
            for subbundle in subbundles: 
                for hemi in ["L", "R"]:
                    if f"{subject}_{subbundle}_{hemi}" not in exists_series:
                        to_concat = pd.DataFrame({
                            "mean_FA": [imputers[subbundle][hemi]["mean_FA"], np.nan, np.nan],
                            "mean_MD": [np.nan, imputers[subbundle][hemi]["mean_MD"], np.nan],
                            "mean_MK": [np.nan, np.nan, imputers[subbundle][hemi]["mean_MK"]],
                            "subjectID": subject,
                            "age": age,
                            "side": hemi,
                            "subbundle": subbundle,
                        })
                        long_tp = pd.concat([long_tp, to_concat], ignore_index=True)
        if len(long_tp[long_tp.subjectID == subject]) != 18:
            raise ValueError()
        long_tp.to_csv(f"/output/long_tract_profiles_imputed{do_oab_suffix}.csv", index=False)
    long_tp = pd.read_csv(f"/output/long_tract_profiles_imputed{do_oab_suffix}.csv")

print(long_tp)

for jj, scalar in enumerate(scalars):
    scalars_to_drop = scalars.copy()
    scalars_to_drop.remove(scalar)
    this_long_tp = long_tp[~np.isnan(long_tp[scalar])].drop(columns=scalars_to_drop)

    res = ez.ezANOVA(
        data=this_long_tp,
        dv=base.as_symbol(f"{scalar}"),
        wid=base.as_symbol('subjectID'),
        within=[base.as_symbol("side"), base.as_symbol("subbundle")],
        between=base.as_symbol('age'))
    print(res)
