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

def guess_aspect (w, h):
    if 0 in [w, h]:
        return 0
    valid_aspects = [
            (16, 9),
            (4, 3),
            (2.35, 1),
            (5, 4),
            (1, 1)
        ]
    ratio = float(w) / float(h)
    return "{}:{}".format(*min(valid_aspects, key=lambda x:abs((float(x[0])/x[1])-ratio)))


class ThemisProgress(dict):
    pass


def get_has_nvidia():
    return True #TODO

has_nvidia = get_has_nvidia()
