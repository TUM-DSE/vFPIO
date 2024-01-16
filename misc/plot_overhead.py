import seaborn as sns
import pandas
import matplotlib as mpl  # type: ignore
import matplotlib.pyplot as plt
from typing import Any, Dict, List, Union

FORMATTER: Dict[str, mpl.ticker.Formatter] = {}
COLUMN_ALIASES: Dict[str, str] = {}

FONTSIZE = 14

sns.set(font_scale=1.6)
sns.set_style("ticks")

data1 = pandas.read_csv("performance_overhead_perf_host.csv")
data2 = pandas.read_csv("performance_overhead_perf_fpga.csv")
print(data1.head())
# print(data["app"][0])
palette = sns.color_palette("pastel")

color1 = palette[0]
color2 = palette[1]
color3 = palette[2]

hatch1 = ""
hatch2 = "."
# hatch3 = "*"

hatch_list = [hatch1, hatch2]

palette_console = [color1, color3]


width = 14 # \textwidth is 7 inch
height = 5

fig, axs = plt.subplots(ncols=2,sharex=True)
fig.set_size_inches(width, height)
fig.suptitle("Lower is better ↓",fontsize=18, color="navy", weight="bold",x = 0.55, y=0.9)
# plt.yscale('log')


g1 = sns.barplot(
            ax=axs[0],
            data=data1,
            x="Size[KiB]",
            y="Cycle",
            hue="Platform",
            # x=column_alias("system"),
            # y=column_alias("nginx-requests"),
            # ci="sd",
            errorbar=None,
            palette=palette_console,
            edgecolor="k",
            # errcolor="black",
            # errwidth=1,
            width=0.8,
            capsize=0.2,
            alpha=.6,
            # height=height,
            # aspect=nginx_width/height,
        )

# apply hatch
for idx, bar in enumerate(axs[0].containers[1]):
    bar.set_hatch(hatch_list[1])

# # apply bar value
# for c in axs[0].containers:
#     labels = [f'{(v.get_height()/1000):.1f}k' for v in c]
#     axs[0].bar_label(c, labels=labels, label_type='edge',
#                     padding=3, 
#                     # fontsize=fontsize, rotation=rotation
#                     )


# ff = FORMATTER["krps"]
# axs[0].yaxis.set_major_formatter(ff)
axs[0].set_yscale('log')
# g1.set(xticks=[], xticklabels=[], xlabel="(a) Throughput of the storage applications")
# g1.set_title("Lower is better ↓", fontsize=15, color="navy", weight="bold",
#                     x = 0.50, y=1, pad=10)
axs[0].set_title("(a) perf-host", weight="bold")
axs[0].legend(loc='upper left')

g2= sns.barplot(
            ax=axs[1],
            data=data2,
            x="Size[KiB]",
            y="Cycle",
            hue="Platform",
            # ci="sd",
            errorbar=None,
            palette=palette_console,
            edgecolor="k",
            # errcolor="black",
            errwidth=1.5,
            # capsize=0.2,
            width=0.8,
            alpha=.6,
            # height=height,
            # aspect=nginx_width/height,
        )
axs[1].set_yscale('log')
axs[1].set_title("(b) perf-fpga", weight="bold")

for idx, bar in enumerate(axs[1].containers[1]):
    bar.set_hatch(hatch_list[1])

# g2.set(xticks=[], xticklabels=["aaa"], xlabel="(b) Throughput of the network applications")
# g2.set_title("Higher is better ↑", fontsize=10, color="navy", weight="bold",
#                     x = 0.50, y=1, pad=10)

# sns.despine(ax=axs[0])
# sns.despine(ax=axs[1])
plt.legend(loc='upper left')

fig.tight_layout()
fig.savefig("perf_overhead.png", bbox_inches='tight')
fig.savefig("perf_overhead.pdf", bbox_inches='tight')