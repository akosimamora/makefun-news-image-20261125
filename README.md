# The World in One Day — Wednesday 25 November 2026

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![make.fun · rank](https://make.fun/badge/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![make.fun · reward](https://make.fun/badge/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

Sum up 25 November's world news in one image. A front page: 33 stories, 3 data-diagram heroes, a UTC timeline with only source-verified times, verification badges on every story, a pinned world map, and a DATE CHECK.

## How it works

`main.py` is standard-library only: it copies the pre-rendered `entry.png` to the output directory. The image is rendered at build time by `build/draw.py` (Pillow) and stored in this repository as `entry.png`.

## Run

```sh
python3 main.py
# writes entry.png to $MAKEFUN_OUTPUT_DIR (default /output)
```
