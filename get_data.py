"""Download Impect's free Bundesliga 2023-24 data into ./data.

The data belongs to Impect and is not included in this repo. This script
fetches it from Impect's own GitHub so you agree to their terms directly:
https://github.com/ImpectAPI/open-data (credit Impect, non-commercial use only).

The notebook runs this for you the first time. You can also run it on its own:
python get_data.py
"""
import json
import urllib.request
from pathlib import Path

RAW = "https://raw.githubusercontent.com/ImpectAPI/open-data/main/data"
API = "https://api.github.com/repos/ImpectAPI/open-data/contents/data/player_kpis"
DATA = Path(__file__).parent / "data"

BASE_FILES = ["kpi_definitions.json", "players/players_743.json",
              "squads/squads_743.json", "matches/matches_743.json"]
MATCHES = 306   # every match of the 2023-24 Bundesliga season


def fetch(url, dest):
    """Download one file, skipping it if it's already there."""
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_suffix(".part")
    urllib.request.urlretrieve(url, partial)
    partial.rename(dest)   # only counts as downloaded once it's complete


def have_data():
    base = all((DATA / Path(name).name).exists() for name in BASE_FILES)
    matches = len(list((DATA / "player_kpis").glob("*.json")))
    return base and matches >= MATCHES


def download_data():
    if have_data():
        print("Impect data already downloaded.")
        return

    print("Downloading Impect's free Bundesliga 2023-24 data from their GitHub.")
    print("About 84MB, first run only.")
    for name in BASE_FILES:
        fetch(f"{RAW}/{name}", DATA / Path(name).name)

    with urllib.request.urlopen(API) as response:
        files = json.load(response)
    for i, f in enumerate(files, 1):
        fetch(f["download_url"], DATA / "player_kpis" / f["name"])
        print(f"\rmatch files: {i}/{len(files)}", end="")
    print("\ndone")


if __name__ == "__main__":
    download_data()
