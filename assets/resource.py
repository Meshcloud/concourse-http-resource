#!/usr/bin/env python3

import glob
import json
import logging as log
import os
import re
import sys
import tempfile
from distutils.version import LooseVersion

import requests


class HTTPResource:
    """HTTP resource implementation."""

    def should_verify_ssl(self, source):
        """Parse the ssl_verify setting from source."""
        ssl_verify = source.get('ssl_verify', True)

        if isinstance(ssl_verify, bool):
            verify = ssl_verify
        elif isinstance(ssl_verify, str):
            # todo: this looks wrong, but I'm no python expert
            verify = str(tempfile.NamedTemporaryFile(
                delete=False, prefix='ssl-').write(verify))

        return verify

    def check(self, source, version):
        """Check for new version(s)."""

        index = source['index']
        regex = re.compile(source['regex'])
        verify = self.should_verify_ssl(source)

        # request index and extract versions
        response = requests.request('GET', index, verify=verify)
        response.raise_for_status()
        index_response = response.text

        versions = regex.findall(index_response)
        versions.sort(key=lambda x: LooseVersion(x))
        versions = [{'version': v} for v in versions]

        # if version is specified get only newer versions
        if version:
            current_version = version
            new_versions = versions[versions.index(current_version):]
            new_versions.pop(0)
        else:
            # otherwise only get the current version
            new_versions = [versions[-1]]

        return new_versions

    def in_cmd(self, target_dir, source, version):
        """Download specific version to target_dir."""

        uri = source['uri_template']
        file_name = source.get('filename')
        verify = self.should_verify_ssl(source)

        # insert version number into URI
        uri = uri.format(**version)

        response = requests.get(uri, stream=True, verify=verify)
        response.raise_for_status()

        if file_name:
            file_name = file_name.format(**version)
        else:
            file_name = uri.split('/')[-1]
        file_path = os.path.join(target_dir, file_name)
        version_file_path = os.path.join(target_dir, 'version')

        with open(file_path, 'wb') as f:
            for block in response.iter_content(1024):
                f.write(block)
            print()

        with open(version_file_path, 'wb') as f:
            f.write(version['version'].encode())

        metadata = []

        # add all response headers to metadata
        for header, value in response.headers.items():
            metadata.append({'name': header, 'value': value})

        # add url to metadata
        metadata.append({'name': 'url', 'value': uri})

        return {
            'version': version,
            'metadata': metadata,
        }

    def out_cmd(self, src_dir, source, version, params):
        """Upload a specific file from src_dir."""

        uri = source['uri_template']
        file_name = params.get('file')
        verify = self.should_verify_ssl(source)

        file_path = os.path.join(src_dir, file_name)

        # unless an exact version is specified, expand file_name glob
        if not version:
            matched = glob.glob(file_path)
            if len(matched) != 1:
                raise Exception('Not exactly one file matched the glob pattern {0}. Matched files: {1}'.format(
                    file_name, matched))

            file_path = matched[0]
            version = {'version': os.path.basename(file_path)}

        # insert version number into URI
        uri = uri.format(**version)

        metadata = []

        with open(file_path, 'rb') as infile:
            response = requests.put(
                uri, data=infile, stream=True, verify=verify)
            response.raise_for_status()

            # add all response headers to metadata
            for header, value in response.headers.items():
                metadata.append({'name': header, 'value': value})

            # add url to metadata
            metadata.append({'name': 'url', 'value': uri})

        return {
            'version': version,
            'metadata': metadata,
        }

    def run(self, command_name, json_data, command_argument):
        """Parse input/arguments, perform requested command return output."""

        with tempfile.NamedTemporaryFile(delete=False, prefix=command_name + '-') as f:
            f.write(bytes(json_data, 'utf-8'))

        data = json.loads(json_data)

        # allow debug logging to console for tests
        if os.environ.get('RESOURCE_DEBUG', False) or data.get('source', {}).get('debug', False):
            log.basicConfig(level=log.DEBUG)
        else:
            logfile = tempfile.NamedTemporaryFile(delete=False, prefix='log')
            log.basicConfig(level=log.DEBUG, filename=logfile.name)
            stderr = log.StreamHandler()
            stderr.setLevel(log.INFO)
            log.getLogger().addHandler(stderr)

        log.debug('command: %s', command_name)
        log.debug('input: %s', data)
        log.debug('args: %s', command_argument)
        log.debug('environment: %s', os.environ)

        # combine source and params
        source = data.get('source', {})
        version = data.get('version', {})
        params = data.get('params', {})

        if command_name == 'check':
            response = self.check(source, version)
        elif command_name == 'in':
            response = self.in_cmd(command_argument[0], source, version)
        elif command_name == 'out':
            response = self.out_cmd(
                command_argument[0], source, version, params)
        else:
            response = {}

        return json.dumps(response)


print(HTTPResource().run(os.path.basename(
    __file__), sys.stdin.read(), sys.argv[1:]))
