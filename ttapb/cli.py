#!/usr/bin/env python

import argparse
import os
import re
import sys
import urllib
import yaml
from objects import k8s_objects, openshift_objects

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
    provision = open('provision.yml', 'w')
    deprovision = open('deprovision.yml', 'w')
    deprovisionlist = []
    with open(inputfile, 'r') as input:
        try:
            data = yaml.load_all(input)
        except:
            pprint("Couldnt parse inputfile.Leaving...", 'red')
            os._exit(1)
        provision.write("---\n")
        deprovision.write("---\n")
        for d in data:
            if 'kind' not in d:
                continue
            if 'metadata' not in d:
                continue
            metadata = d['metadata']
            if 'name' not in metadata:
                continue
            name = d['metadata']['name']
            kind = d['kind']
            resource = kind[0].lower() + kind[1:]
            resource = re.sub('([A-Z])', "_\g<1>", resource).lower()
            kkinds = [o for o in reversed(k8s_objects) if o.endswith(resource)]
            okinds = [o for o in reversed(openshift_objects) if o.endswith(resource)]
            if kkinds:
                resource = kkinds[0]
            elif okinds:
                resource = okinds[0]
            else:
                continue
            # provision.write("- name: Creating %s %s\n" % (kind, name))
            # provision.write("  %s:\n    state: present\n" % (resource))
            if not os.path.exists("templates"):
                os.mkdir("templates")
            src = "templates/%s_%s.yml" % (kind, name)
            with open(src, 'w') as s:
                s.write(yaml.dump(d, default_flow_style=False, encoding='utf-8', allow_unicode=True))
            provision.write("- name: Creating %s %s\n  %s:\n    name: %s\n    namespace: \"{{ namespace}}\"\n    state: present\n    src: %s\n" % (kind, name, resource, name, src))
            # print(yaml.dump(d, default_flow_style=False, encoding='utf-8', allow_unicode=True))
            # print "   -name: execute %s\n    command: %s" % (command, command)
            deprovisionlist.append("- name: Deleting %s %s\n  %s:\n    name: %s\n    namespace: \"{{ namespace}}\"\n    state: absent\n" % (kind, name, resource, name))
    for p in reversed(deprovisionlist):
            deprovision.write(p)
    provision.close()
    deprovision.close()
    os._exit(0)


def cli():
    global config
    parser = argparse.ArgumentParser(description='Convert a template in apb')
    # parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('inputfile', help='Input template file')
    if len(sys.argv) == 1:
        parser.print_help()
        os._exit(0)
    args = parser.parse_args()
    process(args)

if __name__ == '__main__':
    cli()
