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

from pykwalify import core as pykwalify_core
from pykwalify import errors as pykwalify_errors

def validate_yaml(data, schema):
    c = pykwalify_core.Core(source_data=data, schema_data=schema)
    try:
        c.validate(raise_exception=True)
    except pykwalify_errors.SchemaError as e:
        raise Exception('File does not conform to schema: %s' % e)
