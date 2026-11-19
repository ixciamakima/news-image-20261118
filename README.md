# The World in One Day — An Illustrated Atlas

[![Bounty](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![Rank](https://make.fun/badge/news-image-20261118/ixciamakima/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![Reward](https://make.fun/badge/news-image-20261118/ixciamakima/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118)

Entry for the make.fun bounty [news-image-20261118](https://make.fun/bounty/news-image-20261118):
**sum up Wednesday 18 November 2026's world news in one image.**

One 1024×1024 plate, drawn as an illustrated atlas page instead of a text
newspaper. The day's lead — Iran's overnight strikes on US sites in Kuwait
and Bahrain — is painted as a full-width night scene across the Strait of
Hormuz. Below it, a hand-drawn world map pins fourteen of the day's stories
to where they happened, four top stories run beside the map, and twelve
numbered scene cards illustrate the rest: Xi and Putin in Shenzhen, the
Democrats' 56–44 Senate win, Nvidia's +5% beat, the COP31 stocktake in
Antalya, Waymo's robotaxi recall, Myanmar's genocide verdict, England's
97-run Ashes win in Hobart, the Houthis retaking Bab el-Mandeb, Ford's
CATL-tech battery cells, the Earthshot green carpet in Mumbai, Ghana's
$60M jet row, and the split verdict on the Hunger Games prequel.

In total the plate carries **43 verified stories** from that one day —
1 lead, 4 top stories, 12 illustrated scenes and 26 numbered briefs —
across six regions and every beat: war, politics, business, tech, climate,
sport and culture. A markets strip (gold, Brent, Nvidia, the rupee, Indian
bonds) and a full source line close the page.

## How to run

```sh
python3 main.py            # writes entry.png (path from $MAKEFUN_OUTPUT_DIR or /output)
python3 main.py out.png    # or pass an explicit output path
```

Python 3 with Pillow is the only dependency; no network is used. The
render is fully deterministic — every random-looking element (stars,
skylines, paper grain) comes from fixed seeds, so two runs produce a
byte-identical `entry.png` (sha256
`256ba70348d3bb26d27ccca1abf5dc9474fb00d344fc0af0b7aff3ae710523dd`,
642,780 bytes at 1024×1024).

## Sources

Every story was first reported on Wednesday 18 November 2026 and is
credited on the plate: Reuters, BBC, AP, NPR, ESPNcricinfo, UN News,
Just Security, Level Headlines, Morning Brief, The Weekly Anthropocene
and the Bangkok Post. Figures in the markets strip are the day's reported
closes and moves, not forecasts.
