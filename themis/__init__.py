from nxtools import *
from nxtools.media import *

from .output import *
from .utils import *


class Themis(object):
    def __init__(self, *args, **kwargs):
        self.settings = {
                "expand_tv_levels" : False,
                "deinterlace" : False,
                "drop_second_field" : True,
            }
        self.settings.update(kwargs)
        self.input_files = []
        self.outputs = []
        self.video_sink = None
        self.audio_sinks = []
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
            input_file.input_args = []
            if not input_file.probe_result:
                raise IOError, "Unable to open media file {}".format(input_file)
        logging.debug("Themis transcoder initialized")

    @property
    def has_nvidia(self):
        return self.settings.get("has_nvidia", has_nvidia())


    def add_output(self, **kwargs):
        self.outputs.append(ThemisOutput(**kwargs))


    @property
    def filter_chain(self):

        for i, input_file in enumerate(self.input_files):
            for stream in input_file.probe_result["streams"]:
                if stream["codec_type"] == "video":
                    if self.video_sink:
                        continue
                self.video_sink = "{}:{}".format(i, stream["index"])

                if has_nvidia:
                    if stream["codec_name"] in cuvid_decoders:
                        input_file.input_args.extend(["-c:v", cuvid_decoders[stream["codec_name"]]])
                    if self.settings["deinterlace"]:
                        input_file.input_args.extend(["-deint", "adaptive"])
                    if self.settings["drop_second_field"]:
                        input_file.input_args.extend(["-drop_second_field", "1"])
                    #TODO: scale?



        result = ""

        # we have video
        if self.video_sink:
            result += "[{}]".format(self.video_sink)
            if not has_nvidia and self.settings["deinterlace"]:
                result += "yadif"
        result += "[video_track]"


        return result



    def start(self, **kwargs):
        progress_handler = kwargs.get("progress_handler", None)

        if not self.input_files:
            logging.error("Unable to start transcoding. No input file specified.")
            return False

        if not self.outputs:
            logging.error("Unable to start transcoding. No output profile specified.")
            return False

        cmd = []

        for input_file in self.input_files:
            if input_file.input_args:
                cmd.extend(input_file.input_args)
            cmd.extend(["-i", input_file.path])

        cmd.extend(["-filter_complex", self.filter_chain])

        for output_profile in self.outputs:
            if output_profile.has_video:
                cmd.extend(["-map", "[video_track]"])
            cmd.extend(output_profile.build())

        print (cmd)


