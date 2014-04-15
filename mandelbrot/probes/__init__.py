# Copyright 2014 Michael Frank <msfrank@syntaxjockey.com>
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

from zope.interface import Interface, implements
from mandelbrot.mbobject import MBObject

class IProbe(Interface):

    def configure(self, section):
        ""

    def set_id(self, objectid):
        ""

    def get_id(self):
        ""

    def get_type(self):
        ""

    def get_metadata(self):
        ""

    def probe(self):
        ""

class Probe(MBObject):
    implements(IProbe)

    def __init__(self):
        MBObject.__init__(self)
        self._objectid = None
        self._objecttype = None
        self.name = None
        self.description = None
        self.tags = None

    def configure(self, section):
        self.name = section.get_str('display name')
        self.description = section.get_str('description')
        self.tags = section.get_list('tags')

    def set_id(self, objectid):
        if self._objectid is not None:
            raise AttributeError("id is already set")
        self._objectid = objectid

    def get_id(self):
        return self._objectid

    id = property(get_id, set_id)

    def get_type(self):
        return self._objecttype

    @property
    def type(self):
        return self.get_type()

    def get_metadata(self):
        return {'prettyName': self.name, 'description': self.description}

    @property
    def metadata(self):
        return self.get_metadata()

    def probe(self):
        raise NotImplementedError()
