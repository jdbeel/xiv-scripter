import argparse
import re
import time
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

MEAT_AND_MEAD = {
    0: 30,
    1: 40,
    2: 45
}

class XIVScripter:
    def __init__(
        self,
        verbose=LogLevel.INFO,
        config='config.yaml',
        script='scripts/coffee_biscuits.script',
        eat_food=None
    ):
        self.verbose = verbose
        dprint(self.verbose, f"Reading from configuration file: [{config}]", default_priority=LogLevel.DEBUG)
        with open(config) as f:
            config = yaml.load(f, Loader=Loader)

        # Load variables from config
        if eat_food is None:
            self._should_eat_food = config.get('eat_food', False)
        else:
            self._should_eat_food = eat_food
        self._meat_and_mead = config.get('meat_and_mead', 0)
        self._per_run_delay = config.get('per_run_delay', 5.0)
        self._post_food_delay = config.get('post_food_delay', 5.0)
        if self._should_eat_food:
            dprint(
                self.verbose,
                f'Will eat food before running the script and every {MEAT_AND_MEAD[self._meat_and_mead]} minutes after.',
                default_priority=LogLevel.INFO
            )

        # Load in key mapping and parse script.
        self.key_mapping = config.get('key_mapping', None)
        if not self.key_mapping:
            raise ValueError("Key mapping must be defined in config.yaml.")
        parser = Parser(key_mapping=self.key_mapping, log_level=verbose)
        self.script_list = parser.parse_script(script)

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
            dprint(self.verbose, f'Executing command: `{key}`', default_priority=LogLevel.DEBUG)
            self.send_key(key)
            sleep(delay)

    def _eat_food(self):
        """
        Eats food and returns the time when the food will expire.
        """
        eat_food_key = self.key_mapping.get('eat_food', None)
        if eat_food_key is None:
            raise ValueError('eat_food_key must be specified if eat_food is set to True.')
        self.send_key(eat_food_key)
        sleep(self._post_food_delay)
        food_t1 = time.time() + MEAT_AND_MEAD[self._meat_and_mead] * 60

        return food_t1

    def run(self, n_reps):
        """
        Runs the script n_reps times.
        """
        dprint(self.verbose, 'Launching runs in 3...')
        sleep(1)
        dprint(self.verbose, '2...')
        sleep(1)
        dprint(self.verbose, '1...')
        sleep(1)

        # Eat food and set up the times to continue eating food.
        if self._should_eat_food:
            dprint(self.verbose, 'Eating food...')
            food_t1 = self._eat_food()

        for i in range(n_reps):
            if self._should_eat_food:
                if time.time() >= food_t1:
                    dprint(self.verbose, 'Eating food...')
                    food_t1 = self._eat_food()

            dprint(self.verbose, f'Beginning run no. {i + 1}', default_priority=LogLevel.INFO)
            self._run_script()
            sleep(self._per_run_delay)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs scripts to be sent to Final Fantasy XIV.')
    parser.add_argument('--n_reps', metavar='--n_reps', type=int, default=1, help='The number of times to repeat the script.')
    parser.add_argument('--config', metavar='--config', type=str, default='config.yaml', help='The relative path to the config.yaml file.')
    parser.add_argument('--script', metavar='--script', type=str, default='scripts/coffee_biscuits_turnin.script', help='The relative path to the script file to run.')
    parser.add_argument('--eat_food', action='store_true', default=None)

    arguments = vars(parser.parse_args())
    n_reps = arguments['n_reps']
    del arguments['n_reps']

    scripter = XIVScripter(**arguments)
    scripter.run(n_reps)