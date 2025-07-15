import argparse
import colorama

colorama.init()


def execute_cli():
    # Parse command line
    parser = argparse.ArgumentParser()
    command_parser = parser.add_subparsers(title="commands")

    #
    # asa me
    #
    me_parser = command_parser.add_parser("me", help="Get my tasks")
    me_parser.add_argument("-a", "--all", action="append", help="Include all tasks, including completed")

    args = parser.parse_args()

    #
    # Execute command
    #
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
