#!/usr/bin/env python3

import sys

from nxtools import *
from themis import Themis

for source_file, target_file in get_path_pairs("test/input", "test/output", target_ext="mov"):

    t = Themis(
            source_file,
            use_temp_file=False,
            fps=25
        )

    t.add_output(
            target_file,
            video_codec="dnxhd",
            audio_codec="pcm_s16le",
            video_bitrate="36M"
        )

    t.start()
    print("*"*60)
#    if not t.start():
#        sys.exit(1)

