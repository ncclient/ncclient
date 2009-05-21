# Copyright 2009 Shikhar Bhushan
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

from distutils.core import setup

setup(name='ncclient',
      version='0.1.0',
      description="Python library for NETCONF clients",
      author="Shikhar Bhushan",
      author_email="shikhar@schmizz.net",
      url="http://code.google.com/p/ncclient/",
      packages=["ncclient", "ncclient/transport", "ncclient/operations"],
      license="Apache License 2.0",
      platforms=["Posix; OS X; Windows"],
      #classifiers=[]
      )
