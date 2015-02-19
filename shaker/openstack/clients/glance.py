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

from glanceclient import client as glance_client_pkg


GLANCE_VERSION = '1'


def create_client(keystone_client, os_region_name):
    image_api_url = keystone_client.service_catalog.url_for(
        service_type='image', region_name=os_region_name)
    return glance_client_pkg.Client(GLANCE_VERSION,
                                    endpoint=image_api_url,
                                    auth_token=keystone_client.auth_token)


def is_image_exists(glance_client, image_name):
    return False  # glance_client.images.get(image_name)
