# About
This solves the Cribbage Solitaire minigame in Mobius Front '83.

The script uses `PyScreeze` to capture the screen and locate elements from reference images.

Then, it explores the game's state space by identifying the legal moves from each game state.

It will look for a state that has score 61 or higher, then execute the moves that lead to that state.

If it wasn't able to find such a state within the search limits, then it will instead execute a losing state and then reset.

# Requirements
* [Python 3](https://www.python.org/)
* [pynput](https://pypi.org/project/pynput/)
* [PyScreeze](https://pypi.org/project/PyScreeze/)
* [retry](https://pypi.org/project/retry/)

# Usage

Run `solver.py` while the game window is running. The game needs to be either in a screen which has the `New Game` button visible *or* has the fully dealt layout without any cards yet played.

Might not work for different monitor setups / screen resolutions.

# LICENSE

MIT License

Copyright (c) 2023 Kevin Liu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
