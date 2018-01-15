import os

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
                "loudnorm" : -23,
                "fps" : 25,
                "overlay" : False,
                "use_temp_file" : True,            # Encode to temporary file
                "temp_dir" : False,            # If false, use same directory as target
                "temp_prefix" : ".creating."
            }
        self.settings.update(kwargs)
        self.outputs = []
        self.input_files = []
        self.video_tracks = []
        self.audio_tracks = []

        for input_file in args:
            if isinstance(input_file, FileObject):
                self.input_files.append(input_file)
            elif type(input_file) in string_types:
                self.input_files.append(FileObject(input_file))
            else:
                raise TypeError, "{} must be string of FileObject type"

        for i, input_file in enumerate(self.input_files):
            if not (input_file.exists and input_file.size):
                raise IOError, "{} is not a valid file".format(input_file)
            input_file.probe_result = ffprobe(input_file)
            input_file.input_args = []
            if not input_file.probe_result:
                raise IOError, "Unable to open media file {}".format(input_file)

            for stream in input_file.probe_result["streams"]:
                if stream["codec_type"] == "video":
                    width = stream["width"]
                    height = stream["height"]

                    fps_n, fps_d = [float(e) for e in stream["r_frame_rate"].split("/")]
                    fps = fps_n / fps_d

                    try:
                        dar_n, dar_d = [float(e) for e in stream["display_aspect_ratio"].split(":")]
                        if not (dar_n and dar_d):
                            raise Exception
                    except Exception:
                        dar_n, dar_d = float(stream["width"]), float(stream["height"])
                    aspect = dar_n / dar_d
                    aspect =  guess_aspect(dar_n, dar_d)

                    # HW decoding of video track
                    if has_nvidia:
                        if stream["codec_name"] in cuvid_decoders:
                            input_file.input_args.extend(["-c:v", cuvid_decoders[stream["codec_name"]]])
                            if self["deinterlace"]:
                                input_file.input_args.extend(["-deint", "adaptive"])
                            if self["drop_second_field"]:
                                input_file.input_args.extend(["-drop_second_field", "1"])

                    self.video_tracks.append({
                            "faucet" : "{}:{}".format(i, stream["index"]),
                            "index" : len(self.video_tracks),
                            "input_file_index" : i,
                            "width" : width,
                            "height" : height,
                            "fps" : fps,
                            "aspect" : aspect
                        })

                elif stream["codec_type"] == "audio":
                    self.audio_tracks.append({
                            "faucet" : "{}:{}".format(i, stream["index"]),
                            "index" : len(self.video_tracks),
                            "input_file_index" : i,
                            "language" : stream.get("tags", {}).get("language", "eng")
                        })

        logging.debug("Themis transcoder initialized")


    def __getitem__(self, key):
        return self.settings.get(key, None)

    def add_output(self, output_path, **kwargs):
        self.outputs.append(ThemisOutput(self, output_path, **kwargs))


    @property
    def filter_chain(self):
        filters = []

        voutputs = [output.index for output in self.outputs if output.has_video]
        aoutputs = [output.index for output in self.outputs if output.has_audio]

        if self["overlay"] and os.path.exists(str(self["overlay"])):
            splitter = "".join(["[overlay{}]".format(i) for i in voutputs])
            filters.append("movie={},split={}{}".format(self["overlay"], len(voutputs), splitter))


        for i, output in enumerate(self.outputs):
            if output.has_video:
                track = self.video_tracks[output["video_index"]]

                link_filters = []

                if not has_nvidia and self["deinterlace"]:
                    link_filters.append("yadif")

                if track["aspect"] != output.aspect_ratio:
                    if output.aspect_ratio > track["aspect"]: # pillarbox
                        h = track["height"]
                        w = track["height"] * output.aspect_ratio
                        y = 0
                        x = (w - track["width"]) / 2.0
                    else: # letterbox
                        w = track["width"]
                        h = track["width"] * (1/track["aspect"])
                        x = 0
                        y = (h - track["height"]) / 2.0

                    link_filters.append("pad={}:{}:{}:{}:black".format(w, h, x, y))

                elif output["width"] != track["width"] or output["height"] != track["height"]:
                    link_filters.append("scale={}:{}".format(output["width"], output["height"]))


                link = "[{}]".format(track["faucet"])
                link += ",".join(link_filters or ["null"])
                link += "[outv{}]".format(i)
                filters.append(link)

                #TODO: per output overlay
                if self["overlay"]:
                    #TODO: if overlay needs to be scaled
                    filters.append("[overlay{}]scale={}:{}[overlay{}]".format(i,output["width"], output["height"], i))
                    filters.append("[outv{i}][overlay{i}]overlay[outv{i}]".format(i=i))

            if output.has_audio and self.audio_tracks:
                track = self.audio_tracks[output["audio_index"]]
                link_filters = []
                if self["loudnorm"]:
                    link_filters.append("loudnorm=i={}".format(self["loudnorm"]))

                link = "[{}]".format(track["faucet"])
                link += ",".join(link_filters or ["null"])
                link += "[outa{}]".format(i)
                filters.append(link)

        return ";".join(filters)




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
            if input_file.input_args:
                cmd.extend(input_file.input_args)
            cmd.extend(["-i", input_file.path])

        cmd.extend(["-filter_complex", self.filter_chain])

        for i, output in enumerate(self.outputs):
            if output.has_video:
                cmd.extend(["-map", "[outv{}]".format(i)])
            if output.has_audio and self.audio_tracks:
                cmd.extend(["-map", "[outa{}]".format(i)])

            #if self["fps"] !=


            cmd.extend(output.build())

        is_success = ffmpeg(*cmd)

        if is_success:
            if self["use_temp_file"]:
                for output in self.outputs:
                    os.rename(output.temp_path, output.output_path)
        else:
            if self["use_temp_file"]:
                for output in self.outputs:
                    try:
                        os.remove(output.temp_path)
                    except Exception:
                        pass


        logging.debug("Themis returned {}".format(is_success))
        return is_success
