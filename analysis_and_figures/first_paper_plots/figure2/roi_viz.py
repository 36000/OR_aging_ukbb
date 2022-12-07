from AFQ.viz.fury_backend import visualize_volume, visualize_roi
from AFQ.data.fetch import read_mni_template
from dipy.align import resample
import nibabel as nib
import numpy as np
from fury.window import snapshot
from comb import trim

mni = read_mni_template()
roi_dict = {
    "OR_L_1": "/Users/john/AFQ_data/or_templates/left_OR_1.nii.gz",
    "OR_R_1": "/Users/john/AFQ_data/or_templates/right_OR_1.nii.gz",
    "OR_L_2": "/Users/john/AFQ_data/or_templates/left_OR_2.nii.gz",
    "OR_R_2": "/Users/john/AFQ_data/or_templates/right_OR_2.nii.gz",
    "OR_ex_L": "/Users/john/AFQ_data/or_templates/left_OP_MNI.nii.gz",
    "OR_ex_R": "/Users/john/AFQ_data/or_templates/right_OP_MNI.nii.gz",
    "OR_st_L": "/Users/john/AFQ_data/or_templates/left_thal_MNI.nii.gz",
    "OR_st_R": "/Users/john/AFQ_data/or_templates/right_thal_MNI.nii.gz",
    "OR_en_L": "/Users/john/AFQ_data/or_templates/left_V1_MNI.nii.gz",
    "OR_en_R": "/Users/john/AFQ_data/or_templates/right_V1_MNI.nii.gz"
}
for roi_name in ["fov", "mac", "perip"]:
    for side in ["L", "R"]:
        roi_dict[f"{roi_name}_{side}"] = f"/Users/john/AFQ_data/subroi/eccen_roi/3/{roi_name}_{side}.nii.gz"

for roi_name, roi_path in roi_dict.items():
    roi_dict[roi_name] = resample(nib.load(roi_path), mni).get_fdata()
roi_dict["OR_enb_L"] = np.logical_or(roi_dict["OR_st_L"], roi_dict["OR_en_L"])
roi_dict["OR_in_L"] = np.logical_or(roi_dict["OR_L_1"], roi_dict["OR_L_2"])
roi_dict["OR_enb_R"] = np.logical_or(roi_dict["OR_st_R"], roi_dict["OR_en_R"])
roi_dict["OR_in_R"] = np.logical_or(roi_dict["OR_R_1"], roi_dict["OR_R_2"])

viz_kwargs = {"inline": False, "flip_axes": [False, False, False]}

figure = visualize_volume(
    mni.get_fdata(), opacity=0.5, **viz_kwargs)
figure = visualize_roi(
    roi_dict["OR_in_R"],
    color=[0, 1, 1],
    name="Right OR Inclusives",
    figure=figure, **viz_kwargs)
figure = visualize_roi(
    roi_dict["OR_enb_R"],
    color=[1, 1, 0],
    name="Right OR Endpoints",
    figure=figure, **viz_kwargs)
figure = visualize_roi(
    roi_dict["OR_ex_R"],
    color=[1, 0, 1],
    name="Right OR Exclusive",
    figure=figure, **viz_kwargs)
# figure = visualize_roi(
#     roi_dict["fov_R"],
#     color=[0, 1, 1],
#     name="Right Fovea",
#     figure=figure)
# figure = visualize_roi(
#     roi_dict["mac_R"],
#     color=[1, 1, 0],
#     name="Right Macula",
#     figure=figure)
# figure = visualize_roi(
#     roi_dict["perip_R"],
#     color=[1, 0, 1],
#     name="Right Periphery",
#     figure=figure)

# fixed_camera_for_2d = dict(
#     up=dict(x=0, y=1, z=0),
#     eye=dict(x=0, y=0, z=2),
#     center=dict(x=0, y=0, z=0))
# figure.update_layout(
#     scene=dict(
#         camera=fixed_camera_for_2d,
#         dragmode=False),
#     showlegend=False)
# figure.write_image("a_temp.png")
snapshot(figure, "a_temp.png", size=(1200, 1200))

figure = visualize_volume(
    mni.get_fdata(), opacity=0.5, **viz_kwargs)
figure = visualize_roi(
    roi_dict["OR_in_R"],
    color=[0, 1, 1],
    name="Right OR Inclusives",
    figure=figure, **viz_kwargs)
figure = visualize_roi(
    roi_dict["OR_enb_R"],
    color=[1, 1, 0],
    name="Right OR Endpoints",
    figure=figure, **viz_kwargs)
figure = visualize_roi(
    roi_dict["OR_ex_R"],
    color=[1, 0, 1],
    name="Right OR Exclusive",
    figure=figure, **viz_kwargs)
# figure = visualize_roi(
#     roi_dict["fov_L"],
#     color=[0, 1, 1],
#     name="Left Fovea",
#     figure=figure)
# figure = visualize_roi(
#     roi_dict["mac_L"],
#     color=[1, 1, 0],
#     name="Left Macula",
#     figure=figure)
# figure = visualize_roi(
#     roi_dict["perip_L"],
#     color=[1, 0, 1],
#     name="Left Periphery",
#     figure=figure)

# fixed_camera_for_2d = dict(
#     up=dict(x=0, y=0, z=1),
#     eye=dict(x=1, y=0, z=0),
#     center=dict(x=0, y=0, z=0))
# figure.update_layout(
#     scene=dict(
#         camera=fixed_camera_for_2d,
#         dragmode=False),
#     showlegend=False)
    # legend=dict(
    #     yanchor="bottom",
    #     y=0,
    #     xanchor="right",
    #     x=0,
    #     bgcolor='rgba(0.99,0.99,0.99,0.8)',
    #     bordercolor='rgba(0.4,0.4,0.4,0.99)',
    #     borderwidth=2,
    # ))
# figure.write_image("a_temp2.png")
figure.set_camera(
    position=(780.9551599346477, 114.0, 96.0),
    focal_point=(96.0, 114.0, 96.0),
    view_up=(0.0, 0.0, 1.0))

snapshot(figure, "a_temp2.png", size=(1200, 1200))

from PIL import Image
im1 = trim(trim(Image.open('a_temp.png')))
im2 = trim(trim(Image.open('a_temp2.png')))
comb = Image.new('RGB', (im1.width + im2.width, im1.height))
comb.paste(im1, (0, 0))
comb.paste(im2, (im1.width, 0))
comb.save('a_add.png')
