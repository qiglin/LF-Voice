## LF-Voice 

### Overview

The LF model is the most popular voice model. It was originally implemented as an appendix to my PhD dissertation. This repo is an improved version in Python.

The LF model is made of two curves: an exponentially growing curve followed by an return curve at the excitation instant, Te.

Two common ways to provide LF model parameters are generative and descriptive. The "descriptive set" is better suited to analyze voice dynamics while the "generative set" is needed to compute synthesis parameters (aka waveform parameters) to produce the excitation signal.

The synthesis parameters are iteratively worked out by following the restriction that the "positive area" contained by the curves is equal to the "negative area". The waveform is efficiently produced by a 2nd-order filter (the exponential curve) and a 1st-irder filter (the return curve).

### Scripts

The LF class is implemented in lf_voice.py, while lf_main.py is a driver script.

Only math, re, getopt, and matplotlib modules are required.

### Execution

At shell, type<br>
python3 lf_main.py # will take default values

or to use generative set of parameters,<br>
python3 lf_main.py -g "125, 0.1, 6.,5.0, 0.0" -s 20000 -p

or to use descriptive of parameters,<br>
python3 lf_main.py -d "125, -200, 0.5, 1.0, .025" -s 20000 -p

or to get a usage page, type<br>
python3 lf_main.py -h

### License
Distributed under [the MIT License.](https://www.mit.edu/~amini/LICENSE.md)

