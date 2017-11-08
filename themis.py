#!/usr/bin/env python

from nxtools import *
from themis import Themis

for source_file in get_files("test/input"):
    t = Themis(source_file)
    t.add_output(output_dir="test/output")
    t.start()

