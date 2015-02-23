# Copyright (c) 2015 Mirantis Inc.
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

import sys
import uuid

import jinja2

from shaker.engine import utils


def _add_uuids(d):
    for k, v in d.items():
        if isinstance(v, dict):
            _add_uuids(v)
        elif isinstance(v, list):
            for i in v:
                if isinstance(i, dict):
                    _add_uuids(i)
        else:
            d['uuid'] = uuid.uuid4()


def generate_report(report_template, report_filename, data):
    template = utils.read_file(report_template)
    compiled_template = jinja2.Template(template)

    _add_uuids(data)

    rendered_template = compiled_template.render(dict(report=data))

    if report_filename:
        fd = open(report_filename, 'w')
    else:
        fd = sys.stdout

    fd.write(rendered_template)
    fd.close()
