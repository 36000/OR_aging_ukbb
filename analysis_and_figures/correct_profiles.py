import pandas as pd
from tqdm import tqdm
profiles = pd.read_csv("output/tract_profiles.csv")

# correct for lack of unnamed column in newer profiles
slicer = (profiles["subjectID"] == "unknown")
profiles.loc[slicer,"sessionID"] = profiles[slicer]["subjectID"]
profiles.loc[slicer,"subjectID"] = profiles[slicer]["dti_md"]
profiles.loc[slicer,"dti_md"] = profiles[slicer]["dti_fa"]
profiles.loc[slicer,"dti_fa"] = profiles[slicer]["dki_mk"]
profiles.loc[slicer,"dki_mk"] = profiles[slicer]["dki_md"]
profiles.loc[slicer,"dki_md"] = profiles[slicer]["dki_fa"]
profiles.loc[slicer,"dki_fa"] = profiles[slicer]["nodeID"]
profiles.loc[slicer,"nodeID"] = profiles[slicer]["tractID"]
profiles.loc[slicer,"tractID"] = profiles[slicer]["Unnamed: 0"]

profiles["subjectID"] = profiles["subjectID"].astype(int)
profiles.to_csv("output/tract_profiles.csv")

