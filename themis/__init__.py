from nxtools import *

class ThemisProgress(dict):
    pass

class ThemisOutput(object):
    def __init__(self, **kwargs):
        self.args = {
                "width" : 1920,
                "height" : 1080,
                "fps" : 25,
                "video_codec" : "h264",
                "audio_codec" : "aac"
            }
        self.args.update(kwargs)
        for source_key in default_values:
            defaults = default_values[source_key].get(self.args[source_key], {})
            for key in defaults:
                if not key in self.args:
                    self.args[key] = defaults[key]


    def build(self):
        result = []
        return result


class Themis(object):
    def __init__(self, *args):
        self.input_files = [FileObject(path) for path in args]
        outputs = []
        for input_file in self.input_files:
            if not (input_file.exists and input_file.size):
                raise IOError, "{} is not a valid file."


    def add_output(self, **kwargs):
        self.outputs.append(ThemisOutput(**kwargs))


    def start(self, **kwargs):
        progress_handler = kwargs.get("progress_handler", None)

        if not self.input_files:
            logging.error("Unable to start transcoding. No input file specified.")
            return False

        if not outputs:
            logging.error("Unable to start transcoding. No output profile specified.")
            return False

        cmd = ["-y"]

        for input_file in self.input_files:
            pass
