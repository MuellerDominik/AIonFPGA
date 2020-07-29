#!/usr/bin/env python3

'''aionfpga ~ fhnwtoys.training
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

from .definitions import *

rep = [(' ', '-'), ('(', ''), (')', '')]
objects_san = [repl(obj.lower(), rep) for obj in objects]
