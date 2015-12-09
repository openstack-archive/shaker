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

import copy
import re

from oslo_config import cfg
from oslo_config import types
from shaker.engine import utils


IMAGE_BUILDER_TEMPLATES = 'shaker/resources/image_builder_templates/'
REPORT_TEMPLATES = 'shaker/resources/report_templates/'
SCENARIOS = 'shaker/scenarios/'


class Endpoint(types.String):

    def __call__(self, value):
        value = str(value)
        if not re.match('\S+:\d+', value):
            raise ValueError('Wrong value of server_endpoint, '
                             'expected <host>:<port>, but got: %s' % value)
        return value

    def __repr__(self):
        return "Endpoint <host:port>"


COMMON_OPTS = [
    cfg.Opt('server-endpoint',
            default=utils.env('SHAKER_SERVER_ENDPOINT'),
            required=True,
            type=Endpoint(),
            help='Address for server connections (host:port), '
                 'defaults to env[SHAKER_SERVER_ENDPOINT].'),
    cfg.IntOpt('polling-interval',
               default=utils.env('SHAKER_POLLING_INTERVAL') or 10,
               help='How frequently the agent polls server, in seconds')
]

OPENSTACK_OPTS = [
    cfg.StrOpt('os-auth-url', metavar='<auth-url>',
               default=utils.env('OS_AUTH_URL'),
               sample_default='',
               help='Authentication URL, defaults to env[OS_AUTH_URL].'),
    cfg.StrOpt('os-tenant-name', metavar='<auth-tenant-name>',
               default=utils.env('OS_TENANT_NAME'),
               sample_default='',
               help='Authentication tenant name, defaults to '
                    'env[OS_TENANT_NAME].'),
    cfg.StrOpt('os-username', metavar='<auth-username>',
               default=utils.env('OS_USERNAME'),
               sample_default='',
               help='Authentication username, defaults to env[OS_USERNAME].'),
    cfg.StrOpt('os-password', metavar='<auth-password>',
               default=utils.env('OS_PASSWORD'),
               sample_default='',
               help='Authentication password, defaults to env[OS_PASSWORD].'),
    cfg.StrOpt('os-cacert', metavar='<auth-cacert>',
               default=utils.env('OS_CACERT'),
               sample_default='',
               help='Location of CA Certificate, defaults to env[OS_CACERT].'),
    cfg.BoolOpt('os-insecure',
                default=(utils.env('OS_INSECURE') or False),
                help='When using SSL in connections to the registry server, '
                     'do not require validation via a certifying authority, '
                     'defaults to env[OS_INSECURE].'),
    cfg.StrOpt('os-region-name', metavar='<auth-region-name>',
               default=utils.env('OS_REGION_NAME') or 'RegionOne',
               help='Authentication region name, defaults to '
                    'env[OS_REGION_NAME].'),

    cfg.StrOpt('external-net',
               default=utils.env('SHAKER_EXTERNAL_NET'),
               help='Name or ID of external network, defaults to '
                    'env[SHAKER_EXTERNAL_NET]. If no value provided then '
                    'Shaker picks any of available external networks.'),

    cfg.StrOpt('image-name',
               default=utils.env('SHAKER_IMAGE') or 'shaker-image',
               help='Name of image to use. The default is created by '
                    'shaker-image-builder.'),
    cfg.StrOpt('flavor-name',
               default=utils.env('SHAKER_FLAVOR') or 'shaker-flavor',
               help='Name of image flavor. The default is created by '
                    'shaker-image-builder.'),
    cfg.BoolOpt('cleanup-on-error',
                default=(utils.env('SHAKER_CLEANUP_ON_ERROR') or True),
                help='Cleans up the heat-stack upon any error occured during '
                     'scenario execution.'),

]

SERVER_OPTS = [
    cfg.StrOpt('scenario',
               default=utils.env('SHAKER_SCENARIO'),
               required=True,
               help=utils.make_help_options(
                   'Scenario to play. Can be a file name or one of aliases: '
                   '%s. Defaults to env[SHAKER_SCENARIO].', SCENARIOS,
                   type_filter=lambda x: x.endswith('.yaml'))),

    cfg.StrOpt('output',
               default=utils.env('SHAKER_OUTPUT'),
               help='File for output in JSON format, '
                    'defaults to env[SHAKER_OUTPUT].'),
    cfg.IntOpt('agent-loss-timeout',
               default=utils.env('SHAKER_AGENT_LOSS_TIMEOUT') or 60,
               help='Timeout to treat agent as lost in seconds'),
    cfg.IntOpt('agent-join-timeout',
               default=utils.env('SHAKER_AGENT_JOIN_TIMEOUT') or 600,
               help='How long to wait for agents to join in seconds (time '
                    'between stack deployment and start of scenario '
                    'execution).'),
    cfg.BoolOpt('no-report-on-error',
                default=(utils.env('SHAKER_NO_REPORT_ON_ERROR') or False),
                help='Do not generate report for failed scenarios'),
]

REPORT_OPTS = [
    cfg.StrOpt('report-template',
               default=(utils.env('SHAKER_REPORT_TEMPLATE') or 'interactive'),
               help=utils.make_help_options(
                   'Template for report. Can be a file name or one of '
                   'aliases: %s. Defaults to "interactive".',
                   REPORT_TEMPLATES)),
    cfg.StrOpt('report',
               default=utils.env('SHAKER_REPORT'),
               help='Report file name, defaults to env[SHAKER_REPORT]. '),
    cfg.StrOpt('subunit',
               default=utils.env('SHAKER_SUBUNIT'),
               help='Subunit stream file name, defaults to '
                    'env[SHAKER_SUBUNIT].'),
]

INPUT_OPTS = [
    cfg.StrOpt('input',
               default=utils.env('SHAKER_INPUT'),
               required=True,
               help='File to read test results from, '
                    'defaults to env[SHAKER_INPUT].'),
]


AGENT_OPTS = [
    cfg.StrOpt('agent-id',
               default=utils.env('SHAKER_AGENT_ID'),
               help='Agent unique id, defaults to MAC of primary interface.'),
]

IMAGE_BUILDER_OPTS = [
    cfg.StrOpt('image-builder-template',
               default=(utils.env('SHAKER_IMAGE_BUILDER_TEMPLATE') or
                        'ubuntu'),
               help=utils.make_help_options(
                   'Heat template containing receipt of building the image. '
                   'Can be a file name or one of aliases: %s. '
                   'Defaults to "ubuntu".', IMAGE_BUILDER_TEMPLATES)),
]


def list_opts():
    all_opts = (COMMON_OPTS + OPENSTACK_OPTS + SERVER_OPTS + REPORT_OPTS +
                INPUT_OPTS + AGENT_OPTS + IMAGE_BUILDER_OPTS)
    yield (None, copy.deepcopy(all_opts))
