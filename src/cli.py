import argparse
COMMAND_LINE_PARSER = argparse.ArgumentParser("potstein", description="A simple music player", usage="potstein <path to playlist>", epilog="example: potstein /home/user/music")
_ = COMMAND_LINE_PARSER.add_argument("playlistpath")
COMMAND_LINE_ARGS = COMMAND_LINE_PARSER.parse_args()
