import seaborn as sns
import pandas
import matplotlib.pyplot as plt

sns.set(font_scale=2)
sns.set_style("ticks")
# sns.set_theme(style="whitegrid")

data = pandas.read_csv("e2e.csv")
print(data.head())
# print(data["app"][0])
palette = sns.color_palette("pastel")

color1 = palette[0]
color2 = palette[1]
color3 = palette[2]

hatch1 = ""
hatch2 = "\\"
hatch3 = "*"


hatch_list = [hatch1, hatch2, hatch3]

palette_console = [color2, color1, color3]
# palette_console = [color2, color1, color3, palette[3], palette[4], palette[5], palette[6]]

g = sns.catplot(
    data=data, kind="bar",
    x="app", y="throughput", hue="platform",
    errorbar="sd", palette=palette_console, alpha=.8,
    # edgecolor='red',
    # linewidth=1,
    aspect=4, 
    # aspect=1.2, 
    width=0.5,
    # height=5,
    legend=True
)

# add pattern
for bars, hatch in zip(g.ax.containers, hatch_list):
    for bar in bars:
        bar.set_hatch(hatch)


ax = g.facet_axis(0, 0)
# ax.set_ylim(top=3)

def get_num(num):
    if num >= 10:
        return int(num)
    else:
        return "{:.2f}".format(num)

ax.legend()

# # iterate through the axes containers
# for c in ax.containers:
#     labels = [f'{get_num(v.get_height())}' for v in c]
#     # labels = [f'{int(v.get_height())}' for v in c]
#     ax.bar_label(c, labels=labels, label_type='edge')


ax.relim()
ax.autoscale_view()
ax.margins(x=0.001)
# FONT_SIZE = 14
# xytext = (80,240)
ax.annotate(
    # "Lower is better ↓",
    "Higher is better ↑",
    xycoords="axes points",
    xy=(550, 242),
    # xytext=xytext,
    #xytext=(-100, -27),
    # fontsize=FONT_SIZE,
    color="navy",
    weight="bold",
)

g.despine(right=False, top=False, offset={'top':1.5})
# g.tight_layout()
g.set_axis_labels("", "Throughput [MB/s]")
# g.legend.set_title("Platform")


def add_line(ax, xpos, ypos):
    line = plt.Line2D([xpos, xpos], [ypos+0.1, ypos], transform=ax.transAxes, color='black')
    line.set_clip_on(False)
    ax.add_line(line)

add_line(ax, 0, -.1)
add_line(ax, 0, -.2)
add_line(ax, 0, -.3)
# add_line(ax, 0, -.4)

add_line(ax, 8/16, -.1)
add_line(ax, 8/16, -.2)
add_line(ax, 8/16, -.3)
# add_line(ax, 8/16, -.4)


add_line(ax, 1, -.1)
add_line(ax, 1, -.2)
add_line(ax, 1, -.3)
# add_line(ax, 1, -.4)

ax.annotate('Memory benchmarks',
            xycoords="figure points",
            xy=(450, 18),
            # xytext=(-10, 90), 
            # textcoords='offset points',
            horizontalalignment='center', verticalalignment='bottom')
# plt.text(-0.4, -0.6, "Vitis Accel examples")

ax.annotate('RDMA benchmarks',
            xycoords="figure points",
            xy=(1200, 18),
            # xytext=(-10, 90), 
            # textcoords='offset points',
            horizontalalignment='center', verticalalignment='bottom')


# ax.legend()
g.legend.remove()
plt.legend(loc='lower left')

ax.patch.set_edgecolor('black') 
plt.tight_layout()
plt.yscale('log')
# plt.xticks(rotation=15) 
plt.ylim(top=1600)
# sns.move_legend(g, "lower left", bbox_to_anchor=(.55, .45), title='Platform')
# g.fig.subplots_adjust(top=0.92, wspace = 0.1)

# g.fig.suptitle('Isolation overhead')
g.savefig("e2e.png", bbox_inches='tight')
g.savefig("e2e.pdf", bbox_inches='tight')