"""
Created by @dtheodor at 2015-09-06
"""
from properconfig import ConfigParser

if __name__ == "__main__":
    with open("config.conf") as f:
        parser = ConfigParser(description="test")\
            .enable_environ(prefix="LOL")\
            .enable_cli_conf_file()\
            .enable_local_conf_file(fp=f)
    parser.add_argument('-v', '--verbose', type=int, required=True, default=2)

    in_args = "-conf other_config.conf".split()

    args = parser.parse_known_args(in_args)
    print parser.option_sources
    print args
