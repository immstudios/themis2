__all__ = ["ThemisOutput"]

from .defaults import *
from .utils import *

class ThemisOutput(object):
    def __init__(self, parent, output_path, **kwargs):
        self.parent = parent
        self.index = len(parent.outputs)
        self.output_path = str(output_path)
        self.args = {
                "width" : 1920,
                "height" : 1080,
                "aspect_ratio" : False,
                "fps" : 25,
                "audio_sample_rate" : "48000",
                "video_codec" : None,
                "audio_codec" : None,
                "video_index" : 0,
                "audio_index" : 0,
            }
        self.args.update(kwargs)
        for source_key in default_values:
            defaults = default_values[source_key].get(self.args[source_key], {})
            for key in defaults:
                if not key in self.args:
                    self.args[key] = defaults[key]

    @property
    def aspect_ratio(self):
        try:
            if not self["aspect_ratio"]:
                raise KeyError
            if type(self["aspect_ratio"]) == float:
                n, d = self["aspect_ratio"], 1
            elif type(self["aspect_ratio"]) == str:
                n, d = [float(r) for r in self["aspect_ratio"].replace(":", "/").split("/")]
            elif type(self["aspect_ratio"]) in [tuple, list]:
                n, d = self["aspect_ratio"]
        except (KeyError, IndexError, ValueError):
            n, d = self["width"], self["height"]
        return guess_aspect(n, d)

    @property
    def has_video(self):
        return self["video_codec"] is not None

    @property
    def has_audio(self):
        return self["audio_codec"] is not None

    def __getitem__(self, key):
        return self.args.get(key, None)


    def build(self):
        result = []

        #
        # Video encoding profile
        #

        if self.has_video:
            if self["video_codec"] == "h264":
                result.extend([
                        "-pix_fmt", self["pixel_format"],
                        "-b:v", self["video_bitrate"],
                        "-g", self["gop_size"],
                        "-preset:v", self["video_preset"],
                        "-profile:v", self["video_profile"]
                    ])

                if has_nvidia:
                    result.extend([
                            "-c:v", "h264_nvenc",
                            "-strict_gop", "1",
                            "-no-scenecut", "1",
                        ])
                else:
                    result.extend([
                            "-c:v", "libx264",
                            "-x264opts", "keyint={}:min-keyint={}:scenecut=-1".format(self["gop_size"], self["gop_size"])
                        ])

            elif self["video_codec"] == "dnxhd":
                result.extend([
                        "-pix_fmt", self["pixel_format"],
                        "-c:v", "dnxhd"
                    ])

        #
        # Audio encoding profile
        #

        if self.has_audio:
            codec_dict = {
                    "aac" : "libfdk_aac"
                }
            if self["audio_codec"] in codec_dict:
                audio_codec = codec_dict[self["audio_codec"]]
            else:
                audio_codec = self["audio_codec"]
            result.extend([
                    "-c:a", audio_codec,
                    "-ar", self["audio_sample_rate"]
                ])

            if self["audio_bitrate"]:
                result.extend([
                        "-b:a", self["audio_bitrate"]
                    ])

        result.append(self.output_path)
        return result

