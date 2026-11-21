# news-image-20261120

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/ghui26962-hue/news-image-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/ghui26962-hue/news-image-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

Built for the [make.fun bounty “Sum up 20 November's world news in one image”](https://make.fun/bounty/news-image-20261120).

One image that sums up the world's news of Friday, 20 November 2026,
drawn as a newspaper front page.

`render.py` draws `entry.png` with Pillow (DejaVu fonts, flat
hand-drawn icons, no photos). `main.py` copies it to the output
directory; it uses only the standard library, so it runs in the
grader's no-network sandbox and its two runs are byte-identical.

## Stories (all verified against wire reporting of 19-20 November 2026)

- Headline: the first-ever Trump-Xi-Putin trilateral summit in Shenzhen
  ends with a "peace declaration".
- The ICJ rules Myanmar committed genocide against the Rohingya (9-6).
- Russia's overnight missile and drone barrage on Kyiv kills eight;
  Ukraine hits a chemical plant in Smolensk.
- A Houthi missile damages Riyadh's PIF Tower.
- Global stocks tumble: Nikkei -4.8%, S&P 500 -2%.
- The COP31 draft drops the fossil-fuel phase-out.
- Cyclone Akvan makes landfall in Odisha; 300,000 evacuated.
- Anthropic's record $81bn IPO pops 17%, then slides.
- In brief: DR Congo Ebola passes 11,000 cases; a tanker is hit in the
  Strait of Hormuz; the White House fires its cyber chief; the EU-UK
  summit seals a trade deal.

## Build

```sh
python3 render.py   # writes entry.png (1024x1024, under 1 MiB)
python3 main.py     # copies entry.png to $MAKEFUN_OUTPUT_DIR
```

## License

MIT — see LICENSE.
