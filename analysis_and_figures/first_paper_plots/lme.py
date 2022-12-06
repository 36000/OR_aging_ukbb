import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import numpy as np
from tqdm import tqdm
import os.path as op
import altair as alt
import statsmodels.api as sm

font_size = 15

n_boot = 1000
tp = pd.read_csv("/output/tract_profiles_wide.csv")
tp = tp[(tp.nodeID >= 20) & (tp.nodeID < 80)]
do_oab = False

bundle_names_formal = {
    "fov_L": "Fov. OR left",
    "fov_R": "Fov. OR right",
    "mac_L": "Mac. OR left",
    "mac_R": "Mac. OR right",
    "periph_L": "Per. OR left",
    "periph_R": "Per. OR right",
    "CST_L": "CST left",
    "CST_R": "CST right",
    "UNC_L": "UNC left",
    "UNC_R": "UNC right"
}

b_order = [
    "fov_L", "fov_R", "mac_L", "mac_R",
    "periph_L", "periph_R",
    "CST_L", "CST_R", "UNC_L", "UNC_R"]
b_order = [bundle_names_formal[bb] for bb in b_order]

c_range=[
    '#750404','#750405', '#D12828', '#D12829',
    '#FA6161', '#FA6162',
    '#071bf5', '#071bf6', '#26d9fc', '#26d9fd']

pheno = pd.read_csv("output/pheno.csv", low_memory=False)
pheno = pheno[
    (pheno["6148-2.0"] == -7)
    | (pheno["6148-3.0"] == -7)]
print(f"To start: {len(tp)//60}")
tp = tp[tp.subjectID.isin(pheno.eid.unique())]
print(f"After filtering to self-ID'd healthy eyes: {len(tp)//60}")
pheno = pheno[~(
    (pheno["5208-0.0"] >= 0.3) | (pheno["5201-0.0"] >= 0.3) |
    (pheno["5208-1.0"] >= 0.3) | (pheno["5201-1.0"] >= 0.3))]
tp = tp[tp.subjectID.isin(pheno.eid.unique())]
print(f"After filtering to logmar<0.3: {len(tp)//60}")
if do_oab:
    do_oab_suffix = "_oab"
    for bundle in bundle_names_formal.keys():
        tp = tp[~tp[f'dki_fa_{bundle}'].isna()]
    print(f"After filtering to all bundles found: {len(tp)//60}")
else:
    do_oab_suffix = "" 

def to_long(to_df, for_save=False):
    new_df = pd.DataFrame()
    for jj, scalar in enumerate(tqdm(["dki_fa", "dki_md", "dki_mk"])):
        for kk, side in enumerate(tqdm(["L", "R"], leave=False)):
            for ii, subbundle in enumerate([
                    "fov", "mac", "periph", "CST", "UNC"]):
                to_df_this = to_df[~np.isnan(to_df[f"{scalar}_{subbundle}_{side}"])]
                these_means = []
                these_subids = []
                these_ages = []
                for sub_id in to_df_this.subjectID.unique():
                    sub_df = to_df_this[to_df_this.subjectID == sub_id]
                    this_mean = np.mean(sub_df[f"{scalar}_{subbundle}_{side}"].to_numpy())
                    if scalar == "dki_md":
                        this_mean = this_mean*1000
                    these_means.append(this_mean)
                    these_subids.append(sub_id)
                    these_ages.append(sub_df["age"].iloc[0])
                if for_save:
                    new_df = pd.concat([new_df, pd.DataFrame({
                        f"mean_{scalar[-2:].upper()}": these_means,
                        "subjectID": these_subids,
                        "age": these_ages,
                        "side": side,
                        "subbundle": subbundle,
                    })], ignore_index=True)
                else:
                    new_df = pd.concat([new_df, pd.DataFrame({
                        "Sub-bundle": bundle_names_formal[f"{subbundle}_{side}"],
                        f"Mean {scalar[-2:].upper()}": these_means,
                        "subjectID": these_subids,
                        "Tissue Property": scalar[-2:].upper(),
                    })], ignore_index=True)
    return new_df

if False or not op.exists(f"/output/long_tract_profiles{do_oab_suffix}.csv"):
    to_long(tp, True).to_csv(f"/output/long_tract_profiles{do_oab_suffix}.csv")

if True or not op.exists(f"/output/age_coefs{do_oab_suffix}.npy"):
    coefs = np.zeros((3, 10, 2))
    for ii, scalar in enumerate(["dki_fa", "dki_md", "dki_mk"]):
        for jj, subbundle in enumerate(["fov", "mac", "periph", "CST", "UNC"]):
            for kk, side in enumerate(["L", "R"]):
                tp_this = tp[~np.isnan(tp[f"{scalar}_{subbundle}_{side}"])]
                meaned_vals = tp_this.groupby('subjectID', as_index=False)['age', f"{scalar}_{subbundle}_{side}"].mean()
                X = sm.add_constant(meaned_vals["age"].to_numpy().reshape(-1, 1))
                Y = meaned_vals[f"{scalar}_{subbundle}_{side}"].to_numpy()
                ols_result = sm.OLS(Y, X).fit()
                coefs[ii, jj*2+kk, 0] = ols_result.params[1]
                coefs[ii, jj*2+kk, 1] = ols_result.bse[1]
    np.save(f"/output/age_coefs{do_oab_suffix}.npy", coefs)
