"""Turn Impect's per-match player files into one season table, per 90.

Impect gives each player's totals for each match and position. This adds them
up across the season, works out minutes, and converts everything to per 90.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

DATA = Path(__file__).parent / "data"


def load_json(name):
    return json.loads((DATA / name).read_text())


def metric_definitions():
    """All Impect metrics with their label, definition and group."""
    groups = json.loads((Path(__file__).parent / "kpi_groups.json").read_text())
    order = {kpi_id: (g, i) for g, ids in enumerate(groups.values()) for i, kpi_id in enumerate(ids)}
    group_of = {kpi_id: group for group, ids in groups.items() for kpi_id in ids}
    rows = []
    for d in load_json("kpi_definitions.json"):
        details = d.get("details") or {}
        definition = re.sub(r"<[^>]+>", " ", details.get("definition") or "")
        definition = re.sub(r"\s+", " ", definition).strip() or "No definition supplied by Impect."
        rows.append({
            "group": group_of.get(d["id"], "Other"),
            "metric": details.get("label") or d["name"].replace("_", " ").title(),
            "impect_name": d["name"],
            "definition": definition,
            "short": re.split(r"(?<=[.!?])\s", definition)[0],
            "_order": order.get(d["id"], (99, 0)),
        })
    return pd.DataFrame(rows).sort_values("_order").drop(columns="_order").reset_index(drop=True)


def season_per90():
    players = {p["id"]: p for p in load_json("players_743.json")}
    squads = {s["id"]: s["name"] for s in load_json("squads_743.json")}
    kpi_names = {d["id"]: d["name"] for d in load_json("kpi_definitions.json")}

    totals = defaultdict(lambda: defaultdict(float))
    match_share = defaultdict(float)
    share_by_position = defaultdict(lambda: defaultdict(float))
    share_by_team = defaultdict(lambda: defaultdict(float))
    matches = defaultdict(set)

    for f in sorted((DATA / "player_kpis").glob("*.json")):
        match = json.loads(f.read_text())
        for side in ("squadHome", "squadAway"):
            team = squads[match[side]["id"]]
            # a player gets one row per position he played in the match
            for p in match[side]["players"]:
                pid = p["id"]
                match_share[pid] += p["matchShare"]
                share_by_position[pid][p["position"]] += p["matchShare"]
                share_by_team[pid][team] += p["matchShare"]
                matches[pid].add(match["matchId"])
                for k in p["kpis"]:  # Impect leaves zeros out, so missing = 0
                    totals[pid][k["kpiId"]] += k["value"]

    rows = []
    for pid, share in match_share.items():
        info = players.get(pid, {})
        rows.append({
            "player": info.get("commonname"),
            "team": max(share_by_team[pid], key=share_by_team[pid].get),
            "position": max(share_by_position[pid], key=share_by_position[pid].get),
            "birthdate": info.get("birthdate"),
            "apps": len(matches[pid]),
            # a full match incl. stoppage time is about 98.5 minutes in Impect's
            # seconds, so count minutes as match share x 90 instead
            "minutes": round(share * 90),
            **{name: totals[pid].get(kid, 0.0) for kid, name in kpi_names.items()},
        })

    season = pd.DataFrame(rows)
    season["age"] = ((pd.Timestamp("2024-01-01") - pd.to_datetime(season["birthdate"]))
                     .dt.days / 365.25).round(1)
    stats = list(kpi_names.values())
    per90 = season.copy()
    per90[stats] = season[stats].div(season["minutes"].clip(lower=1), axis=0) * 90
    return per90
