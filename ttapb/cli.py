#!/usr/bin/env python

import argparse
import os
import re
import urllib
import yaml
from ttapb.objects import k8s_objects, openshift_objects

__version__ = '0.3'


def pprint(text, color=None):
    colors = {'blue': '34', 'red': '31', 'green': '32', 'yellow': '33', 'pink': '35', 'white': '37'}
    if color is not None and color in colors:
        color = colors[color]
        print('\033[1;%sm%s\033[0;0m' % (color, text))
    else:
        print(text)


def process(args):
    """Process """
    inputfile = args.inputfile[0]
    render = args.render
    if inputfile.startswith('http'):
        pprint("Downloading %s..." % inputfile, 'green')
        urllib.urlretrieve(inputfile, 'ttapb.yml')
        if 'NotFound' in open('ttapb.yml').read():
            pprint("Url %s not found.Leaving..." % inputfile, 'red')
        inputfile = 'ttapb.yml'
    elif not os.path.exists(inputfile):
        pprint("Inputfile %s not found.Leaving..." % inputfile, 'red')
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
            if not os.path.exists("templates"):
                os.mkdir("templates")
            if render:
                src = "%s_%s.yml.j2" % (kind, name)
                dest = "/tmp/%s_%s.yml" % (kind, name)
                k8src = dest
            else:
                src = "%s_%s.yml" % (kind, name)
                dest = "%s_%s.yml" % (kind, name)
                k8src = "\"{{ role_path }}/files/%s_%s.yml\"" % (kind, name)
            with open("templates/%s" % src, 'w') as s:
                yaml.dump(d, stream=s, default_flow_style=False, encoding='utf-8', allow_unicode=True, explicit_start=True)
            if render:
                provision.write("- name: Rendering %s %s\n  template: \n    src: %s\n    dest: %s\n\n" % (kind, name, src, dest))
            if 'cluster' in resource:
                namespace = ''
            else:
                namespace = '    namespace: \"{{ namespace}}\"\n'
            provision.write("- name: Creating %s %s\n  %s:\n    name: %s\n%s    state: present\n    src: %s\n\n" % (kind, name, resource, name, namespace, k8src))
            deprovisionlist.append("- name: Deleting %s %s\n  %s:\n    name: %s\n%s    state: absent\n\n" % (kind, name, resource, name, namespace))
    for p in reversed(deprovisionlist):
            deprovision.write(p)
    provision.close()
    deprovision.close()
    os._exit(0)


def cli():
    parser = argparse.ArgumentParser(description='Convert a template in apb')
    parser.add_argument('-r', '--render', action='store_true', help='Create intermediate jinja files')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('inputfile', help='Input template file', nargs=1)
    args = parser.parse_args()
    process(args)

if __name__ == '__main__':
    cli()
