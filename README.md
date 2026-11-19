[![make.fun](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/ixciamakima/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/ixciamakima/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118)

# The World in One Day — An Illustrated Atlas

Entry to [make.fun's news-image-20261118](https://make.fun/bounty/news-image-20261118):
sum up Wednesday 18 November 2026's world news in one image.

v3 rebuilds the v2 illustrated atlas from scratch with one critical
fix: the program now writes `entry.png` **only** to the output
directory the grader gives it (`argv[1]`, else `MAKEFUN_OUTPUT_DIR`,
else `/output`) — never to the repo directory. v2 was rejected by the
server on `run_completes` because it wrote into the read-only `/bot`
directory; this version passes a faithful grader simulation
(read-only copy, run as `nobody`, `python3 -P -s`, 60 s limit) with
exit 0 and a byte-identical image.

## The image

An atlas plate on deep navy with a gold masthead: a painted night
scene of the lead story (Iran strikes Kuwait & Bahrain over the
Strait of Hormuz), a hand-drawn world map with 14 numbered pins, a
Top Stories column, 12 illustrated scene cards, and 26 numbered
briefs. **43 verified stories** (Reuters, BBC, AP, NPR,
ESPNcricinfo, UN News, Just Security, Level Headlines, Morning
Brief, The Weekly Anthropocene, Bangkok Post), **13 illustrated
scenes** plus the map, 6 regions.

## Run it

```sh
python3 main.py <output-dir>   # writes <output-dir>/entry.png
```

With no argument it writes to `$MAKEFUN_OUTPUT_DIR`, else `/output`.
Needs Python 3.12+ and Pillow only; no network, no writes anywhere
else, deterministic (repeated runs produce a byte-identical PNG).
1024×1024, about 677 KB.

## Files

- `main.py` — the whole generator, self-contained (stdlib + Pillow).
- `entry.png` — the rendered image (regenerate with the command above).
- `LICENSE` — MIT.
