from dipy.io.streamline import save_tractogram, load_tractogram
from AFQ.segmentation import Segmentation
from AFQ.definitions.mapping import ConformedFnirtMapping
from AFQ.registration import read_mapping
from dipy.io.stateful_tractogram import StatefulTractogram, Space

import nibabel as nib
import numpy as np
import sys

from fsl.data.image import Image
from fsl.transform.fnirt import readFnirt
from fsl.utils.path import PathError

screen = sys.argv[1]
batch = sys.argv[2]
SUB = sys.argv[3]

data_dir = "data/jk232/"

fa_path = f"{data_dir}optic_bids_{screen}_{batch}/derivatives/afq/sub-{SUB}/sub-{SUB}_dwi_model-DKI_FA.nii.gz"
fa_img = nib.load(fa_path)
reg_template = nib.load(f"{data_dir}AFQ_data/subroi/eccen_roi/3/fov_R.nii.gz")
try:
    nearest_warp = f"{data_dir}optic_bids_{screen}_{batch}/derivatives/TBSS/sub-{SUB}/sub-{SUB}_dwi_MNI_to_dti_FA_warp.nii.gz"
    nearest_space = f"{data_dir}optic_bids_{screen}_{batch}/derivatives/TBSS/sub-{SUB}/sub-{SUB}_dwi_dti_FA_to_MNI.nii.gz"
    subj = Image(fa_path)
    their_templ = Image(nearest_space)
    warp = readFnirt(nearest_warp, their_templ, subj)
    mapping = ConformedFnirtMapping(warp, reg_template.affine)
except PathError:
    reg_prealign = np.load(
        f"{data_dir}optic_bids_{screen}_{batch}/derivatives/afq/sub-{SUB}/sub-{SUB}_dwi_prealign_from-DWI_to-MNI_xfm.npy")
    reg_prealign_inv = np.linalg.inv(reg_prealign)
    mapping = read_mapping(
        f"{data_dir}optic_bids_{screen}_{batch}/derivatives/afq/sub-{SUB}/sub-{SUB}_dwi_mapping_from-DWI_to_MNI_xfm.nii.gz",
        fa_path,
        reg_template,
        prealign=reg_prealign_inv)

for side in ["R", "L"]:
    bundle_dict = {}
    for roi_name in ["fov", "mac", "perip"]:
        bundle_dict[f"{roi_name}_3_{side}"] = {
            "end": nib.load(f"{data_dir}AFQ_data/subroi/eccen_roi/3/{roi_name}_{side}.nii.gz")}
    
    sft = load_tractogram(
        f"{data_dir}optic_bids_{screen}_{batch}/derivatives/afq/sub-{SUB}/clean_bundles/sub-{SUB}_dwi_space-RASMM_model-DTI_desc-det-AFQ-{side}_OR_tractography.trk",
        fa_img)
    if len(sft.streamlines) == 0:
        for key in bundle_dict.keys():
           save_tractogram(sft, f"{data_dir}optic_bids_{screen}_{batch}/derivatives/subbundle/sub-{SUB}/sls/{key}.trk", bbox_valid_check=False)
        continue
    seg = Segmentation(
        save_intermediates=f"{data_dir}optic_bids_{screen}_{batch}/derivatives/subbundle/sub-{SUB}/subbundle_inters",
        roi_dist_tie_break=True)
    seg.img = fa_img
    fg = seg.segment(bundle_dict, sft, mapping=mapping, img_affine=fa_img.affine, reg_template=reg_template)
    for key, val in fg.items():
        print(len(fg[key]))
        save_tractogram(
            fg[key],
            f"{data_dir}optic_bids_{screen}_{batch}/derivatives/subbundle/sub-{SUB}/sls/{key}.trk",
            bbox_valid_check=False)
