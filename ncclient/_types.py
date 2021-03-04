# Copyright 2020 Ebben Aries
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import enum

class Datastore(enum.Enum):
    """RFC8342 NMDA Datastores"""
    STARTUP = 0
    CANDIDATE = 1
    RUNNING = 2
    INTENDED = 3
    OPERATIONAL = 4

class FilterType(enum.Enum):
    """RFC6241 NETCONF filtering"""
    SUBTREE = 0
    XPATH = 1

class WithDefaults(enum.Enum):
    """RFC6243 NETCONF with-defaults modes"""
    REPORT_ALL = 0
    REPORT_ALL_TAGGED = 1
    TRIM = 2
    EXPLICIT = 3

class Origin(enum.Enum):
    """RFC8342 NMDA Origin annotations"""
    INTENDED = 0
    DYNAMIC = 1
    SYSTEM = 2
    LEARNED = 3
    DEFAULT = 4
    UNKNOWN = 5
