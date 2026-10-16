import argparse
COMMAND_LINE_PARSER = argparse.ArgumentParser("potstein",
                                              description="A simple music player",
                                              epilog="example: potstein /home/user/music -c ./config.py")
_ = COMMAND_LINE_PARSER.add_argument("playlistpath")
_ = COMMAND_LINE_PARSER.add_argument("-c", "--config")

COMMAND_LINE_ARGS = COMMAND_LINE_PARSER.parse_args()
