#!/usr/bin/env python

import argparse
import os
import sys
import urllib
import yaml

__version__ = '0.1'


def pprint(text, color=None):
    colors = {'blue': '34', 'red': '31', 'green': '32', 'yellow': '33', 'pink': '35', 'white': '37'}
    if color is not None and color in colors:
        color = colors[color]
        print('\033[1;%sm%s\033[0;0m' % (color, text))
    else:
        print(text)


def process(args):
    """Process """
    inputfile = args.inputfile
    if inputfile.startswith('http'):
        pprint("Downloading %s..." % inputfile, 'green')
        urllib.urlretrieve(inputfile, 'ttapb.yml')
        if 'NotFound' in open('ttapb.yml').read():
            pprint("Url %s not found.Leaving..." % inputfile, 'red')
        inputfile = 'ttapb.yml'
    elif not os.path.exists(inputfile):
        pprint("Inputfile %s not found.Leaving..." % sys.argv[0], 'red')
        os._exit(1)
    else:
        pprint("Processing %s..." % inputfile, 'green')
    with open(inputfile, 'r') as input:
        try:
            data = yaml.load_all(input)
        except:
            pprint("Couldnt parse inputfile.Leaving...", 'red')
            os._exit(1)
        for d in data:
            if 'kind' not in d:
                continue
            else:
                kind = d['kind']
                print(kind)
                # print(yaml.dump(d, default_flow_style=False, encoding='utf-8', allow_unicode=True))
    os._exit(0)


def cli():
    global config
    parser = argparse.ArgumentParser(description='Convert a template in apb')
    # parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('inputfile', help='Input template file')

    args = parser.parse_args()
    process(args)

if __name__ == '__main__':
    cli()
