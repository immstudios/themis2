from nxtools import *
from nxtools.media import *

from .profiles import *

class ThemisProgress(dict):
    pass



class Themis(object):
    def __init__(self, *args):
        self.input_files = []
        self.outputs = []
        for input_file in args:
            if isinstance(input_file, FileObject):
                self.input_files.append(input_file)
            elif type(input_file) in string_types:
                self.input_files.append(FileObject(input_file))
            else:
                raise TypeError, "{} must be string of FileObject type"
        for input_file in self.input_files:
            if not (input_file.exists and input_file.size):
                raise IOError, "{} is not a valid file".format(input_file)
            input_file.probe_result = ffprobe(input_file)
            if not input_file.probe_result:
                raise IOError, "Unable to open media file {}".format(input_file)
        logging.debug("Themis transcoder initialized")


    def add_output(self, **kwargs):
        self.outputs.append(ThemisOutput(**kwargs))


    def start(self, **kwargs):
        progress_handler = kwargs.get("progress_handler", None)

        if not self.input_files:
            logging.error("Unable to start transcoding. No input file specified.")
            return False

        if not self.outputs:
            logging.error("Unable to start transcoding. No output profile specified.")
            return False

        cmd = ["-y"]

        for input_file in self.input_files:
            cmd.extend([
                    "-i", input_file.path
                ])

        for output_profile in self.outputs:
            cmd.extend(output_profile.build())

        print (cmd)


