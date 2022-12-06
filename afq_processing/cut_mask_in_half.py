import nibabel as nib
import sys

sub = sys.argv[1]
screen = sys.argv[2]
iteration = sys.argv[3]
keep_back = ("back" in sys.argv[4])

o_folder = f"optic_bids_{screen}_{iteration}"
prefix = ""

og_brain_mask = nib.load(f"output/{o_folder}/derivatives/afq/sub-{sub}/{prefix}sub-{sub}_dwi_brain_mask.nii.gz")
data = og_brain_mask.get_fdata()
half_length = int(data.shape[1]//2)
if keep_back:
    data[:, half_length:, :] = 0
else:
    data[:, :half_length, :] = 0
nib.save(nib.Nifti1Image(data, og_brain_mask.affine), f"output/{o_folder}/derivatives/afq/sub-{sub}/{prefix}sub-{sub}_dwi_brain_mask_halved.nii.gz")

