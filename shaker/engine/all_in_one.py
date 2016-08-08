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

import tempfile

from oslo_config import cfg
from oslo_log import log as logging

from shaker.engine import config
from shaker.engine import image_builder
from shaker.engine import server
from shaker.engine import utils

LOG = logging.getLogger(__name__)


def _configure_log_file(log_file):
    cfg.CONF.set_override('log_file', log_file)
    logging.setup(cfg.CONF, 'shaker')
    cfg.CONF.log_opt_values(LOG, logging.DEBUG)


def main():
    utils.init_config_and_logging(
        config.COMMON_OPTS + config.OPENSTACK_OPTS + config.SERVER_OPTS +
        config.REPORT_OPTS + config.IMAGE_BUILDER_OPTS + config.CLEANUP_OPTS
    )

    artifacts_dir = cfg.CONF.artifacts_dir
    if not artifacts_dir:
        artifacts_dir = tempfile.mkdtemp(prefix='shaker')
        cfg.CONF.set_override('artifacts_dir', artifacts_dir)

    # image-builder
    _configure_log_file(utils.join_folder_prefix_ext(
        artifacts_dir, 'image_builder', 'log'))
    LOG.info('Building the image')
    image_builder.build_image()

    # core
    _configure_log_file(utils.join_folder_prefix_ext(
        artifacts_dir, 'execution', 'log'))

    if len(cfg.CONF.scenario) > 1:
        cfg.CONF.set_override(
            'output', utils.join_folder_prefix_ext(
                artifacts_dir, 'aggregated', 'json'))
        cfg.CONF.set_override(
            'report', utils.join_folder_prefix_ext(
                artifacts_dir, 'aggregated', 'html'))
        cfg.CONF.set_override(
            'subunit', utils.join_folder_prefix_ext(
                artifacts_dir, 'aggregated', 'subunit'))
        cfg.CONF.set_override(
            'book', utils.join_folder_prefix_ext(artifacts_dir, 'aggregated'))

    LOG.info('Executing scenario(s)')
    server.act()

    # cleanup
    _configure_log_file(utils.join_folder_prefix_ext(
        artifacts_dir, 'cleanup', 'log'))
    LOG.info('Cleaning up')
    image_builder.cleanup()

if __name__ == "__main__":
    main()
