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

import functools
import json
import sys

import jinja2
from oslo_config import cfg
from oslo_log import log as logging
import yaml

from shaker.engine import aggregators
from shaker.engine import config
from shaker.engine import utils


LOG = logging.getLogger(__name__)


def calculate_stats(data):
    for test_result in data['result']:
        aggregator = aggregators.get_aggregator(test_result['definition'])

        for iteration_result in test_result['results_per_iteration']:
            for agent_result in iteration_result['results_per_agent']:
                aggregator.agent_summary(agent_result)

            aggregator.iteration_summary(iteration_result)

        aggregator.test_summary(test_result)


def generate_report(report_template, report_filename, data):
    LOG.debug('Generating report, template: %s, output: %s',
              report_template, report_filename or 'stdout')

    calculate_stats(data)

    # add more filters to jinja
    jinja_env = jinja2.Environment()
    jinja_env.filters['json'] = json.dumps
    jinja_env.filters['yaml'] = functools.partial(yaml.safe_dump, indent=2,
                                                  default_flow_style=False)

    template = utils.read_file(report_template)
    compiled_template = jinja_env.from_string(template)
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

    LOG.debug('Reading JSON data from: %s', cfg.CONF.input)
    report_data = json.loads(utils.read_file(cfg.CONF.input))

    generate_report(cfg.CONF.report_template, cfg.CONF.report, report_data)


if __name__ == "__main__":
    main()
