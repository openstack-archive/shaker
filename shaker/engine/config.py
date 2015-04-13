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

from oslo_config import cfg
from shaker.engine import utils


COMMON_OPTS = [
    cfg.StrOpt('server-endpoint',
               default=utils.env('SHAKER_SERVER_ENDPOINT'),
               required=True,
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
]

SERVER_OPTS = [
    cfg.StrOpt('scenario',
               default=utils.env('SHAKER_SCENARIO'),
               required=True,
               help='Scenario file name, defaults to env[SHAKER_SCENARIO].'),

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
               default=(utils.env('SHAKER_REPORT_TEMPLATE') or
                        'shaker/resources/report_template.html'),
               help='Report template file name'),
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
               required=True,
               help='Agent unique id, defaults to env[SHAKER_AGENT_ID].'),
]

IMAGE_BUILDER_OPTS = [
    cfg.StrOpt('image-builder-template',
               default=(utils.env('SHAKER_IMAGE_BUILDER_TEMPLATE') or
                        'shaker/resources/image_builder_template.yaml'),
               help='Heat template for the image builder.'),
]


def list_opts():
    all_opts = (COMMON_OPTS + OPENSTACK_OPTS + SERVER_OPTS + REPORT_OPTS +
                INPUT_OPTS + AGENT_OPTS + IMAGE_BUILDER_OPTS)
    yield (None, copy.deepcopy(all_opts))
