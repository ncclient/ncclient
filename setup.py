# Copyright 2009 Shikhar Bhushan
# Copyright 20{13,14} Leonidas Poulopoulos
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

from setuptools import setup
from distutils.command.install import install as _install

import sys
import platform

if not sys.version_info[0] == 2:
    print "Sorry, Python 3 is not supported (yet)"
    exit()

if sys.version_info.major == 2 and sys.version_info.minor < 6:
    print "Sorry, Python < 2.6 is not supported"
    exit()

addextra = []

if platform.system() == 'Linux':
    if platform.linux_distribution()[0] in ['Debian', 'Ubuntu']:
        addextra = ["libxml2-dev", "libxslt1-dev"]

install_requires=[
          "setuptools>0.6",
          "paramiko>1.7",
          "lxml>3.0"]

class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (self.install_lib,),
                     msg="")

def _post_install(dir):
    global addextra
    if addextra:
      print "\nNote: If you haven't done so, consider installing the %s libraries (aptitude install %s)\n" %(", ".join(addextra), " ".join(addextra) )


setup(name='ncclient',
      version='0.4.0',
      description="Python library for NETCONF clients",
# TODO: leopoul: review Cisco ncclient/devices and bring them into third party
      author="Shikhar Bhushan, Leonidas Poulopoulos, Ebben Aries",
      author_email="shikhar@schmizz.net, leopoul@noc.grnet.gr, earies@juniper.net",
      url="http://ncclient.grnet.gr/",
      packages=[
          "ncclient",
          "ncclient/transport",
          "ncclient/operations",
          "ncclient/operations/third_party",
          "ncclient/operations/third_party/juniper",
          ],
      install_requires=install_requires,
      license="Apache License 2.0",
      platforms=["Posix; OS X; Windows"],
      cmdclass={'install': install},
      #classifiers=[]
      )







