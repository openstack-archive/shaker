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
               required=True,
               help='Address for server connections (host:port)'),
]

OPENSTACK_OPTS = [
    cfg.StrOpt('os-auth-url', metavar='<auth-url>',
               default=utils.env('OS_AUTH_URL'),
               help='Authentication URL, defaults to env[OS_AUTH_URL].'),
    cfg.StrOpt('os-tenant-name', metavar='<auth-tenant-name>',
               default=utils.env('OS_TENANT_NAME'),
               help='Authentication tenant name, defaults to '
                    'env[OS_TENANT_NAME].'),
    cfg.StrOpt('os-username', metavar='<auth-username>',
               default=utils.env('OS_USERNAME'),
               help='Authentication username, defaults to env[OS_USERNAME].'),
    cfg.StrOpt('os-password', metavar='<auth-password>',
               default=utils.env('OS_PASSWORD'),
               help='Authentication password, defaults to env[OS_PASSWORD].'),
    cfg.StrOpt('os-region-name', metavar='<auth-region-name>',
               default=utils.env('OS_REGION_NAME') or 'RegionOne',
               help='Authentication region name, defaults to '
                    'env[OS_REGION_NAME].'),

    cfg.StrOpt('external-net',
               help='Name or ID of external network. If not set the network '
                    'is chosen randomly.'),

    cfg.StrOpt('image-name',
               default='shaker-image',
               help='Name of image to use. The default is created by '
                    'shaker-image-builder'),
    cfg.StrOpt('flavor-name',
               default='shaker-flavor',
               help='Name of image flavor. The default is created by '
                    'shaker-image-builder'),
]

SERVER_OPTS = [
    cfg.StrOpt('scenario',
               required=True,
               help='Scenario file name'),

    cfg.StrOpt('report-template',
               default='shaker/engine/report.template',
               help='Report template file name (Jinja format)'),
    cfg.StrOpt('report',
               help='Report file name. If not specified print to stdout'),
]

AGENT_OPTS = [
    cfg.StrOpt('agent-id',
               required=True,
               help='Agent unique id'),
]


def list_opts():
    yield (None, copy.deepcopy(COMMON_OPTS))
    yield (None, copy.deepcopy(OPENSTACK_OPTS))
    yield (None, copy.deepcopy(SERVER_OPTS))
    yield (None, copy.deepcopy(AGENT_OPTS))
