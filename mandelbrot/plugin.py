# Copyright 2013 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Mandelbrot.
#
# Mandelbrot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Mandelbrot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Mandelbrot.  If not, see <http://www.gnu.org/licenses/>.

from pkg_resources import Environment, working_set
from mandelbrot.loggers import getLogger

logger = getLogger("mandelbrot.plugin")

class PluginError(Exception):
    pass

class IPlugin(object):

    def __init__(self, *args, **kwargs):
        pass

    def configure(self, section):
        pass

    def init(self):
        pass

    def fini(self):
        pass

class PluginManager(object):
    """
    """

    def configure(self, section):
        env = Environment([])
        self._eggs,errors = working_set.find_plugins(env)
        # load plugin eggs
        for p in self._eggs:
            working_set.add(p)
        for e in errors:
            logger.info("failed to load plugin egg '%s'", e)

    def getfactory(self, group, name=None):
        entrypoints = list(working_set.iter_entry_points(group, name))
        if len(entrypoints) == 0:
            raise PluginError("Factory not found for entry point %s:%s" % (group,name))
        return entrypoints[0].load()

    def newinstance(self, group, name, *args, **kwargs):
        factory = self.getfactory(group, name)
        return factory()
