#!/usr/bin/env python3
# coding: utf-8

import os
import re
import volkanic
from volkanic.compat import cached_property

regexes = {
    '.': re.compile(r'[a-z][0-9a-z]*(\.[a-z][0-9a-z]*)?$'),
    '-': re.compile(r'[a-z][0-9a-z]*(-[a-z][0-9a-z]*)?$'),
    '_': re.compile(r'[a-z][0-9a-z]*(_[a-z][0-9a-z]*)?$'),
}


class GlobalInterface(volkanic.GlobalInterface):
    package_name = 'joker.project'

    @cached_property
    def jinja2_env(self):
        # noinspection PyPackageRequirements
        import jinja2
        cfg = self.conf['jinja2'].copy()
        loader = jinja2.PackageLoader(self.package_name, 'templates')
        loader_cfg = cfg.pop('loader', None)
        if loader_cfg:
            loader = jinja2.ChoiceLoader([
                jinja2.FileSystemLoader(loader_cfg, followlinks=True),
                loader,
            ])
        autoescape_cfg = cfg.pop('autoescape', ['html', 'xml'])
        autoescape = jinja2.select_autoescape(autoescape_cfg)
        return jinja2.Environment(loader=loader, autoescape=autoescape, **cfg)


class ProjectInterface:
    def __init__(self, name: str, parent_dir='.'):
        self.parent_dir = os.path.abspath(parent_dir)
        for sep, regex in regexes.items():
            if regex.match(name):
                self.identifier = name.replace(sep, '_')
                self.package_name = name.replace(sep, '.')
                self.project_name = name.replace(sep, '-')
                self.names = self.package_name.split('.')
                return
        msg = f"neither a project_name, package_name nor identifier: '{name}'"
        raise ValueError(msg)

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

    def under_project_dir(self, *paths, relative=False):
        if relative:
            return os.path.join(*paths)
        return os.path.join(self.parent_dir, self.project_name, *paths)

    def under_package_dir(self, *paths, relative=False):
        parts = list(self.names)
        parts.extend(paths)
        return self.under_project_dir(*parts, relative=relative)
