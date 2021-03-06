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

import time
from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.tz import tzutc
from pyparsing import *

EpochDateTime = Word(srange('[1-9]'), srange('[0-9]'))
def parseEpochDateTime(tokens):
    return datetime.fromtimestamp(long(tokens[0]), tzutc())
EpochDateTime.setParseAction(parseEpochDateTime)

ISODateTimeUTC = Regex(r'\d{4}-\d{2}-\d{2}T\d{2}\:\d{2}\:\d{2}Z')
ISODateTimeAndOffset = Regex(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}')
def parseISODateTime(tokens):
    return parse(tokens[0])
ISODateTimeUTC.setParseAction(parseISODateTime)
ISODateTimeAndOffset.setParseAction(parseISODateTime)

ISODateTime = ISODateTimeUTC | ISODateTimeAndOffset

TimeValue = Word(srange('[1-9]'), srange('[0-9]'))

UnitDays = CaselessKeyword('day') | CaselessKeyword('days')
UnitDays.setParseAction(lambda x: lambda hours: hours * 60 * 60 * 24)
UnitHours = CaselessKeyword('hour') | CaselessKeyword('hours')
UnitHours.setParseAction(lambda x: lambda hours: hours * 60 * 60)
UnitMinutes = CaselessKeyword('minute') | CaselessKeyword('minutes')
UnitMinutes.setParseAction(lambda x: lambda minutes: minutes * 60)
UnitSeconds = CaselessKeyword('second') | CaselessKeyword('seconds')
UnitSeconds.setParseAction(lambda x: lambda seconds: seconds)
TimeUnit = UnitDays | UnitHours | UnitMinutes | UnitSeconds

DirectionAgo = CaselessLiteral("ago")
DirectionAgo.setParseAction(lambda x: lambda point,delta: point - delta)
DirectionAhead = CaselessLiteral("ahead")
DirectionAhead.setParseAction(lambda x: lambda point,delta: point + delta)

RelativeDirection = DirectionAgo | DirectionAhead
RelativeDateTime = TimeValue + TimeUnit + RelativeDirection
def parseRelativeDateTime(tokens):
    value = long(tokens[0])
    magnify = tokens[1]
    shift = tokens[2]
    seconds = magnify(value)
    return shift(datetime.now(tzutc()), timedelta(seconds=seconds))
RelativeDateTime.setParseAction(parseRelativeDateTime)

DateTime = ISODateTime | RelativeDateTime | EpochDateTime

ClosedDateTimeRange = DateTime + Suppress(Literal('..')) + DateTime
LeftOpenDateTimeRange = Literal('..') + DateTime
RightOpenDateTimeRange = DateTime + Literal('..')

DateTimeRange = ClosedDateTimeRange | LeftOpenDateTimeRange | RightOpenDateTimeRange

DateTimePlusDelta = DateTime + Suppress(Literal('+')) + TimeValue + TimeUnit
def parseDateTimePlusDelta(tokens):
    start = tokens[0]
    value = long(tokens[1])
    magnify = tokens[2]
    delta = timedelta(seconds=magnify(value))
    return [start, start + delta]
DateTimePlusDelta.setParseAction(parseDateTimePlusDelta)

NowPlusDelta = Suppress(Literal('+')) + TimeValue + TimeUnit
def parseNowPlusDelta(tokens):
    start = datetime.now(tzutc())
    value = long(tokens[0])
    magnify = tokens[1]
    delta = timedelta(seconds=magnify(value))
    return [start, start + delta]
NowPlusDelta.setParseAction(parseNowPlusDelta)

DateTimeWindow = ClosedDateTimeRange | DateTimePlusDelta | NowPlusDelta

def parse_datetime(string):
    """
    Parse a datetime string.  Datetimes may be specified using the following formats:
    """
    return DateTime.parseString(string, parseAll=True).asList()[0]

def parse_timerange(string):
    """
    Parse a timerange string.  Timeranges may be specified using the following formats:

    START..END      between START and END
    START..         from START to infinity
    ..END           from -infinity to END
   
    Returns a 2-tuple containing the start and end datetimes in UTC timezone,
    otherwise throws Exception.
    """
    start,end = DateTimeRange.parseString(string, parseAll=True).asList()
    if start == "..":
        start = None
    if end == "..":
        end = None
    return (start,end)

def parse_timewindow(string):
    """
    Parse a timewindow.  Timewindows may be specified using the following
    formats:

    START..END
    START+DELTA
    +DELTA

    Returns a 2-tuple containing the start and end datetimes in UTC timezone,
    otherwise throws Exception.
    """
    return DateTimeWindow.parseString(string, parseAll=True).asList()
