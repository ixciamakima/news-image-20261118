# The World in One Day — An Illustrated Atlas

[![news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![Rank](https://make.fun/badge/news-image-20261118/ixciamakima/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![Reward](https://make.fun/badge/news-image-20261118/ixciamakima/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118)

An illustrated atlas plate summing up Wednesday 18 November 2026 in a
single 1024×1024 image: a night painting of the Hormuz lead story (Iran
strikes Kuwait & Bahrain), a hand-drawn world map with 14 numbered pins,
a Top Stories column, 12 illustrated scene cards and 26 numbered briefs —
43 verified stories across 6 regions, drawn programmatically with Pillow.

## Run

```sh
python3 main.py [output_dir]
```

The program writes `entry.png` to the given directory, or to
`MAKEFUN_OUTPUT_DIR`, or to `/output` when neither is set. It needs no
network and writes nothing anywhere else. Python 3.12+ and Pillow 10+.

## Entry

- `main.py` — the whole entry: layout, painting, map, cards and briefs.
- `entry.png` — the rendered image (1024×1024, under 1 MiB), produced by
  running `main.py`; deterministic across runs (identical SHA-256).
- `LICENSE` — MIT.
