import argparse
import re
from time import sleep

import psutil
import pywinauto
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from script_parser import Parser
from utilities import dprint
from utilities import LogLevel

PER_RUN_DELAY = 3.0

class XIVScripter:
    def __init__(
        self,
        verbose=LogLevel.INFO,
        config='config.yaml',
        script='scripts/coffee_biscuits.script'
    ):
        dprint(verbose, f"Reading from configuration file: [{config}]", default_priority=LogLevel.DEBUG)
        with open(config) as f:
            config = yaml.load(f, Loader=Loader)

        parser = Parser(key_mapping=config['key_mapping'], log_level=verbose)
        self.script_list = parser.parse_script(script)

        self.verbose = verbose
        match config:
            case {'target_process': target_process, 'window_title': window_title}:
                self._window_title = window_title
                self._target_process = target_process
            case _:
                raise ValueError("target_process and window_title are not specified in config.yaml.")

        self.connect_to_game()

    def connect_to_game(self):
        pid = None
        for p in psutil.process_iter():
            try:
                if p.name() == self._target_process:
                    query = re.search("pid=(.+?), name=", str(p))
                    pid = int(query.group(1))
            except psutil.AccessDenied:
                pass

        if pid is None:
            raise ValueError("Unable to find FFXIV process.")

        app = pywinauto.application.Application().connect(process=pid)

        self._app = app

    def send_key(self, key):
        """
        Sends a keystroke to the window.
        
        Parameters
        ----------
        key: str
            The keystroke to send to the window.
        """
        self._app.window(title=self._window_title).send_keystrokes(key)

    def _run_script(self):
        """
        Runs each command in the script and waits for the specified delay after each command.
        """
        for key, delay in self.script_list:
            dprint(self.verbose, f'Executing command: `{key}`')
            self.send_key(key)
            sleep(delay)

    def run(self, n_reps):
        """
        Runs the script n_reps times.
        """
        for i in range(n_reps):
            dprint(self.verbose, f'Beginning run no. {i + 1}', default_priority=LogLevel.INFO)
            self._run_script()
            sleep(PER_RUN_DELAY)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs scripts to be sent to Final Fantasy XIV.')
    parser.add_argument('--n_reps', metavar='--n_reps', type=int, default=1, help='The number of times to repeat the script.')
    parser.add_argument('--config', metavar='--config', type=str, default='config.yaml', help='The relative path to the config.yaml file.')
    parser.add_argument('--script', metavar='--script', type=str, default='scripts/coffee_biscuits_turnin.script', help='The relative path to the script file to run.')

    arguments = vars(parser.parse_args())
    n_reps = arguments['n_reps']
    del arguments['n_reps']

    scripter = XIVScripter(**arguments)
    scripter.run(n_reps)