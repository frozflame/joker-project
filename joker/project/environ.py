#!/usr/bin/env python3
# coding: utf-8

import os
import re

import volkanic
from volkanic.compat import cached_property


class GlobalInterface(volkanic.GlobalInterface):
    package_name = 'joker.project'
    _options = {'namespaced_config_path': True}

    default_config = {
        'templates': [],
    }

    @cached_property
    def jinja2_env(self):
        # noinspection PyPackageRequirements
        import jinja2
        loader = jinja2.PackageLoader(self.package_name, 'templates')
        searchpath = self.conf['templates']
        if searchpath:
            loader = jinja2.ChoiceLoader([
                jinja2.FileSystemLoader(searchpath, followlinks=True),
                loader,
            ])
        autoescape = jinja2.select_autoescape(['html', 'xml'])
        return jinja2.Environment(loader=loader, autoescape=autoescape)


class ProjectInterface:
    _regexes = {
        '.': re.compile(r'[a-z][0-9a-z]*(\.[a-z][0-9a-z]*)?$'),
        '-': re.compile(r'[a-z][0-9a-z]*(-[a-z][0-9a-z]*)?$'),
        '_': re.compile(r'[a-z][0-9a-z]*(_[a-z][0-9a-z]*)?$'),
    }

    def __init__(self, name: str, parent_dir='.'):
        self.parent_dir = os.path.abspath(parent_dir)
        self.names = []
        for sep, regex in self._regexes.items():
            if regex.match(name):
                self.package_name = name.replace(sep, '.')
                self.project_name = name.replace(sep, '-')
                self.identifier = name.replace(sep, '_')
                self.names = name.split(sep)
                break
        if not self.names:
            msg = (
                f"neither a project_name, package_name "
                f"nor identifier: '{name}'"
            )
            raise ValueError(msg)
        self.description = f'{self.project_name} project'

    def __repr__(self):
        c = self.__class__.__name__
        r = repr(self.package_name)
        return f'{c}({r})'

    @property
    def namespace_names(self) -> list:
        return self.names[:-1]

    @property
    def namespace(self) -> str:
        return '.'.join(self.namespace_names)

    @property
    def package_path(self):
        return '/'.join(self.names)

    @property
    def name_length(self) -> int:
        return len(self.project_name)

    def under_project_dir(self, *paths, relative=False):
        if relative:
            return os.path.join(*paths)
        return os.path.join(self.parent_dir, self.project_name, *paths)

    def under_package_dir(self, *paths, relative=False):
        parts = list(self.names)
        parts.extend(paths)
        return self.under_project_dir(*parts, relative=relative)
