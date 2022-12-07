from dipy.io.streamline import load_tractogram
from dipy.io.stateful_tractogram import StatefulTractogram, Space
from dipy.io.stateful_tractogram import apply_affine
import numpy as np
import altair as alt
from altair_saver import save
import nibabel as nib
from PIL import Image
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd

t1 = nib.load("ex_sub/T1.nii.gz")
proc_t1_data = t1.get_fdata()

# This helps t1 processing
low_b = np.quantile(proc_t1_data, 0.01)
high_b = np.quantile(proc_t1_data, 0.99)
proc_t1_data[proc_t1_data < low_b] = low_b
proc_t1_data[proc_t1_data > high_b] = high_b
proc_t1_data = proc_t1_data - low_b
proc_t1_data = proc_t1_data / (high_b - low_b)


proc_t1_data = proc_t1_data*255.

df = pd.DataFrame()
side_dict = {"L": "L,", "R": "R,"}
for side in ["L", "R"]:
    for roi_name in ["fov_3", "mac_3", "perip_3"]:
        sls_fname = f"ex_sub/{roi_name}_{side}.trk"
        try:
            sft = load_tractogram(sls_fname, "same", Space.RASMM, bbox_valid_check=False)
        except:
            continue
        min_coord = 100
        for sl in sft.streamlines:
            this_min = np.min(sl[:, 1])
            if this_min < min_coord:
                min_coord = this_min
        for slice in [10, 30]:
            # print(slice)
            if slice == 10 and "perip" in roi_name:
                continue
            axial_coords = []
            coronal_coords = []
            sag_coords = []
            for jj, sl in enumerate(sft.streamlines):
                sl = np.asarray(sl)
                idx = (np.abs(sl[:, 1] - slice - min_coord)).argmin()

                # sft2 = load_tractogram(sls_fname, "same", Space.VOX, bbox_valid_check=False)
                # print(sft2.streamlines[jj][idx, 1])

                df = df.append({
                    "side": side,
                    "bundle": roi_name,
                    "slice": f"{side_dict[side]} {slice}mm ant. of VC",
                    "Axial": sl[idx, 0],
                    "Sag": sl[idx, 1],
                    "Coronal": sl[idx, 2],
                    "median": 1,
                }, ignore_index=True)
                axial_coords.append(sl[idx, 0])
                coronal_coords.append(sl[idx, 2])
                sag_coords.append(sl[idx, 1])
            if len(axial_coords) > 1:
                df = df.append({
                    "side": side,
                    "bundle": roi_name,
                    "slice": f"{side_dict[side]} {slice}mm ant. of VC",
                    "Axial": np.median(axial_coords),
                    "Sag": np.median(sag_coords),
                    "Coronal": np.median(coronal_coords),
                    "median": 10,
                }, ignore_index=True)

fontsize=25
for ii, column_name in enumerate(df.slice.unique()):
    this_df = df[df.slice == column_name]
    domain = [-35, 35]
    z_domain = [-35, 35]
    x_kwargs = dict(title="<-Left ... Right->", scale=alt.Scale(zero=False, domain=domain), axis=alt.Axis(tickCount=2))
    y_kwargs = dict(title="<-Inferior ... Superior->", scale=alt.Scale(zero=False, domain=z_domain), axis=alt.Axis(tickCount=2))

    sag_mm = np.median(this_df["Sag"])

    rasmm_points = []
    for xx in range(domain[0], domain[1], 1):
        for zz in range(z_domain[0], z_domain[1], 1):
            rasmm_points.append((xx, sag_mm, zz))

    vox_points = apply_affine(
        np.linalg.inv(t1.affine), rasmm_points).astype(int)

    z_range = z_domain[1]-z_domain[0]
    x_range = domain[1]-domain[0]
    this_t1_data = np.zeros((z_range, x_range))
    for xx in range(x_range):
        for zz in range(z_range):
            vox_xx, vox_yy, vox_zz = vox_points[xx*z_range+zz]
            this_t1_data[z_range-zz-1, xx] = proc_t1_data[vox_xx, vox_yy, vox_zz]

    im = Image.fromarray(this_t1_data).convert('RGB')
    im.save("temp_t1.png")

    img_source = pd.DataFrame.from_records([
      {"x": (domain[0]+domain[1])/2, "y": (z_domain[1]+z_domain[0])/2, "img": "temp_t1.png"},
    ])

    scatters = alt.Chart(this_df, title=column_name).mark_point().encode(
        x=alt.X("Axial", **x_kwargs),
        y=alt.Y("Coronal", **y_kwargs),
        color=alt.Color(
            'bundle',
            legend=None,
            scale=alt.Scale(
                domain=['fov_3', 'mac_3', 'perip_3'],
                range=["red", "limegreen", "blue"])),
        opacity=alt.Opacity("median", scale=alt.Scale(domain=[1, 10], range=[0.3, 1]), legend=None),
        strokeWidth=alt.StrokeWidth("median", scale=alt.Scale(domain=[1, 10], range=[5, 10]), legend=None),
        size=alt.Size("median", scale=alt.Scale(domain=[1, 10], range=[300, 600]), legend=None)
    ).properties(
        width=400,
        height=400
    )

    image_chart = alt.Chart(img_source).mark_image(
        width=400,
        height=400,
        opacity=0.75
    ).encode(
        x=alt.X('x', **x_kwargs),
        y=alt.Y('y', **y_kwargs),
        url='img'
    )
    
    save((image_chart + scatters).configure_axis(
        labelFontSize=20,
        titleFontSize=fontsize
    ).configure_title(fontSize=40), f"d{ii}.png")

    # from PIL import Image
    # im1 = Image.open(f"d{ii}.png")
    # im2 = Image.open('')
    # comb = Image.new('RGB', (im1.width + im2.width, im1.height))
    # comb.paste(im1, (0, 0))
    # comb.paste(im2, (im1.width, 0))
    # comb.save('a_add.png')

    