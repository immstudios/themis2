__all__ = ["ThemisOutput"]


from defaults import *

has_nvidia = False


class ThemisOutput(object):
    def __init__(self, **kwargs):
        self.args = {
                "width" : 1920,
                "height" : 1080,
                "fps" : 25,
                "audio_sample_rate" : "48000"
            }
        self.args.update(kwargs)
        for source_key in default_values:
            defaults = default_values[source_key].get(self.args[source_key], {})
            for key in defaults:
                if not key in self.args:
                    self.args[key] = defaults[key]

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
            result.extend([
                    "-c:a", self["audio_codec"],
                    "-ar", self["audio_sample_rate"]
                ])

            if self["audio_bitrate"]:
                result.extend([
                        "-b:a", self["audio_bitrate"]
                    ])

        return result

