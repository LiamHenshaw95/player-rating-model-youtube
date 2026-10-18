# Player rating model: dribbling winger

A simple player rating model built on Impect's free Bundesliga 2023-24 data. It goes with the YouTube video *How to build a player rating model like a football club*.

It works in four steps:

1. Write the profile: the attributes you want, in order of importance.
2. Pick the stats that measure them, and give each stat a weight out of 100.
3. Turn every stat into a z-score within the player pool (how far from average), capped at ±3.
4. Multiply by the weights, add them up, and turn the total into a 0-100 rating.

This is the weighted z-score approach (Model 1) from Sahil Gidwani's rating model workshop.

## Run it

```
pip install -r requirements.txt
jupyter lab dribbling_winger_rating.ipynb
```

Run the notebook from the top. The first cell downloads Impect's data from their GitHub into `./data` (about 84MB, first run only). If you'd rather download it on its own first, run `python get_data.py`. You can also open the notebook in VS Code.

## The model in the video

The profile is a winger who beats his man and carries the ball into the box. Each stat is per 90 minutes:

| Part of the profile | Stat | Weight |
|---|---|---|
| Beats his man 1v1 | Ground duels won | 15 |
| | Dribble threat | 15 |
| Carries the ball forward | Distance carried towards goal | 25 |
| Takes defenders out of the game | Defenders bypassed | 20 |
| Creates for others | Shot-creating actions | 8 |
| | Expected assists | 7 |
| Gets into scoring positions | Packing xG | 10 |

The player pool is left wingers, right wingers and attacking midfielders with 900+ minutes. The notebook also:
- re-weights the model for a manager who wants goals from wide (packing xG up to 30), to show how the shortlist changes
- draws a radar of one player across the five parts of the profile, so you can answer "why him?" in one sentence

## Build your own

Change three things in the notebook:
- `WEIGHTS`: the stats and how much each one counts. They must add up to 100.
- `POSITIONS`: who you compare against. Impect's positions are `GOALKEEPER`, `CENTRAL_DEFENDER`, `LEFT_WINGBACK_DEFENDER`, `RIGHT_WINGBACK_DEFENDER`, `DEFENSE_MIDFIELD`, `CENTRAL_MIDFIELD`, `ATTACKING_MIDFIELD`, `LEFT_WINGER`, `RIGHT_WINGER` and `CENTER_FORWARD`.
- `MIN_MINUTES`: the minimum minutes played.

Section 3 of the notebook lists all 103 of Impect's stats with a definition for each, and `find("word")` searches them. To use a stat that isn't in the model yet, add it to `STAT_NAMES` in `helpers.py` with a plain-English name.

## Files

- `get_data.py` downloads Impect's data (the notebook calls it for you).
- `prep.py` adds up each player's matches and turns them into per-90 numbers.
- `helpers.py` handles the plain-English stat names and how the tables and charts look.
- `kpi_groups.json` groups Impect's stats for the list in section 3.
- `dribbling_winger_rating.ipynb` is the model itself.

## Data

The data belongs to **Impect** and is not included in this repo. `get_data.py` downloads it from [github.com/ImpectAPI/open-data](https://github.com/ImpectAPI/open-data), so you get it from Impect directly. By using it you agree to Impect's terms: non-commercial use only, credit Impect as the data provider, and don't pass the data on.

Things to know about Impect's data before you use it:
- It's event data, tagged from match video. There's no tracking data, so nothing on pace and very little off the ball.
- A "dribble" is any carry of more than two steps, so it's closer to a carry than to a take-on.
- Minutes are counted as match share × 90, because Impect's full match includes stoppage time.
- xG includes penalties.

## What the model can't tell you

It ranks players inside one league and doesn't adjust for team or league strength. It can't see pace, decisions or mentality, and it doesn't know about age, contracts or budget. A model doesn't find players. It tells you who to go and watch.

## More

Made by Liam Henshaw. If you want to go further with scouting and recruitment analysis, have a look at the [Football Recruitment Roadmap](https://footballrecruitmentroadmap.carrd.co/) (free) or the [Recruitment Room](https://www.recruitmentroom.co/).

## Licence

The code is MIT licensed (see `LICENSE`). The data stays Impect's.
