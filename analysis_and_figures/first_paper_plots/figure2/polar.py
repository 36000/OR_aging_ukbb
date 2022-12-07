from math import pi
import matplotlib.pyplot as plt
import matplotlib.patches as ptc

rmax = 30
fontsize = 24
rticks = list(range(0, rmax, 5))
rtick_labels = [""]*len(rticks)

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})


ax.add_artist(ptc.Circle((0, 0), rmax, transform=ax.transData._b, color=[0, 0, 1], alpha=0.9))
ax.add_artist(ptc.Circle((0, 0), 7, transform=ax.transData._b, color=[0, 1, 0], alpha=0.9))
ax.add_artist(ptc.Circle((0, 0), 3, transform=ax.transData._b, color=[1, 0, 0], alpha=0.9))
ax.annotate("7", xy=(pi/8, 8), fontsize=fontsize, ha="center", color="white")
ax.annotate("3", xy=(pi/8, 4), fontsize=fontsize, ha="center", color="black")

ax.set_rmax(rmax)
ax.set_rticks(rticks)
ax.set_yticklabels(rtick_labels)
ax.set_xticklabels([])
ax.grid(True)

#ax.set_title("Degrees Eccentricity", va='bottom')
plt.savefig("b.png")