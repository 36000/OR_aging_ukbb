import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms
from PIL import Image, ImageChops
import numpy as np

def bbox(img):
    img = np.sum(img, axis=-1)
    rows = np.any(img, axis=1)
    cols = np.any(img, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]

    return cmin, rmin, cmax, rmax

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    this_bbox = bbox(diff)
    if this_bbox:
        return im.crop(this_bbox)

def trim_manual(im):
    cmin, rmin, cmax, rmax = bbox(im)
    c_range = cmax - cmin
    cmin = c_range//10
    cmax = (c_range*9)//10
    return im.crop((cmin, rmin, cmax, rmax))

fig = plt.figure(figsize=(8, 6))
grid = plt.GridSpec(3, 4, hspace=0, wspace=0)
subplot_count = 0

def add_img(x_coord, y_coord, fname, reduct_count=2, man_count=0, legend=None, legend_kwargs={},):
    global subplot_count
    subplot_label_ypos=1.0
    ax = fig.add_subplot(grid[y_coord, x_coord])
    im1 = Image.open(fname)
    for _ in range(reduct_count):
        im1 = trim(im1)
    for _ in range(man_count):
        im1 = trim_manual(im1)
    if legend is not None:
        subplot_label_ypos=0.7
        patches = []
        for value, color in legend.items():
            patches.append(mpatches.Patch(
                color=color,
                label=value))
        ax.legend(handles=patches, borderaxespad=0., **legend_kwargs)
    trans = mtransforms.ScaledTranslation(10/72, -5/72, fig.dpi_scale_trans)
    ax.text(0.0, subplot_label_ypos, f"{chr(65+subplot_count)})", transform=ax.transAxes + trans,
            fontsize='medium', verticalalignment="top", fontfamily='serif',
            bbox=dict(facecolor='0.7', edgecolor='none', pad=3.0))
    ax.imshow(np.asarray(im1), aspect=1)
    ax.axis('off')
    subplot_count = subplot_count + 1

add_img(1, 0, 'a_temp.png', legend={
    "Right OR Inclusives": [0, 1, 1],
    "Right OR Endpoints": [1, 1, 0],
    "Right OR Exclusive": [1, 0, 1]},
    legend_kwargs=dict(bbox_to_anchor=(1.1, 0.75), loc=2))
add_img(3, 0, 'a_temp2.png')
add_img(0, 1, 'b.png', legend={
    "Fovea (<=3°)": [1, 0, 0],
    "Macula (>3°, <=7°)": [0, 1, 0],
    "Periphery (>7°)": [0, 0, 1]},
    legend_kwargs=dict(bbox_to_anchor=(0.05, 1.1), loc=2))


add_img(1, 1, 'a.png')

# add_img(0, 1, 'c4.png')
# add_img(1, 1, 'c2.png')
add_img(2, 1, 'c3.png', man_count=3)
add_img(3, 1, 'c1.png', reduct_count=1, man_count=1)

reduce_count_d = 0
add_img(0, 2, 'd0.png', reduct_count=reduce_count_d)
add_img(1, 2, 'd1.png', reduct_count=reduce_count_d)
add_img(2, 2, 'd2.png', reduct_count=reduce_count_d)
add_img(3, 2, 'd3.png', reduct_count=reduce_count_d)

fname = "fig1.png"
fig.tight_layout()
fig.savefig(fname)
im1 = Image.open(fname)
im1 = trim(im1)
im1.save(fname)
