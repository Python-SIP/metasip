# Copyright (c) 2018 Riverbank Computing Limited.
#
# This file is part of dip.
#
# This file may be used under the terms of the GNU General Public License
# version 3.0 as published by the Free Software Foundation and appearing in
# the file LICENSE included in the packaging of this file.  Please review the
# following information to ensure the GNU General Public License version 3.0
# requirements will be met: http://www.gnu.org/copyleft/gpl.html.
#
# If you do not wish to use this file under the terms of the GPL version 3.0
# then you may purchase a commercial license.  For more information contact
# info@riverbankcomputing.com.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


import argparse
import importlib
import os
import sys

from ..version import DIP_RELEASE

from . import Robot


# The attributes used by the hook.
automation_commands = []
delay = 200
timeout = 5000


# Define a hook that will be called before the event loop is called for the
# first time.

def exec_hook():

    # Create a robot to record all the automation commands in the right
    # sequence.
    robot = Robot(delay=delay, timeout=timeout)

    for step in automation_commands:
        step.record(robot)

    robot.play(after=0)

    # Remove the hook so it is only ever called once.
    delattr(sys.modules['builtins'], '__pyQtPreEventLoopHook__')


def main():
    """ The setuptools entry point for the automation application. """

    # Parse the command line.
    global automation_commands, delay, timeout

    arg_parser = argparse.ArgumentParser(
		    description="Automate a script")

    arg_parser.add_argument('-V', '--version', action='version',
            version=DIP_RELEASE)

    arg_parser.add_argument('-c', '--commands', dest='commands',
            action='append', default=[], metavar='FILE',
            help="add the automation commands defined in FILE")
    arg_parser.add_argument('-d', '--delay', dest='delay', type=int,
            default=delay,
            help="the delay in milliseconds between automation commands "
                    "[default: {}]".format(delay))
    arg_parser.add_argument('-t', '--timeout', dest='timeout', type=int,
            default=timeout,
            help="the time in milliseconds to wait for a widget to become "
                    "visible [default: {}]".format(timeout))

    arg_parser.add_argument('script',
            help="the name of the script being automated")
    arg_parser.add_argument('arguments', nargs=argparse.REMAINDER,
            help="the arguments passed to the script")

    args = arg_parser.parse_args()

    delay = args.delay
    timeout = args.timeout

    # Import any automation commands.
    for commands_file in args.commands:
        name = os.path.basename(commands_file).split('.')[0]
        spec = importlib.util.spec_from_file_location(name, commands_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        automation_commands += getattr(module, 'automation_commands', [])

    if len(automation_commands) != 0:
        setattr(sys.modules['builtins'], '__pyQtPreEventLoopHook__', exec_hook)

    # Run the application.
    sys.argv = [args.script] + args.arguments

    with open(args.script) as f:
        exec(f.read(), globals())
