"""Display helpers for the notebook.

Kept out of the notebook so the video only shows the decisions: the profile,
the weights and the results. Nothing in here changes the numbers.
"""
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import HTML

# plain-English names for the Impect stats used in the model
STAT_NAMES = {
    "WON_GROUND_DUELS": "Ground duels won",
    "PXT_DRIBBLE": "Dribble threat",
    "DISTANCE_TO_GOAL_COVERED_DRIBBLE": "Distance carried towards goal",
    "BYPASSED_DEFENDERS": "Defenders bypassed",
    "SHOT_CREATING_ACTIONS": "Shot-creating actions",
    "EXPECTED_GOAL_ASSISTS": "Expected assists",
    "PACKING_XG": "Packing xG",
}

ORANGE, GREY, DARK = "#e8731a", "#9aa5b1", "#1f2522"

plt.rcParams.update({
    "font.size": 13,
    "axes.titlesize": 15,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

CELL = "text-align:left;padding:6px 14px;font-size:16px;border-bottom:1px solid #ddd"


def show(df, highlight=None, decimals=2):
    """A bigger, left-aligned table. Optionally highlights one player's row in orange."""
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_float_dtype(df[col]):
            df[col] = df[col].round(decimals)
    head = "".join(f'<th style="{CELL};font-weight:700">{c}</th>' for c in df.columns)
    rows = []
    for _, r in df.iterrows():
        style = f"background:{ORANGE}22;font-weight:700" if highlight and highlight in r.values else ""
        rows.append(f'<tr style="{style}">' + "".join(f'<td style="{CELL}">{v}</td>' for v in r.values) + "</tr>")
    return HTML(f'<table style="border-collapse:collapse"><tr>{head}</tr>{"".join(rows)}</table>')


def plot_shortlist(shortlist, n=10, highlight=None, title="Shortlist"):
    """Top n players as a bar chart of their 0-100 rating."""
    top = shortlist.head(n).iloc[::-1]
    colours = [ORANGE if p == highlight else GREY for p in top["player"]]
    fig, ax = plt.subplots(figsize=(9, 0.5 * n + 1))
    ax.barh(top["player"], top["rating"], color=colours)
    for y, v in enumerate(top["rating"]):
        ax.text(v + 1, y, str(v), va="center", fontweight="bold")
    ax.set_xlim(0, 110)
    ax.set_xlabel("rating (0-100)")
    ax.set_title(title)
    plt.tight_layout()


def compare(before, after, n=10, track=()):
    """How the top n moved when the weights changed, plus any players you want to track."""
    rank_before = {p: i + 1 for i, p in enumerate(before["player"])}
    rank_after = {p: i + 1 for i, p in enumerate(after["player"])}
    names = list(after["player"].head(n)) + [p for p in track if rank_after[p] > n]
    rows = []
    for p in names:
        was, now = rank_before[p], rank_after[p]
        move = "same" if was == now else (f"up {was - now}" if now < was else f"down {now - was}")
        rows.append({"player": p, "before": was, "after": now, "move": move})
    return pd.DataFrame(rows)


def plot_radar(areas, title):
    """One player's percentile in each key area, as a radar. 50 = the middle of the pool."""
    import numpy as np

    labels, values = list(areas), list(areas.values())
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values_loop, angles_loop = values + values[:1], angles + angles[:1]   # close the shape

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={"polar": True})
    ax.set_theta_offset(np.pi / 2)    # first area at the top
    ax.set_theta_direction(-1)        # go round clockwise
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25", "50", "75", "100"], color=GREY, fontsize=10)
    ax.plot(np.linspace(0, 2 * np.pi, 200), [50] * 200, color=GREY, linestyle="--", linewidth=1)  # middle of the pool

    ax.plot(angles_loop, values_loop, color=ORANGE, linewidth=2.5)
    ax.fill(angles_loop, values_loop, color=ORANGE, alpha=0.25)
    for angle, value in zip(angles, values):
        # score in a small white box on the point itself, so it never hits the area labels
        ax.text(angle, value, str(value), ha="center", va="center", fontweight="bold", color=DARK,
                bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": ORANGE})

    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=13)
    ax.tick_params(axis="x", pad=22)      # push the area names out past the 100 ring
    ax.spines["polar"].set_visible(False)
    ax.set_title(title, pad=40)
    plt.tight_layout()