coefs = np.load(f"/output/age_coefs{do_oab_suffix}.npy")
coefs[1, ...] = coefs[1, ...] * 1000. # put md in reasonable range

# this is bar plot
df = pd.DataFrame()
for jj, scalar in enumerate(["dki_fa", "dki_md", "dki_mk"]):
    for kk, side in enumerate(["L", "R"]):
        for ii, subbundle in enumerate([
                "fov", "mac", "periph", "CST", "UNC"]):
            this_coef = coefs[jj, ii*2+kk]
            # this_mean = np.mean(this_coef)
            # this_low, this_high = st.t.interval(
            #     0.95, this_coef.shape[0]-1,
            #     loc=this_mean, scale=st.sem(this_coef)
            # )
            this_df = pd.DataFrame({
                "Sub-bundle": [bundle_names_formal[f"{subbundle}_{side}"]],
                "Mean TP/year mean": [this_coef[0]],
                "Mean TP/year": [this_coef[0] - 1.96*this_coef[1]],
                "Mean TP/year max": [this_coef[0] + 1.96*this_coef[1]],
                "Tissue Property": [scalar[-2:].upper()]
            })
            df = pd.concat([df, this_df], ignore_index=True)

bars = alt.Chart().mark_bar().encode(
    x=alt.X('Sub-bundle:O', sort=b_order),
    y=alt.Y('Mean TP/year mean:Q'),
    color=alt.Color(
        'Sub-bundle:N',
        sort=b_order,
        scale=alt.Scale(
            domain=b_order,
            range=c_range
        )),
)

error_bars = alt.Chart().mark_errorbar().encode(
    x=alt.X("Sub-bundle:O", sort=b_order),
    y="Mean TP/year:Q",
    y2="Mean TP/year max:Q",
    strokeWidth=alt.value(3)
)

chart = alt.layer(bars, error_bars, data=df).facet(
    column=alt.Column('Tissue Property:N', header=alt.Header(labelFontSize=font_size), title=None)
).resolve_scale(y=alt.ResolveMode("independent"))
chart.configure_axis(
    labelFontSize=font_size,
    titleFontSize=font_size).configure_legend(
        labelFontSize=font_size,
        titleFontSize=font_size,
    ).configure_title(
        fontSize=font_size,
        ).save(f"/output/first_paper_plots/lme_regress{do_oab_suffix}.html")



# this is violin plot
low_age_tp = tp[tp.age_bin == "45-51"]
# low_age_tp = tp[tp.age_bin == "72-81"]
df = to_long(low_age_tp)


font_size = 25
violins = []
for scalar in ["FA", "MD", "MK"]:
    to_label = scalar == "FA"
    
    violin = alt.Chart().transform_density(
        f'Mean {scalar}',
        as_=[f'Mean {scalar}', f'density {scalar}'],
        groupby=['Sub-bundle'],
        # extent=[0, 1.4],
    ).mark_area(orient='horizontal').encode(
        y=f'Mean {scalar}:Q',
        color=alt.Color(
            'Sub-bundle:N',
            sort=b_order,
            scale=alt.Scale(
                domain=b_order,
                range=c_range
            )),
        x=alt.X(
            f'density {scalar}:Q',
            stack='center',
            impute=None,
            title=None,
            axis=alt.Axis(labels=False, values=[0],grid=False, ticks=True),
        )).properties(width=100)

    boxplot = alt.Chart().mark_boxplot(color='black').encode(
        alt.Y(f'Mean {scalar}')
    ).properties(width=200)

    points = alt.Chart().mark_point(
        filled=True,
        color='white'
    ).encode(
        y=alt.Y(f'mean(Mean {scalar}):Q')
    )

    error_bars = alt.Chart().mark_errorbar(
        extent='ci'
    ).encode(
        y=alt.Y(f'Mean {scalar}:Q')
    )

    violins.append(alt.layer(
        violin, boxplot,
        data=df).facet(
            column=alt.Column(
                'Sub-bundle:N',
                header=alt.Header(
                    labels=to_label,
                    titleOrient='bottom',
                    labelOrient='bottom',
                    labelPadding=0,
                    labelAngle=45,
                    labelFontSize=font_size
                ),
                sort=b_order,
                title=None
    )).resolve_scale(x=alt.ResolveMode("independent")))

alt.VConcatChart(vconcat=violins).configure_view(
    stroke=None
).configure_facet(
    spacing=0,
).configure_axis(
    labelFontSize=font_size,
    titleFontSize=font_size
).configure_legend(
    labelFontSize=font_size,
    titleFontSize=font_size,
    titleLimit=0,
    labelLimit=0
).configure_title(
    fontSize=font_size
).save(f"/output/first_paper_plots/lme_average{do_oab_suffix}.html")
