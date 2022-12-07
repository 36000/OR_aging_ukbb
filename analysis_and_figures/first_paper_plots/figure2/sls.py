from AFQ.viz.fury_backend import visualize_bundles, visualize_roi, single_bundle_viz, visualize_volume
from AFQ.utils.streamlines import SegmentedSFT
from dipy.io.streamline import load_tractogram
from dipy.io.stateful_tractogram import Space
from dipy.tracking.streamline import set_number_of_points
import pandas as pd
import numpy as np
from fury.window import snapshot
from fury.actor import text_3d, line
import nibabel as nib
from dipy.align import resample

color_dict = {
    "fov_3_L": [1, 0, 0],
    "mac_3_L": [0, 1, 0],
    "perip_3_L": [0, 0, 1],
    "fov_3_R": [1, 0, 0],
    "mac_3_R": [0, 1, 0],
    "perip_3_R": [0, 0, 1],
}

name_dict = {
    "fov_3_L": "fov_L",
    "mac_3_L": "mac_L",
    "perip_3_L": "perip_L",
    "fov_3_R": "fov_R",
    "mac_3_R": "mac_R",
    "perip_3_R": "perip_R",
}

profiles = pd.read_csv("ex_sub/profiles.csv")
profiles = profiles[profiles.subjectID == 1001789]

b0 = nib.load("ex_sub/b0.nii.gz")
t1 = nib.load("ex_sub/T1.nii.gz")
t1_data = resample(t1, b0).get_fdata()
t1_data = t1_data[:, :t1_data.shape[1]//2, :]


figure = None
figure2 = None
for bundle_name, color in color_dict.items():
    this_profile = profiles[profiles.tractID == name_dict[bundle_name]]
    if len(this_profile) < 1:
        continue
    seg_sft = SegmentedSFT(
        {bundle_name: load_tractogram(f"ex_sub/{bundle_name}.trk", "same")},
        Space.RASMM)
    figure = single_bundle_viz(
        this_profile.dki_fa.to_numpy(), seg_sft,
        bundle_name, "dki_fa",
        figure=figure,
        flip_axes=[True, False, False],
        labelled_nodes=[],
        include_profile=False)
    figure2 = visualize_bundles(
        seg_sft,
        bundle_dict={bundle_name: None},
        bundle=bundle_name,
        colors=[color],
        flip_axes=[True, False, False],
        figure=figure2)
    figure = visualize_roi(
        f"ex_sub/{bundle_name}/as_used.nii.gz",
        flip_axes=[True, False, False],
        color=color, figure=figure)

    if "fov_3_L" == bundle_name:
        seg_sft.sft.to_vox()
        fgarray = np.asarray(set_number_of_points(seg_sft.sft.streamlines, 100))
        fgarray = np.median(fgarray, axis=0)
        max_x = np.max(fgarray[:, 0])
    if "fov_3_R" == bundle_name: 
        seg_sft.sft.to_vox()
        fgarray = np.asarray(set_number_of_points(seg_sft.sft.streamlines, 100))
        fgarray = np.median(fgarray, axis=0)
        min_coord = np.min(fgarray[:, 1])
        for slice in [0, 10, 20, 30]:
            idx = (np.abs(fgarray[:, 1] - slice - min_coord)).argmin()
            line_pts = np.zeros((2, 3))
            this_spot = fgarray[idx]
            this_spot[0] = max_x
            line_pts[0] = this_spot.copy()
            this_spot[0] = max_x + 5
            line_pts[1] = this_spot.copy()
            this_spot[0] = max_x + 10
            text_part = text_3d(
                f"{slice}mm",
                position=this_spot, color=(0, 0, 0),
                font_size=3, justification="center",
                vertical_justification="middle", font_family='Arial')
            figure.add(text_part)
            figure.add(line([line_pts], colors=(0, 0, 0), linewidth=5))
            if slice == 0:
                min_y = this_spot[1] - 0.5
            if slice == 30:
                max_y = this_spot[1]
        figure.add(line(
            [[[max_x + 2.5, min_y, this_spot[2]], [max_x + 2.5, max_y, this_spot[2]]]],
            colors=(0, 0, 0), linewidth=5))

    # figure2 = visualize_roi(
    #     f"ex_sub/{bundle_name}/as_used.nii.gz",
    #     flip_axes=[True, False, False],
    #     color=color, figure=figure2)


figure = visualize_volume(
    t1_data,
    opacity=0.5,
    figure=figure,
    flip_axes=[True, False, False],
    inline=False)
figure2 = visualize_volume(
    t1_data,
    opacity=0.5,
    figure=figure2,
    flip_axes=[True, False, False],
    inline=False)

snapshot(figure, "c1.png", size=(1200, 1200))
snapshot(figure2, "c3.png", size=(1200, 1200))

# fixed_camera_for_2d = dict(
#     up=dict(x=0, y=0, z=1),
#     eye=dict(x=2, y=0, z=0),
#     center=dict(x=0, y=0, z=0))
# figure.update_layout(
#     scene=dict(
#         camera=fixed_camera_for_2d,
#         dragmode=False),
#     showlegend=False)
# figure2.update_layout(
#     scene=dict(
#         camera=fixed_camera_for_2d,
#         dragmode=False),
#     showlegend=False)
# figure.write_image("c1.png")
# figure2.write_image("c3.png")
# fixed_camera_for_2d = dict(
#     up=dict(x=0, y=1, z=0),
#     eye=dict(x=0, y=0, z=2),
#     center=dict(x=0, y=0, z=0))
# figure.update_layout(
#     scene=dict(camera=fixed_camera_for_2d))
# figure2.update_layout(
#     scene=dict(camera=fixed_camera_for_2d))
# figure.write_image("c2.png")
# figure2.write_image("c4.png")

# def convert_png_transparent(src_file, dst_file, bg_color=(255,255,255)):
#     image = Image.open(src_file).convert("RGBA")
#     array = np.array(image, dtype=np.ubyte)
#     mask = (array[:,:,:3] == bg_color).all(axis=2)
#     alpha = np.where(mask, 0, 255)
#     array[:,:,-1] = alpha
#     Image.fromarray(np.ubyte(array)).save(dst_file, "PNG")

# convert_png_transparent("c2.png", "for_pres.png")

# figure_for_pres = single_bundle_viz(
#     this_profile.dki_fa.to_numpy(), seg_sft,
#     bundle_name, "dki_fa",
#     flip_axes=[True, False, False],
#     labelled_nodes=[],
#     include_profile=True)
# figure_for_pres.update_layout(
#     scene=dict(
#         camera=fixed_camera_for_2d,
#         dragmode=False),
#     showlegend=False)
# figure_for_pres.write_image("prof_for_pres.png")