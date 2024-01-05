## LF-Voice 

### Overview

The LF model is the most popular voice model. It was originally implemented as an appendix to my PhD dissertation. This repo is an improved version in Python.

The LF model is made of two curves: an exponentially growing sinusoid followed by a return curve (also an exponential function) at the excitation instant, T<sub>e</sub>.

Two common ways to provide LF model parameters are (1) generative and (2) descriptive. The "descriptive set" is better suited to analyze voice dynamics while the "generative set" is needed to compute synthesis parameters (aka waveform parameters) to produce the excitation signal.

The synthesis parameters are iteratively worked out by following the restriction that the "positive area" contained by the curves is equal to the "negative area". The waveform is efficiently produced by 

* a 2nd-order filter (the exponential growing sinusoid), and
* a 1st-order filter (the return curve).

### Scripts

The LF class is implemented in lf_voice.py, while lf_main.py is a driver script.

Only math, re, getopt, and matplotlib modules are required. These modules are so common so no requirements.txt is included. 

### Execution

At shell, type<br>
```python3 lf_main.py``` # will take default values

or to use generative set of parameters,<br>
```python3 lf_main.py -g "125, -200, 6., 4.5, 0.2" -s 20000 -p```

or to use descriptive of parameters,<br>
```python3 lf_main.py -d "125, -200, 0.5, 1.0, .025" -s 20000 -p```

or to display a usage page, type<br>
```python3 lf_main.py -h```

### References
* Fant, Liljencrants, and Lin: "A four-parameter model of glottal flow", _STL-QPSR_, pp. 1-13
* Lin: _"Speech Production Theory and Articulatory Speech Synthesis,"_ ISSN 0280-9850, Ph.D. Thesis, Royal Institute of Technology, Sweden. 
  
### License
Distributed under [the MIT License.](https://www.mit.edu/~amini/LICENSE.md)

