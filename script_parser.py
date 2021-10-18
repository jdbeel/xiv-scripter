from utilities import dprint
from utilities import LogLevel

class Parser:
    def __init__(self, key_mapping: dict, default_delay=1, log_level=LogLevel.INFO):
        self.log_level = log_level
        self.key_mapping = key_mapping
        self.default_delay = default_delay

    def load_script(self, script_path):
        # List of tuple: command opcode to delay.
        script_list = []
        dprint(self.log_level, "Loading script...", default_priority=LogLevel.INFO)

        with open(script_path, 'r') as f:
            for line in f:
                match line.split():
                    case ["#", *text]:
                        # This is a comment. Log it to debug and move on.
                        dprint(self.log_level, f'  Comment: ' + ' '.join(text), default_priority=LogLevel.DEBUG)
                    case [command]:
                        # If a command doesn't have the delay specified, use the default delay.
                        dprint(self.log_level, f'  Added command: `{command}`', default_priority=LogLevel.DEBUG)

                        if command not in self.key_mapping:
                            raise ValueError('Command not in key mapping. Update config.yaml.')

                        script_list.append((command, self.default_delay))
                    case [command, delay]:
                        # If a command does have the delay specified, overwrite the default delay.
                        dprint(self.log_level, f'  Added command: `{command}` with delay: `{delay}`', default_priority=LogLevel.DEBUG)
                        if command not in self.key_mapping:
                            raise ValueError('Command not in key mapping. Update config.yaml.')

                        script_list.append((command, float(delay)))
                    case []:
                        pass
                    case _:
                        raise ValueError('Incorrect script formatting. Maybe you forgot a space after the `#` in a comment?')
        
        dprint(self.log_level, f'Script `{script_path}` loaded successfully!', default_priority=LogLevel.INFO)               

        return script_list

    def convert_script_to_virtual_keys(self, script_list):
        new_script_list = []

        for command, delay in script_list:
            new_script_list.append((self.key_mapping[command], delay))

        return new_script_list

    def parse_script(self, script_path: str):
        script_list = self.load_script(script_path)
        script_list = self.convert_script_to_virtual_keys(script_list)

        return script_list



