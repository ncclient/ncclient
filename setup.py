# Copyright 2009 Shikhar Bhushan
# Copyright 201[2-5] Leonidas Poulopoulos (@leopoul)
# Copyright 2013 Ebben Aries
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

from setuptools import setup, find_packages
from distutils.command.install import install as _install

import sys
import platform
import codecs
import versioneer

__author__ = "Shikhar Bhushan, Leonidas Poulopoulos, Ebben Aries, Einar Nilsen-Nygaard"
__author_email__ = "shikhar@schmizz.net, lpoulopoulos@verisign.com, exa@dscp.org, einarnn@gmail.com"
__licence__ = "Apache 2.0"

if sys.version_info.major == 2 and sys.version_info.minor < 7:
    print ("Sorry, Python < 2.7 is not supported")
    exit()

#parse requirements
req_lines = [line.strip() for line in open("requirements.txt").readlines()]
install_reqs = list(filter(None, req_lines))

test_req_lines = [line.strip() for line in open("test-requirements.txt").readlines()]
test_reqs = list(filter(None, test_req_lines))

with codecs.open('README.rst', 'r', encoding='utf8') as file:
    long_description = file.read()


setup(name='ncclient',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description="Python library for NETCONF clients",
      long_description = long_description,
      author=__author__,
      author_email=__author_email__,
      url="https://github.com/ncclient/ncclient",
      packages=find_packages(exclude=['test', 'test.*']),
      install_requires=install_reqs,
      tests_require=test_reqs,
      license=__licence__,
      platforms=["Posix; OS X; Windows"],
      keywords=['NETCONF', 'NETCONF Python client', 'Juniper Optimization', 'Cisco NXOS Optimization'],
      python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: System :: Networking',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ])







