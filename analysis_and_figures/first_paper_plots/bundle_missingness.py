import pandas as pd
import altair as alt
import numpy as np

font_size = 20

dataframe = pd.read_csv("output/tract_profiles_filt.csv")
bundles = ["UNC_L", "UNC_R", "CST_L", "CST_R", "fov_L", "fov_R",  "mac_L", "mac_R", "periph_L", "periph_R"]

age_bins = list(dataframe["age_bin"].unique())

b_order = ["Fov. OR", "Mac. OR", "Per. OR", "CST", "UNC"]

bundle_names_formal = {
    "fov_L": "Fov. OR",
    "fov_R": "Fov. OR",
    "mac_L": "Mac. OR",
    "mac_R": "Mac. OR",
    "periph_L": "Per. OR",
    "periph_R": "Per. OR",
    "CST_L": "CST",
    "CST_R": "CST",
    "UNC_L": "UNC",
    "UNC_R": "UNC"
}

hemi_names_formal = {
    "fov_L": "Left",
    "fov_R": "Right",
    "mac_L": "Left",
    "mac_R": "Right",
    "periph_L": "Left",
    "periph_R": "Right",
    "CST_L": "Left",
    "CST_R": "Right",
    "UNC_L": "Left",
    "UNC_R": "Right"
}

dataframe = dataframe[dataframe["nodeID"] == 49]

bundle_counts_df = pd.DataFrame()
for age_bin in age_bins:
    this_df = dataframe[dataframe["age_bin"] == age_bin]
    number_of_subjects = len(this_df["subjectID"])
    for bundle in bundles:
        these_counts = pd.DataFrame({
            "Hemisphere": number_of_subjects*[hemi_names_formal[bundle]],
            "Bundle Name": number_of_subjects*[bundle_names_formal[bundle]],
            "Age Bin": number_of_subjects*[age_bin],
            "Percent Found": ~this_df[f'dki_fa_{bundle}'].isna()})
        bundle_counts_df = pd.concat([bundle_counts_df, these_counts], ignore_index=True)

chart = alt.Chart().mark_bar().encode(
    x=alt.X("Age Bin"),
    color=alt.Color("Age Bin", scale=alt.Scale(scheme="plasma")),
    y=alt.Y("mean(Percent Found):Q"))

error_bars = alt.Chart().mark_errorbar(extent='ci').encode(
    x=alt.X("Age Bin"),
    y='Percent Found:Q',
)

alt.LayerChart(
    layer=[chart, error_bars], data=bundle_counts_df).facet(
        column=alt.Column(
            "Bundle Name",
            sort=b_order,
            header=alt.Header(
                titleOrient='bottom',
                labelOrient='bottom',
                labelPadding=0,
                labelAngle=45,
                labelFontSize=font_size,
                titleFontSize=font_size
            )),
        row=alt.Row("Hemisphere", header=alt.Header(
                labelFontSize=font_size,
                titleFontSize=font_size))).configure_axis(
            labelFontSize=font_size,
            titleFontSize=font_size,
            labelLimit=0).configure_legend(
                labelFontSize=font_size,
                titleFontSize=font_size,
                titleLimit=0,
                labelLimit=0,
                columns=7,
                orient='bottom'
            ).configure_title(
                fontSize=font_size
                ).save('output/first_paper_plots/bundle_missingness.html')
