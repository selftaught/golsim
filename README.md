# Game of life clone
## Intro

This is yet another Game of Life clone, developed using the [pygame library](https://github.com/pygame/pygame). This project was started out of boredom, an interest play around with pygame / cellular automata. It's a WIP and has limited functionality with limited patterns available. The existing open source software [Golly](https://github.com/jimblandy/golly) is the recommended software for simulating Conway's Game of Life, as well as the [simulator](https://conwaylife.com/) on the official website.

[![Build Status](https://app.travis-ci.com/selftaught/GameOfLife.svg?token=Tx7EAKup6EXJbMTwywxS&branch=main)](https://app.travis-ci.com/selftaught/GameOfLife)

![Game of Life](https://i.imgur.com/HfXrR09.png)

## Install requirements

1. Create venv: `python3 -m venv venv`
2. Activate venv: `source venv/bin/activate`
3. Install requirements: `pip3 install -r requirements.txt`

## Run the game

`python3 game.py`

## Contributing

1. Fork it
2. Create feature branch (`git checkout -b feature/adding-xyz`)
3. Make some changes and commit (`git commit -m '...'`)
4. Push changes to remote feature branch (`git push origin feature/adding-x-and-y`)
5. Create PR when feature branch is ready for review

## TODO

- [ ] Cell selection & controls (copy, cut, save)
- [ ] Increase cell array size to something like 5000x5000
- [ ] Start with a zoomed in view at the center of the cell array
- [ ] Zooming in/out on cell array (increase/decrease number of visible cells)
- [ ] Panning to view other parts of the cell array when zoomed
- [ ] Autosave game cell array seed to a file for replay
- [ ] Rotate selected pattern by 90 degrees on hot key
