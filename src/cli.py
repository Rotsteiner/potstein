import argparse
COMMAND_LINE_PARSER = argparse.ArgumentParser("potstein",
                                              description="A simple music player",
                                              epilog="example: potstein /home/user/music -c ./config.py")
_ = COMMAND_LINE_PARSER.add_argument("playlistpath")
_ = COMMAND_LINE_PARSER.add_argument("-c", "--config", help="Path to the configuration file.")
_ = COMMAND_LINE_PARSER.add_argument("-d", "--debugfile",
                                     help= "if debug.enable = True in the config than this flag is used to configure a file where debug output is send to. Examples include other ttys, files, pipes and anything else that the POSIX standard treats as a file.")

COMMAND_LINE_ARGS = COMMAND_LINE_PARSER.parse_args()
