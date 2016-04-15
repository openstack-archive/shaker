# Copyright (c) 2016 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import re
import os
import sys
import textwrap

import jinja2
import yaml


def make(src, dest):
    scenarios = []
    templates = []

    jinja_env = jinja2.Environment()

    for dirpath, dirnames, filenames in os.walk(src):
        for filename in sorted(filenames):
            if not (filename.endswith('.yaml') or
                    filename.endswith('.hot')):
                continue

            fullpath = os.path.join(dirpath, filename)

            with open(fullpath) as f:
                try:
                    raw = f.read()
                    compiled_template = jinja_env.from_string(raw)
                    rendered_template = compiled_template.render(
                        dict(agents={}))
                    content = yaml.safe_load(rendered_template)

                    s_id = '/'.join(fullpath.split('/')[2:]).split('.')[0]

                    info = dict(title=content.get('title') or s_id,
                                description=content['description'],
                                path=fullpath,
                                scenario_id=s_id)
                    if filename.endswith('.yaml'):
                        scenarios.append(info)
                    else:
                        templates.append(info)
                except Exception as e:
                    print('Failed to read file %s: %s' % (fullpath, e))

    scenarios.sort(key=lambda x: x['scenario_id'])
    templates.sort(key=lambda x: x['scenario_id'])

    with open(dest, 'w') as out:
        print('.. _catalog:\n', file=out)
        print('Scenario Catalog', file=out)
        print('================', file=out)
        print('', file=out)

        print('Scenarios', file=out)
        print('---------', file=out)
        print('', file=out)

        for info in scenarios:
            print_info(out, info, prefix='scenario')
            print('To use this scenario specify parameter ``--scenario %s``.\n'
                  'Scenario source is available at: '
                  'https://github.com/openstack/shaker/blob/master/%s' %
                  (info['scenario_id'], info['path']), file=out)
            print('', file=out)

        print('Heat Templates', file=out)
        print('--------------', file=out)
        print('', file=out)

        for info in templates:
            print_info(out, info, prefix='template')
            print('Template source is available at: '
                  'https://github.com/openstack/shaker/blob/master/%s' %
                  info['path'], file=out)
            print('', file=out)


def print_info(out, info, prefix):
    block_id = re.sub(r'[^\w\d]+', '_', info['title']).lower()
    print('.. _%s_%s:\n' % (prefix, block_id), file=out)
    print(info['title'], file=out)
    print('^' * len(info['title']), file=out)
    print('\n'.join(textwrap.wrap(info['description'], width=79)), file=out)
    print('', file=out)


if len(sys.argv) < 2:
    print('Usage: build_scenario_catalog <dest file>')
    sys.exit(1)


print('Generating scenario catalog')
make(src='shaker/scenarios/', dest=sys.argv[1])
