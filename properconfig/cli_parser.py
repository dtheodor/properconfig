# -*- coding: utf-8 -*-
"""
author: dtheodor
created: 2015-Aug-03


"""
import os
import sys
from argparse import ArgumentParser, _get_action_name, _, ArgumentError, \
    SUPPRESS
from ConfigParser import ConfigParser as FileConfigParser, DEFAULTSECT, \
    Error as ConfigParserError
from collections import namedtuple

ParseAttempt = namedtuple("ParseAttempt", ["success", "value", "option_name"])
failed_attempt = ParseAttempt(success=False,
                              value=None,
                              option_name=None)

def _pick_action_option(action):
    for string in action.option_strings:
        if "--" in string:
            return string
    return action.option_strings[0]

class ConfigParser(ArgumentParser):
    """Parses arguments from environment variables and files as well as from
    the command line.
    """

    def __init__(self, environ_prefix=None, fp=None, *args, **kwargs):
        super(ConfigParser, self).__init__(*args, **kwargs)
        self.environ_parser = EnvironParser(prefix=environ_prefix)
        self.from_env = True
        self.from_file = True
        self.file_parser = FileParser(fp)

    def parse_from_other_sources(self, action):
        """Try to read the action's value from all non-CLI configuration
        sources.
        """
        parsed = self.environ_parser.parse(action)
        if parsed.success:
            return parsed
        parsed = self.file_parser.parse(action)
        if parsed.success:
            return parsed
        return failed_attempt

    def parse_from_env(self, action):
        if self.from_env:
            return self.environ_parser.parse(action)
        return failed_attempt

    def parse_from_file(self, action):
        if self.from_file:
            parsed = self.environ_parser.parse(action)
            if parsed.success:
                return parsed
            return failed_attempt


    def error(self, message):
        print message
        raise Exception(message), None, sys.exc_info()[2]

    def parse_args(self, args=None, namespace=None):
        super(ConfigParser, self).parse_args(args=args, namespace=namespace)
        pass

    def _get_value(self, action, arg_string):
        #return 5
        print "omfg"
        return super(ConfigParser, self)._get_value(action, arg_string)

    def _parse_known_args(self, arg_strings, namespace):
        # replace arg strings that are file references
        if self.fromfile_prefix_chars is not None:
            arg_strings = self._read_args_from_files(arg_strings)

        # map all mutually exclusive arguments to the other arguments
        # they can't occur with
        action_conflicts = {}
        for mutex_group in self._mutually_exclusive_groups:
            group_actions = mutex_group._group_actions
            for i, mutex_action in enumerate(mutex_group._group_actions):
                conflicts = action_conflicts.setdefault(mutex_action, [])
                conflicts.extend(group_actions[:i])
                conflicts.extend(group_actions[i + 1:])

        # find all option indices, and determine the arg_string_pattern
        # which has an 'O' if there is an option at an index,
        # an 'A' if there is an argument, or a '-' if there is a '--'
        option_string_indices = {}
        arg_string_pattern_parts = []
        arg_strings_iter = iter(arg_strings)
        for i, arg_string in enumerate(arg_strings_iter):

            # all args after -- are non-options
            if arg_string == '--':
                arg_string_pattern_parts.append('-')
                for arg_string in arg_strings_iter:
                    arg_string_pattern_parts.append('A')

            # otherwise, add the arg to the arg strings
            # and note the index if it was an option
            else:
                option_tuple = self._parse_optional(arg_string)
                if option_tuple is None:
                    pattern = 'A'
                else:
                    option_string_indices[i] = option_tuple
                    pattern = 'O'
                arg_string_pattern_parts.append(pattern)

        # join the pieces together to form the pattern
        arg_strings_pattern = ''.join(arg_string_pattern_parts)

        # converts arg strings to the appropriate and then takes the action
        seen_actions = set()
        seen_non_default_actions = set()

        def take_action(action, argument_strings, option_string=None):
            seen_actions.add(action)
            argument_values = self._get_values(action, argument_strings)

            # error if this argument is not allowed with other previously
            # seen arguments, assuming that actions that use the default
            # value don't really count as "present"
            if argument_values is not action.default:
                seen_non_default_actions.add(action)
                for conflict_action in action_conflicts.get(action, []):
                    if conflict_action in seen_non_default_actions:
                        msg = _('not allowed with argument %s')
                        action_name = _get_action_name(conflict_action)
                        raise ArgumentError(action, msg % action_name)

            # take the action if we didn't receive a SUPPRESS value
            # (e.g. from a default)
            if argument_values is not SUPPRESS:
                action(self, namespace, argument_values, option_string)

        # function to convert arg_strings into an optional action
        def consume_optional(start_index):

            # get the optional identified at this index
            option_tuple = option_string_indices[start_index]
            action, option_string, explicit_arg = option_tuple

            # identify additional optionals in the same arg string
            # (e.g. -xyz is the same as -x -y -z if no args are required)
            match_argument = self._match_argument
            action_tuples = []
            while True:

                # if we found no optional action, skip it
                if action is None:
                    extras.append(arg_strings[start_index])
                    return start_index + 1

                # if there is an explicit argument, try to match the
                # optional's string arguments to only this
                if explicit_arg is not None:
                    arg_count = match_argument(action, 'A')

                    # if the action is a single-dash option and takes no
                    # arguments, try to parse more single-dash options out
                    # of the tail of the option string
                    chars = self.prefix_chars
                    if arg_count == 0 and option_string[1] not in chars:
                        action_tuples.append((action, [], option_string))
                        char = option_string[0]
                        option_string = char + explicit_arg[0]
                        new_explicit_arg = explicit_arg[1:] or None
                        optionals_map = self._option_string_actions
                        if option_string in optionals_map:
                            action = optionals_map[option_string]
                            explicit_arg = new_explicit_arg
                        else:
                            msg = _('ignored explicit argument %r')
                            raise ArgumentError(action, msg % explicit_arg)

                    # if the action expect exactly one argument, we've
                    # successfully matched the option; exit the loop
                    elif arg_count == 1:
                        stop = start_index + 1
                        args = [explicit_arg]
                        action_tuples.append((action, args, option_string))
                        break

                    # error if a double-dash option did not use the
                    # explicit argument
                    else:
                        msg = _('ignored explicit argument %r')
                        raise ArgumentError(action, msg % explicit_arg)

                # if there is no explicit argument, try to match the
                # optional's string arguments with the following strings
                # if successful, exit the loop
                else:
                    start = start_index + 1
                    selected_patterns = arg_strings_pattern[start:]
                    arg_count = match_argument(action, selected_patterns)
                    stop = start + arg_count
                    args = arg_strings[start:stop]
                    action_tuples.append((action, args, option_string))
                    break

            # add the Optional to the list and return the index at which
            # the Optional's string args stopped
            assert action_tuples
            for action, args, option_string in action_tuples:
                take_action(action, args, option_string)
            return stop

        # the list of Positionals left to be parsed; this is modified
        # by consume_positionals()
        positionals = self._get_positional_actions()

        # function to convert arg_strings into positional actions
        def consume_positionals(start_index):
            # match as many Positionals as possible
            match_partial = self._match_arguments_partial
            selected_pattern = arg_strings_pattern[start_index:]
            arg_counts = match_partial(positionals, selected_pattern)

            # slice off the appropriate arg strings for each Positional
            # and add the Positional and its args to the list
            for action, arg_count in zip(positionals, arg_counts):
                args = arg_strings[start_index: start_index + arg_count]
                start_index += arg_count
                take_action(action, args)

            # slice off the Positionals that we just parsed and return the
            # index at which the Positionals' string args stopped
            positionals[:] = positionals[len(arg_counts):]
            return start_index

        # consume Positionals and Optionals alternately, until we have
        # passed the last option string
        extras = []
        start_index = 0
        if option_string_indices:
            max_option_string_index = max(option_string_indices)
        else:
            max_option_string_index = -1
        while start_index <= max_option_string_index:

            # consume any Positionals preceding the next option
            next_option_string_index = min([
                                               index
                                               for index in option_string_indices
                                               if index >= start_index])
            if start_index != next_option_string_index:
                positionals_end_index = consume_positionals(start_index)

                # only try to parse the next optional if we didn't consume
                # the option string during the positionals parsing
                if positionals_end_index > start_index:
                    start_index = positionals_end_index
                    continue
                else:
                    start_index = positionals_end_index

            # if we consumed all the positionals we could and we're not
            # at the index of an option string, there were extra arguments
            if start_index not in option_string_indices:
                strings = arg_strings[start_index:next_option_string_index]
                extras.extend(strings)
                start_index = next_option_string_index

            # consume the next optional and any arguments for it
            start_index = consume_optional(start_index)

        # consume any positionals following the last Optional
        stop_index = consume_positionals(start_index)

        # if we didn't consume all the argument strings, there were extras
        extras.extend(arg_strings[stop_index:])

        # if we didn't use all the Positional objects, there were too few
        # arg strings supplied.
        if positionals:
            self.error(_('too few arguments'))

        # make sure all required actions were present, and convert defaults.
        for action in self._actions:
            if action not in seen_actions:
                # read from other sources
                parsed = self.parse_from_other_sources(action)
                if parsed.success:
                    take_action(action, parsed.value, parsed.option_name)
                elif action.required:
                    name = _get_action_name(action)
                    self.error(_('argument %s is required') % name)
                else:
                    # Convert action default now instead of doing it before
                    # parsing arguments to avoid calling convert functions
                    # twice (which may fail) if the argument was given, but
                    # only if it was defined already in the namespace
                    if (action.default is not None and
                            isinstance(action.default, basestring) and
                            hasattr(namespace, action.dest) and
                                action.default is getattr(namespace, action.dest)):
                        setattr(namespace, action.dest,
                                self._get_value(action, action.default))

        # make sure all required groups had one option present
        for group in self._mutually_exclusive_groups:
            if group.required:
                for action in group._group_actions:
                    if action in seen_non_default_actions:
                        break

                # if no actions were used, report the error
                else:
                    names = [_get_action_name(action)
                             for action in group._group_actions
                             if action.help is not SUPPRESS]
                    msg = _('one of the arguments %s is required')
                    self.error(msg % ' '.join(names))

        # return the updated namespace and the extra arguments
        return namespace, extras


