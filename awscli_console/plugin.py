from awscli_console import common
import logging, webbrowser, sys

# This is not included in requirements.txt to avoid making the program heavier
# for those who will not use it as a plugin. But should work when called by the
# aws cli.
import awscli

def awscli_initialize(cli):
    cli.register('building-command-table.main', inject_commands)

def inject_commands(command_table, session, **kwargs):
    command_table['console'] = Console(session)

class Console(awscli.customizations.commands.BasicCommand):
    NAME = 'console'
    DESCRIPTION = 'Authenticate to AWS console'
    SYNOPSIS = 'aws console [--profile=name] [--browser=true|false]'

    ARG_TABLE = [
        {
            'name': 'browser',
            'cli_type_name': 'boolean',
            'default': True,
            'help_text': 'Open the console url in the browser'
        },
    ]

    UPDATE = False

    def _run_main(self, args, parsed_globals):
        logging.basicConfig(level=logging.INFO)
        for handler in logging.root.handlers:
            handler.addFilter(logging.Filter(__name__))
        self._call(args, parsed_globals)

        return 0

    def _call(self, options, parsed_globals):
        session = common.get_session(parsed_globals.profile)
        signin_token = common.get_signin_token(session)
        login_url = common.get_login_url(signin_token, session.region_name)
        logout_url = common.get_logout_url(login_url)

        print(logout_url)
        if options.browser:
            print("Opening URL in your browser...", file=sys.stderr)
            webbrowser.open(logout_url)
