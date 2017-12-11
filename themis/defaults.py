default_values = {

    "video_codec" : {
        "h264" : {
                "pixel_format" : "yuv420p",
                "video_bitrate"  : "4000k",
                "video_profile" : "main",
                "video_preset" : "slow",
                "gop_size" : 80,
            },

        "dnxhd" : {
                "pixel_format" : "yuv422p",
                "video_bitrate" : "120M",
            }
        },

    "audio_codec" : {
        "aac" : {
                "audio_bitrate" : "192k"
            }
        }
}

