import numpy as np
import altair as alt
from altair import datum
import pandas as pd
from altair_transform import transform_chart

pheno = pd.read_csv("output/pheno.csv", low_memory=False)

profile = pd.read_csv("output/tract_profiles_wide.csv", low_memory=False)
low_node = 20
high_node = 80
profile = profile[(profile.nodeID >= low_node) & (profile.nodeID < high_node)]
print(len(profile)//60)
pheno = pheno[
    (pheno["6148-2.0"] == -7)
    | (pheno["6148-3.0"] == -7)]
profile = profile[profile.subjectID.isin(pheno.eid.unique())]
print(len(profile)//60)
pheno = pheno[(
    ((pheno["5208-0.0"] <= 0.3) & (pheno["5201-0.0"] <= 0.3)) |
    ((pheno["5208-1.0"] <= 0.3) & (pheno["5201-1.0"] <= 0.3)))]
profile = profile[profile.subjectID.isin(pheno.eid.unique())]
print(len(profile)//60)
profile.to_csv("output/tract_profiles_filt.csv")

spec_pheno = pd.DataFrame()

ethnic_map = {
    1: "White",
    1001: "British",
    2001: "White & Black Caribbean",
    3001: "Indian",
    4001: "Caribbean",
    2: "Mixed",
    1002: "Irish",
    2002: "White & Black African",
    3002: "Pakistani",
    4002: "African",
    3: "Asian or Asian British",
    1003: "Other white",
    2003: "White and Asian",
    3003: "Bangladeshi",
    4003: "Other Black",
    4: "Black or Black British",
    2004: "Other mixed",
    3004: "Other Asian",
    5: "Chinese",
    6: "Other ethnic group",
    -1: "Do not know",
    -3: "Prefer not to answer"}
sex_map = {
    0: "Female",
    1: "Male"}

pheno["21000-0.0"] = pheno["21000-0.0"].replace(np.nan, -1)
spec_pheno["Ethnicity"] = pheno["21000-0.0"].replace(ethnic_map)
spec_pheno["Age"] = pheno["21003-2.0"].astype(int)
spec_pheno["Sex"] = pheno["31-0.0"].replace(sex_map)
spec_pheno["subjectID"] = pheno["eid"]
profile = profile.merge(spec_pheno, on="subjectID")

total_count = len(profile.subjectID.unique())
print(f"Total # of subjects: {total_count}")
for tract_name in ["fov_L", "fov_R", "mac_L", "mac_R", "periph_L", "periph_R"]:
    count = np.sum(~np.isnan(profile[f'dki_fa_{tract_name}'].to_numpy()))//100
    print(f"{tract_name} valid: {count} ({(1-count / total_count)*100}%)")

for_violin_spec_pheno = spec_pheno.copy()
for i in range(100):
    to_append = {
        "Age": 82,
        "Sex": "100 subjects"
    }
    if i == 50:
        to_append["texthere"] = True
    for_violin_spec_pheno = for_violin_spec_pheno.append(to_append, ignore_index=True)
for i in range(200):
    for_violin_spec_pheno = for_violin_spec_pheno.append({
        "Age": 82,
        "Sex": "White Space"
    }, ignore_index = True)
x_spec = alt.X(
    'count(Age):Q',
    stack='center',
    impute=None,
    title=None,
    axis=alt.Axis(labels=False, values=[0], grid=False, ticks=True)
)
y_spec = alt.Y(
    'Age:Q',
    scale=alt.Scale(domain=[45, 81]))
color_spec = alt.Color(
    'Sex:N',
    scale=alt.Scale(
        domain=['Female', 'Male', "100 subjects", "White Space"],
        range=['green', 'red', "black", "white"]),
    legend=alt.Legend(values=["Female", "Male"]))
chart = alt.Chart(for_violin_spec_pheno).mark_bar(orient='horizontal').encode(
    y=y_spec,
    color=color_spec,
    x=x_spec
)

chart_text = alt.Chart(for_violin_spec_pheno).mark_text(
    align='left',
    baseline='top',
    fontSize = 20,
    dx = 18,
    dy = 5
).encode(
    x=x_spec,
    y=y_spec,
    text='Sex',
    color=color_spec
).transform_filter(datum.texthere)

chart = chart + chart_text

ethnicity_pie = alt.Chart(spec_pheno).mark_bar().encode(
    x=alt.X(
        'Ethnicity:N'),
    color='Sex:N',
    y=alt.Y(
        'count(Ethnicity):Q',
        title="Count of subjects per bin"
        #scale=alt.Scale(type='symlog')
    ),
)


age_bin_df = {"age_bin": [], "Count of subjects per bin": [], "Sex": []}
for age_bin in profile.age_bin.unique():
    for sex in profile["Sex"].unique():
        this_prof = profile[profile.age_bin == age_bin]
        this_prof = this_prof[this_prof["Sex"] == sex]
        age_bin_df["age_bin"].append(age_bin)
        age_bin_df["Count of subjects per bin"].append(len(this_prof)/100)
        age_bin_df["Sex"].append(sex)
age_bin_df = pd.DataFrame(age_bin_df)
forced_age_bins = alt.Chart(age_bin_df).mark_bar().encode(
    x=alt.X(
        'age_bin:N', title="Selected age bins"),
    color='Sex:N',
    y=alt.Y('Count of subjects per bin:Q'),
)

#   transform_chart(ethnicity_pie) |\
chart = chart | forced_age_bins

# chart = chart.configure_view(
#     stroke=None
# )

chart.configure_axis(
    labelFontSize=20,
    titleFontSize=20,
    labelLimit=0).configure_legend(
        labelFontSize=20,
        titleFontSize=20,
        columns=2,
        orient='bottom',
        titleLimit=0,
        labelLimit=0
    ).save('output/first_paper_plots/pheno_hist.html')
