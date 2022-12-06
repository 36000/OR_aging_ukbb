from dipy.io.streamline import load_tractogram
from dipy.io.stateful_tractogram import StatefulTractogram, Space
from dipy.stats.analysis import afq_profile
import numpy as np
import nibabel as nib
import sys
import pandas as pd
import os.path as op
from tqdm import tqdm
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

data_dir = "data/jk232/"

screen = sys.argv[1]
batch = sys.argv[2]
subjects = sys.argv[3:]

df = pd.DataFrame(columns = ['tractID', 'nodeID', 'dki_fa', 'dki_md', 'dki_mk', 'dti_fa', 'dti_md', 'subjectID', 'sessionID'])

for SUB in tqdm(subjects):
    afq_path = f"{data_dir}optic_bids_{screen}_{batch}/derivatives/afq/sub-{SUB}/"
    subbundle_path = f"{data_dir}optic_bids_{screen}_{batch}/derivatives/subbundle/sub-{SUB}/"
    if not op.exists(f"{afq_path}sub-{SUB}_dwi_model-DKI_MD.nii.gz"):
        continue
    fa = nib.load(f"{afq_path}sub-{SUB}_dwi_model-DKI_FA.nii.gz")
    md = nib.load(f"{afq_path}sub-{SUB}_dwi_model-DKI_MD.nii.gz")
    mk = nib.load(f"{afq_path}sub-{SUB}_dwi_model-DKI_MK.nii.gz")
    dtifa = nib.load(f"{afq_path}sub-{SUB}_dwi_model-DTI_FA.nii.gz")
    dtimd = nib.load(f"{afq_path}sub-{SUB}_dwi_model-DTI_MD.nii.gz")

    name_dict = {"0": "peripheral", "1": "foveal"}

    bundle_dict = {}
    sls_dict = {}
    for side in ["R", "L"]:
        for roi_name in ["fov_3", "mac_3", "perip_3"]:
            sls_fname = f"{subbundle_path}sls/{roi_name}_{side}.trk"
            if not op.exists(sls_fname):
                continue
            sls = load_tractogram(sls_fname, "same", Space.VOX, bbox_valid_check=False)
            if len(sls.streamlines) > 0:
                scalar_dict = {}
                for scalar_name, scalar in {"dki_fa": fa, "dki_md": md, "dki_mk": mk, "dti_fa": dtifa, "dti_md": dtimd}.items():
                    scalar_dict[scalar_name] = afq_profile(scalar.get_fdata(), sls.streamlines, np.eye(4))
                for idx in range(100):
                    df = df.append({
                        "nodeID": idx, "subjectID": SUB, "tractID": f"{roi_name[:-2]}_{side}", "sessionID": "unknown",
                        "dki_fa": scalar_dict["dki_fa"][idx],
                        "dki_md": scalar_dict["dki_md"][idx], "dki_mk": scalar_dict["dki_mk"][idx],
                        "dti_fa": scalar_dict["dti_fa"][idx], "dti_md": scalar_dict["dti_md"][idx]}, ignore_index=True)
                if "fov" in roi_name:
                    i = 0
                elif "mac" in roi_name:
                    i = 1
                elif "perip" in roi_name:
                    i = 2
                bundle_dict[f"{roi_name}_{side}"] = {"uid": i}
                sls_dict[f"{roi_name}_{side}"] = sls
df.to_csv(f"{data_dir}optic_bids_{screen}_{batch}/derivatives/subbundle/profiles.csv")
