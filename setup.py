# Copyright 2009 Shikhar Bhushan
# Copyright 201[2-4] Leonidas Poulopoulos (@leopoul)
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

import sys

if sys.version_info[0] == 2 and sys.version_info[1] < 6:
    print("Sorry, Python < 2.6 is not supported")
    exit()

#parse requirements
req_lines = [line.strip() for line in open("requirements.txt").readlines()]
install_reqs = list(filter(None, req_lines))

with open('README.rst') as file:
    long_description = file.read()


setup(name='ncclient',
      version='0.4.3',
      description="Python library for NETCONF clients",
      long_description = long_description,
      author="Shikhar Bhushan, Leonidas Poulopoulos, Ebben Aries",
      author_email="shikhar@schmizz.net, leopoul@noc.grnet.gr, earies@juniper.net",
      url="http://ncclient.leopoul.com",
      packages=find_packages('.'),
      install_requires=install_reqs,
      license="Apache License 2.0",
      platforms=["Posix; OS X; Windows"],
      keywords=('NETCONF', 'NETCONF Python client', 'Juniper Optimization', 'Cisco NXOS Optimization'),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Networking',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ]
      )







