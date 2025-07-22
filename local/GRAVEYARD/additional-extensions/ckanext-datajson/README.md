# ckanext-datajson

[![Github Actions](https://github.com/GSA/ckanext-datajson/actions/workflows/test.yml/badge.svg)](https://github.com/GSA/ckanext-datajson/actions)
[![PyPI version](https://badge.fury.io/py/ckanext-datajson.svg)](https://badge.fury.io/py/ckanext-datajson)

A CKAN extension containing plugins `datajson`.
First is used by http://catalog.data.gov/ to harvest data sources
from a remote /data.json file according to the U.S. Project
Open Data metadata specification (https://resources.data.gov/schemas/dcat-us/v1.1/).

Plugin `datajson` provides a harvester to import datasets from other
remote /data.json files. See below for setup instructions.

And the plugin also provides a new view to validate /data.json files
at http://ckanhostname/dcat-us/validator.


## Features

- [:heavy_check_mark:] **datajson** provides data.json export and DCAT-US metadata UI integration
  - Read more about [`datajson`](docs/datajson.md)
- [:heavy_check_mark:] **datajson_harvest** extends [ckanext-harvest](https://github.com/ckan/ckanext-harvest/)
to collect metadata fromremote data.json sources
  - Read more about [`datajson_harvest`](docs/datajson_harvest.md)
- [:warning:] **cmsdatanav_harvest** extends [ckanext-harvest](https://github.com/ckan/ckanext-harvest/)
to collect metadata from for the CMS Data Navigator catalog
- [:heavy_check_mark:] **datajson_validator** provides a web form to validate dcat-us metadata data.json compliance.
  - Read more about [`datajson_validator`](docs/datajson_validator.md)


## Usage

### Requirements

All requirements are tracked `setup.py` when possible.  Some CKAN extensions are not on PyPI, so they 
(and their dependencies) must be tracked in `requirements.txt`.
- [ckanext-harvest](https://github.com/ckan/ckanext-harvest/)

CKAN version   | Compatibility
-------------- | -------------
<=2.7          | :x:
2.8            | :warning:
2.9.5          | :heavy_check_mark:
2.9.6          | :heavy_check_mark:

### Installation

To install, activate your CKAN virtualenv, install dependencies, and
install the module in develop mode, which just puts the directory in your
Python path.

	. path/to/pyenv/bin/activate
	pip install -r requirements.txt
	python setup.py develop

Then in your CKAN .ini file, add `datajson`
to your ckan.plugins line:

	ckan.plugins = (other plugins here...) datajson

That's the plugin for /data.json output. To make the harvester available,
also add:

	ckan.plugins = (other plugins here...) harvest datajson_harvest
	
To make the datajson validator route and web form available, also add:

	ckan.plugins = (other plugins here...) datajson_validator

[ Optional ] Set the resource count limit allowed in one record so that fetch-consumer does not run out of memory during harvesting. Default is unlimited. Once set, records with higher resource count will see import errors. 
 `ckanext.datajson.max_resource_count = 1000`

## Development

### Setup

Build the docker containers.

    $ make build

Start the docker containers.

    $ make up

CKAN will start at [localhost:5000](http://localhost:5000/).

Clean up any containers and volumes.

    $ make clean

Open a shell to run commands in the container.

    $ docker-compose exec app /bin/bash

If you're unfamiliar with docker-compose, see our
[cheatsheet](https://github.com/GSA/datagov-deploy/wiki/Docker-Best-Practices#cheatsheet)
and the [official docs](https://docs.docker.com/compose/reference/).

For additional make targets, see the help.

    $ make help


### Testing

They follow the guidelines for [testing CKAN
extensions](https://docs.ckan.org/en/2.9/extensions/testing-extensions.html#testing-extensions).

To run the extension tests, start the containers with `make up`, then:

    $ make test

Lint the code.

    $ make lint


### Matrix builds

The test development environment drops as many dependencies as possible. It is
not meant to have feature parity with
[GSA/catalog.data.gov](https://github.com/GSA/catalog.data.gov/). Tests should
mock external dependencies where possible.

In order to support multiple versions of CKAN, or even upgrade to new versions
of CKAN, we support development and testing through the `CKAN_VERSION`
environment variable.

    $ make CKAN_VERSION=2.9.5 test
    $ make CKAN_VERSION=2.9 test
    
Note: When testing patch versions of CKAN, the services may not have patch releases.
So, take note of the `SERVICES_VERSION` variable which tracks the minor release to 
pull for the `db` and `solr` images.


## Credit / Copying

Original work written by the HealthData.gov team. It has been modified in support of Data.gov.

As a work of the United States Government, this package is in the public
domain within the United States. Additionally, we waive copyright and
related rights in the work worldwide through the CC0 1.0 Universal
public domain dedication (which can be found at http://creativecommons.org/publicdomain/zero/1.0/).

## Ways to Contribute
We're so glad you're thinking about contributing to ckanext-datajson!

Before contributing to ckanext-datajson we encourage you to read our
[CONTRIBUTING](CONTRIBUTING.md) guide, our [LICENSE](LICENSE.md), and our README
(you are here), all of which should be in this repository. If you have any
questions, you can email the Data.gov team at
[datagov@gsa.gov](mailto:datagov@gsa.gov).
