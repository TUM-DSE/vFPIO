import seaborn as sns
import pandas
import matplotlib  # type: ignore
import matplotlib.pyplot as plt
from typing import Any, Dict, List, Union

matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
FORMATTER: Dict[str, matplotlib.ticker.Formatter] = {}
COLUMN_ALIASES: Dict[str, str] = {}

FONTSIZE = 14
# matplotlib.rcParams["text.usetex"] = True
sns.set(font_scale=1.6)
sns.set_style("ticks")

data1 = pandas.read_csv("performance_isolation.csv")
data2 = pandas.read_csv("context_switch.csv")
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
palette_console = [color1, color3, color2]


width = 14  # \textwidth is 7 inch
height = 5

fig, axs = plt.subplots(ncols=2)
fig.set_size_inches(width, height)
fig.suptitle(
    "Lower is better ↓", fontsize=18, color="navy", weight="bold", x=0.55, y=0.9
)
# plt.yscale('log')


g1 = sns.barplot(
    ax=axs[0],
    data=data1,
    x="priority",
    y="cycle",
    # hue="platform",
    # x=column_alias("system"),
    # y=column_alias("nginx-requests"),
    # ci="sd",
    errorbar=None,
    palette=palette_console,
    edgecolor="k",
    # errcolor="black",
    # errwidth=1,
    width=0.5,
    capsize=0.2,
    alpha=0.6,
    # height=height,
    # aspect=nginx_width/height,
)

# # apply hatch
# for idx, bar in enumerate(axs[0].containers[1]):
#     bar.set_hatch(hatch_list[1])

# # apply bar value
# for c in axs[0].containers:
#     labels = [f'{(v.get_height()/1000):.1f}k' for v in c]
#     axs[0].bar_label(c, labels=labels, label_type='edge',
#                     padding=3,
#                     # fontsize=fontsize, rotation=rotation
#                     )


# ff = FORMATTER["krps"]
# axs[0].yaxis.set_major_formatter(ff)
# axs[0].set_yscale('log')
g1.set(xlabel="")
# g1.set_title("Lower is better ↓", fontsize=15, color="navy", weight="bold",
#                     x = 0.50, y=1, pad=10)
axs[0].set_title("(a) Clock cycles", weight="bold")


g2 = sns.barplot(
    ax=axs[1],
    data=data2,
    x="size",
    y="count",
    hue="platform",
    # ci="sd",
    errorbar=None,
    palette=palette_console,
    edgecolor="k",
    # errcolor="black",
    errwidth=1.5,
    # capsize=0.2,
    width=0.8,
    alpha=0.6,
    # height=height,
    # aspect=nginx_width/height,
)
# axs[1].set_yscale('log')
axs[1].set_title("(b) Context switch", weight="bold")

for idx, bar in enumerate(axs[1].containers[1]):
    bar.set_hatch(hatch_list[1])

g2.set(xlabel="Size [KiB]")
# g2.set_title("Higher is better ↑", fontsize=10, color="navy", weight="bold",
#                     x = 0.50, y=1, pad=10)

# sns.despine(ax=axs[0])
# sns.despine(ax=axs[1])

plt.legend(loc="lower left")

fig.tight_layout()
fig.savefig("perf_sched.png", bbox_inches="tight")
fig.savefig("perf_sched.pdf", bbox_inches="tight")
