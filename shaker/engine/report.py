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
import json

import sys

import jinja2
from oslo_config import cfg
from oslo_log import log as logging

from shaker.engine import config
from shaker.engine import utils


LOG = logging.getLogger(__name__)


def generate_report(report_template, report_filename, data):
    template = utils.read_file(report_template)
    compiled_template = jinja2.Template(template)

    rendered_template = compiled_template.render(dict(report=data))

    if report_filename:
        fd = open(report_filename, 'w')
    else:
        fd = sys.stdout

    fd.write(rendered_template)
    fd.close()
    LOG.info('Report generated')


def main():
    utils.init_config_and_logging(config.REPORT_OPTS + config.INPUT_OPTS)

    if cfg.CONF.input:
        LOG.debug('Reading JSON data from: %s', cfg.CONF.input)
        report_data = json.loads(utils.read_file(cfg.CONF.input))

        generate_report(cfg.CONF.report_template, cfg.CONF.report,
                        report_data)


if __name__ == "__main__":
    main()
