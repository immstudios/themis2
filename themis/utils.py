cuvid_decoders = {
    "h264" : "h264_cuvid",
    "hevc" : "hevc_cuvid",
    "mjpeg" : "mjpeg_cuvid",
    "mpeg1video" : "mpeg1_cuvid",
    "mpeg2video" : "mpeg2_cuvid",
    "mpeg4" : "mpeg4_cuvid",
    "vc1" : "vc1_cuvid",
    "vp8" : "vp8_cuvid",
    "vp9" : "vp9_cuvid",
}

class ThemisProgress(dict):
    pass


def has_nvidia():
    return False #TODO
