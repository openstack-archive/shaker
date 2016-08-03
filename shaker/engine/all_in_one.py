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

import errno
import os

from oslo_config import cfg
from oslo_log import log as logging

from shaker.engine import config
from shaker.engine import image_builder
from shaker.engine import server
from shaker.engine import utils

LOG = logging.getLogger(__name__)


def _make_filename(folder, prefix, ext=None):
    tmp_report = prefix
    if ext:
        tmp_report = '%s.%s' % (tmp_report, ext)
    return os.path.join(folder, tmp_report)


def _mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def main():
    utils.init_config_and_logging(
        config.COMMON_OPTS + config.OPENSTACK_OPTS + config.SERVER_OPTS +
        config.REPORT_OPTS + config.IMAGE_BUILDER_OPTS + config.CLEANUP_OPTS +
        config.ALL_IN_ONE_OPTS
    )

    artifacts_dir = cfg.CONF.artifacts_dir
    if artifacts_dir:
        prefix = utils.strict(cfg.CONF.scenario)
        _mkdir_p(artifacts_dir)
        cfg.CONF.set_override('output',
                              _make_filename(artifacts_dir, prefix, 'json'))
        cfg.CONF.set_override('report',
                              _make_filename(artifacts_dir, prefix, 'html'))
        cfg.CONF.set_override('subunit',
                              _make_filename(artifacts_dir, prefix, 'subunit'))
        cfg.CONF.set_override('book', _make_filename(artifacts_dir, prefix))

    LOG.info('Building the image')
    image_builder.build_image()
    LOG.info('Starting scenario execution')
    server.act()
    LOG.info('Cleaning up')
    image_builder.cleanup()
    LOG.info('Done')

if __name__ == "__main__":
    main()
