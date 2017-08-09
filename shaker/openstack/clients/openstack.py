# Copyright (c) 2015 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os_client_config
from oslo_log import log as logging
from oslo_utils import importutils

osprofiler_profiler = importutils.try_import("osprofiler.profiler")

LOG = logging.getLogger(__name__)


def init_profiling(os_profile):
    if osprofiler_profiler:  # lib is present
        if os_profile:
            osprofiler_profiler.init(os_profile)
            trace_id = osprofiler_profiler.get().get_base_id()
            LOG.info('Profiling is enabled, trace id: %s', trace_id)
    elif os_profile:  # param is set, but lib is not present
        LOG.warning('osprofiler library is required for profiling')


class OpenStackClient(object):
    def __init__(self, openstack_params):
        LOG.debug('Establishing connection to OpenStack')

        init_profiling(openstack_params.get('os_profile'))

        config = os_client_config.OpenStackConfig()
        cloud_config = config.get_one_cloud(**openstack_params)
        if openstack_params['os_insecure']:
            cloud_config.config['verify'] = False
            cloud_config.config['cacert'] = None
        self.keystone_session = cloud_config.get_session()
        self.nova = cloud_config.get_legacy_client('compute')
        self.neutron = cloud_config.get_legacy_client('network')
        self.glance = cloud_config.get_legacy_client('image')

        # heat client wants endpoint to be always set
        endpoint = cloud_config.get_session_endpoint('orchestration')
        self.heat = cloud_config.get_legacy_client('orchestration',
                                                   endpoint=endpoint)

        # Ping OpenStack
        self.keystone_session.get_token()

        LOG.info('Connection to OpenStack is initialized')
