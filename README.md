![Build Status](https://github.com/ncclient/ncclient/actions/workflows/check.yaml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/ncclient/ncclient/badge.svg?branch=master)](https://coveralls.io/github/ncclient/ncclient?branch=master)
[![Documentation Status](https://readthedocs.org/projects/ncclient/badge/?version=latest)](https://readthedocs.org/projects/ncclient/?badge=latest)


# ncclient: Python library for NETCONF clients

ncclient is a Python library that facilitates client-side scripting
and application development around the NETCONF protocol. `ncclient` was
developed by [Shikar Bhushan](http://schmizz.net). It is now maintained
by [Leonidas Poulopoulos (@leopoul)](http://ncclient.org) and Einar Nilsen-Nygaard (@einarnn)

**Docs**: [http://ncclient.readthedocs.org](http://ncclient.readthedocs.org)

**PyPI**: [https://pypi.python.org/pypi/ncclient](https://pypi.python.org/pypi/ncclient)


## Recent Highlights

|  Date  | Release | Description |
| :----: | :-----: | :---------- |
| 05/29/21 | `0.6.12` | See [release page](https://github.com/ncclient/ncclient/releases/tag/v0.6.12)|
| 05/27/21 | `0.6.11` | See [release page](https://github.com/ncclient/ncclient/releases/tag/v0.6.11)|
| 02/18/21 | `0.6.10` | See [release page](https://github.com/ncclient/ncclient/releases/tag/v0.6.10)|
| 08/08/20 | `0.6.9` | See [release page](https://github.com/ncclient/ncclient/releases/tag/v0.6.9) |
| 08/01/20 | `0.6.8` | Pulled due to accidental breaking API change |
| 12/21/19 | `0.6.7` | See [release page](https://github.com/ncclient/ncclient/releases/tag/v0.6.7) |
| 05/27/19 | `0.6.6` | See [release page](https://github.com/ncclient/ncclient/releases/tag/v0.6.6) |
| 05/27/19 | `0.6.5` | Pulled due to bug in PyPi upload |
| 04/07/19 | `0.6.4` | See [release page](https://github.com/ncclient/ncclient/releases/tag/v0.6.4) |
| 09/26/18 | `0.6.3` | See [release page](https://github.com/ncclient/ncclient/releases/tag/v0.6.3) |
| 08/20/18 | `0.6.2` | See [release page](https://github.com/ncclient/ncclient/releases/tag/v0.6.2) |
| 07/02/18 | `0.6.0` | Minor release reinstating Python 3.7 and greater compatibility, but necessitating a change to client code that uses `async_mode`. |
| 07/02/18 | `0.5.4` | New release rolling up myriad of small commits since `0.5.3`. Please note that this release is **incompatible wth Python 3.7** due to the use of a new Python 3.7 keyword, `async`, in function signatures. This will be resolved in 0.6.0|

## Requirements

* Python 2.7 or Python 3.5+
* setuptools 0.6+
* Paramiko 1.7+
* lxml 3.3.0+
* libxml2
* libxslt

If you are on Debian/Ubuntu install the following libs (via aptitude or apt-get):
* libxml2-dev
* libxslt1-dev

## Installation

    [ncclient] $ sudo python setup.py install
    
or via pip:

    pip install ncclient

Also locally via pip from within local clone:

    pip install -U .

## Examples

    [ncclient] $ python examples/juniper/*.py

## Usage

### Get device running config
Use either an interactive Python console (ipython)
or integrate the following in your code:

    from ncclient import manager

    with manager.connect(host=host, port=830, username=user, hostkey_verify=False) as m:
        c = m.get_config(source='running').data_xml
        with open("%s.xml" % host, 'w') as f:
            f.write(c)

As of 0.4.1 ncclient integrates Juniper's and Cisco's forks, lots of new concepts
have been introduced that ease management of Juniper and Cisco devices respectively.
The biggest change is the introduction of device handlers in connection paramms.
For example to invoke Juniper's functions annd params one has to re-write the above with `device_params={'name':'junos'}`:

    from ncclient import manager

    with manager.connect(host=host, port=830,
                         username=user, hostkey_verify=False,
                         device_params={'name':'junos'}) as m:
        c = m.get_config(source='running').data_xml
        with open("%s.xml" % host, 'w') as f:
            f.write(c)

Device handlers are easy to implement and prove to be futureproof.

### Supported device handlers

When instantiating a connection to a known type of NETCONF server:

* Juniper: `device_params={'name':'junos'}`
* Cisco:
    - CSR: `device_params={'name':'csr'}`
    - Nexus: `device_params={'name':'nexus'}`
    - IOS XR: `device_params={'name':'iosxr'}`
    - IOS XE: `device_params={'name':'iosxe'}`
* Huawei:
    - `device_params={'name':'huawei'}`
    - `device_params={'name':'huaweiyang'}`
* Nokia SR OS: `device_params={'name':'sros'}`
* H3C: `device_params={'name':'h3c'}`
* HP Comware: `device_params={'name':'hpcomware'}`
* Server or anything not in above: `device_params={'name':'default'}`


## For Developers

### Running Unit Tests Locally

To run the same tests locally as are run via GitHub's CI/CD integration with Travis, the following istructions can be followed:

1. Create a virtual environment, in this case using `virtualenvwrapper`:

    ```
    mkvirtualenv ncclient-testing
    ```

1. Install your local `ncclient` package (ensuring you are in your virtual environment):

    ```
    pip install -U .
    ```

1. Install testing dependencies:

    ```
    pip install nose rednose coverage coveralls mock
    ```

1. Finally, run the tests:

    ```
    nosetests test --rednose --verbosity=3
    ```

### Making a Release

As of `0.6.1`, `versioneer` has been integrated into the `ncclient` codebase. This simplifies the creation of a new release, by ensuring that version numbers are automatically generated from the git tag used for the release, which **must** be in the form `v0.1.2`. Versioneer also allows for the clean install of development versions locally using pip. For example:

```
$ pip install -U .
Processing /opt/git-repos/versioneer-ncclient

[...intermediate ouput elided...]

Building wheels for collected packages: ncclient
  Running setup.py bdist_wheel for ncclient ... done
  Stored in directory: /Users/einarnn/Library/Caches/pip/wheels/fb/48/a8/5c781ebcfff7f091e18950e125c0ff638a5a2dc006610aa1e5
Successfully built ncclient
Installing collected packages: ncclient
  Found existing installation: ncclient 0.6.1
    Uninstalling ncclient-0.6.1:
      Successfully uninstalled ncclient-0.6.1
Successfully installed ncclient-0.6.0+23.g0d9ccd6.dirty
```

Thus, making a release becomes a simple process:

1. Ensure all tests run clean (ideally both locally and via Travis) and that `README.md` (yes, this file!!) has been updated appropriately.
2. Apply appropriate version tag, e.g. `git tag v0.6.1`
3. Build packages:

    ```
    python setup.py bdist sdist
    ```

4. After ensuring twine is installed, test twine upload:

    ```
    twine upload \
        --repository-url https://test.pypi.org/legacy/ \
        -u ******* -p ******* \
        dist/ncclient-0.6.1.tar.gz
    ````

5. Push git tags back to origin, `git push --tags`
6. Do real twine upload:

    ```
    twine upload \
        -u ******* -p ******* \
        dist/ncclient-0.6.1.tar.gz
    ```

## Contributors

* v0.6.12: @einarnn
* v0.6.11: @musicinmybrain, @sstancu, @earies
* v0.6.10: @vnitinv, @omaxx, @einarnn, @musicinmybrain, @tonynii, @sstancu, Martin Volf, @fredgan, @avisom, Viktor Velichkin, @ogenstad, @earies
* v0.6.8: [Fred Gan](https://github.com/fredgan), @vnitinv, @kbijakowski, @iwanb, @badguy99, @liuyong, Andrew Mallory, William Lvory
* v0.6.7: @vnitinv, @chaitu-tk, @sidhujasminder, @crutcha, @markgoddard, @ganeshrn, @songxl, @doesitblend, @psikala, @xuxiaowei0512, @muffizone
* v0.6.6: @sstancu, @hemna, @ishayansheikh
* v0.6.4: @davidhankins, @mzagozen, @knobix, @markafarrell, @psikala, @moepman, @apt-itude, @yuekyang
* v0.6.3: @rdkls, @Anthony25, @rsmekala, @vnitinv, @siming85
* v0.6.2: @einarnn, @glennmatthews, @bryan-stripe, @nickylba
* v0.6.0: @einarnn
* v0.5.4: @adamcubel, Joel Teichroeb, @leopoul, Chase Garner, @budhadityabanerjee, @earies, @ganeshrn, @vnitinv, Siming Yuan, @mirceaaulinic, @stacywsmith, Xavier Hardy, @jwwilcox, @QijunPan, @avangel, @marekgr, @hugovk, @felixonmars, @dexteradeus
* v0.5.3: [Justin Wilcox](https://github.com/jwwilcox), [Stacy W. Smith](https://github.com/stacywsmith), [Mircea Ulinic](https://github.com/mirceaulinic), [Ebben Aries](https://github.com/earies), [Einar Nilsen-Nygaard](https://github.com/einarnn), [QijunPan](https://github.com/QijunPan)
* v0.5.2: [Nitin Kumar](https://github.com/vnitinv), [Kristian Larsson](https://github.com/plajjan), [palashgupta](https://github.com/palashgupta), [Jonathan Provost](https://github.com/JoProvost), [Jainpriyal](https://github.com/Jainpriyal), [sharang](https://github.com/sharang), [pseguel](https://github.com/pseguel), [nnakamot](https://github.com/nnakamot), [Алексей Пастухов](https://github.com/p-alik), [Christian Giese](https://github.com/GIC-de), [Peipei Guo](https://github.com/peipeiguo), [Time Warner Cable Openstack Team](https://github.com/twc-openstack)
* v0.4.7: [Einar Nilsen-Nygaard](https://github.com/einarnn), [Vaibhav Bajpai](https://github.com/vbajpai), Norio Nakamoto 
* v0.4.6: [Nitin Kumar](https://github.com/vnitinv), [Carl Moberg](https://github.com/cmoberg), [Stavros Kroustouris](https://github.com/kroustou) 
* v0.4.5: [Sebastian Wiesinger](https://github.com/sebastianw), [Vincent Bernat](https://github.com/vincentbernat), [Matthew Stone](https://github.com/bigmstone), [Nitin Kumar](https://github.com/vnitinv)
* v0.4.3: [Jeremy Schulman](https://github.com/jeremyschulman), [Ray Solomon](https://github.com/rsolomo), [Rick Sherman](https://github.com/shermdog), [subhak186](https://github.com/subhak186)
* v0.4.2: [katharh](https://github.com/katharh), [Francis Luong (Franco)](https://github.com/francisluong), [Vincent Bernat](https://github.com/vincentbernat), [Juergen Brendel](https://github.com/juergenbrendel), [Quentin Loos](https://github.com/Kent1), [Ray Solomon](https://github.com/rsolomo), [Sebastian Wiesinger](https://github.com/sebastianw), [Ebben Aries](https://github.com/earies) 
* v0.4.1: [Jeremy Schulman](https://github.com/jeremyschulman), [Ebben Aries](https://github.com/earies), Juergen Brendel