class EnvironParser(object):
    """Parse values from environment variables."""
    def __init__(self, prefix):
        self.prefix = prefix

    def cli_option_to_env_var(self, option):
        variable = option.lstrip("-").replace('-', '_').upper()
        return "{0}_{1}".format(self.prefix, variable)

    def parse(self, action):
        for string in action.option_strings:
            variable = self.cli_option_to_env_var(string)
            try:
                return ParseAttempt(
                    success=True,
                    value=[os.environ[variable]],
                    option_name=string)
            except KeyError:
                pass
        return failed_attempt


class FileParser(object):
    """Parses values from an .ini file.

    Uses the ConfigParser module.
    """
    def __init__(self, fp, filename=None):
        self.filename = filename
        config = self.config = FileConfigParser()
        config.readfp(fp)

    @classmethod
    def from_filename(cls, filename):
        with open(filename) as f:
            return FileParser(f, filename)

    def cli_option_to_file_option(self, option):
        return option.lstrip("-")

    def parse(self, action):
        for string in action.option_strings:
            option = self.cli_option_to_file_option(option)
            try:
                value = self.config.get(DEFAULTSECT, option)
                return ParseAttempt(success=True,
                                    value=[value],
                                    option_name=string)
            except ConfigParserError:
                pass
        return failed_attempt




if __name__ == "__main__":
    with open("config.conf") as f:
        parser = ConfigParser(environ_prefix="LOL",
                              fp=f,
                              description="test")
    parser.add_argument('-v', '--verbose', type=int, required=True, default=2)

    in_args = "".split()

    args = parser.parse_known_args(in_args)
    print args
