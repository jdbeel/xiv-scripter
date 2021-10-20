# XIV Scripter

This is a tool for scripting out series of actions in FFXIV. It allows for custom actions to be defined in `config.yaml` as well as custom scripts to be written and run.

## Requirements

- `python>=3.10`
- Microsoft Visual C++ 14 (this one is a massive pain to install, but there are plenty of resources online.)
- `requirements.txt`

## Usage

For instance, if I wanted to craft 5 sets of coffee biscuits:

`python xiv_scripter.py --n_reps 5 --script script/coffee_biscuits_craft.script`

For a more complete guide, see:

`python xiv_scripter.py --help`

Each script has a unique set up which must be done manually. Check the comments at the top of each script for a description.

## Adding Scripts

If you write your own script which is useful, go ahead and create a pull request to add it to the repo.
