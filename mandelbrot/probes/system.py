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

import os, psutil
from mandelbrot.probes import ScalarProbe
from mandelbrot.evaluation import Evaluation, Health
from mandelbrot.table import size2string

class SystemLoad(ScalarProbe):
    """
    Check system load.

    Parameters:

    degraded threshold  = LOAD1: float, LOAD5: float, LOAD15: float
    failed threshold    = LOAD1: float, LOAD5: float, LOAD15: float
    divide per cpu      = PERCPU: boolean = false
    """
    def get_type(self):
        return "io.mandelbrot.probe.SystemLoad"

    def configure(self, section):
        self.failed = section.get_args("failed threshold", float, float, float,
                names=('LOAD1','LOAD5','LOAD15'), minimum=3, maximum=3)
        self.degraded = section.get_args("degraded threshold", float, float, float,
                names=('LOAD1','LOAD5','LOAD15'), minimum=3, maximum=3)
        self.percpu = section.get_bool("divide per cpu", False)
        ScalarProbe.configure(self, section)

    def probe(self):
        load1, load5, load15 = os.getloadavg()
        ncores = psutil.cpu_count()
        summary = "load average is %.1f %.1f %.1f, detected %i cores" % (load1,load5,load15,ncores)
        if self.percpu == True:
            load1 = load1 / float(ncores)
            load5 = load5 / float(ncores)
            load15 = load15 / float(ncores)
        if self.failed is not None:
            fail1, fail5, fail15 = self.failed
            if load1 > fail1 or load5 > fail5 or load15 > fail15:
                return Evaluation(Health.FAILED, summary)
        if self.degraded is not None:
            degr1, degr5, degr15 = self.degraded
            if load1 > degr1 or load5 > degr5 or load15 > degr15:
                return Evaluation(Health.DEGRADED, summary)
        return Evaluation(Health.HEALTHY, summary)

class SystemCPU(ScalarProbe):
    """
    Check system CPU utilization.

    Parameters:
    user failed threshold     = USER: percent
    user degraded threshold   = USER: percent
    system failed threshold   = SYSTEM: percent
    system degraded threshold = SYSTEM: percent
    iowait failed threshold   = IOWAIT: percent
    iowait degraded threshold = IOWAIT: percent
    extended summary          = EXTENDED: bool = false
    """
    def __init__(self):
        ScalarProbe.__init__(self)
        # throw away the first value
        psutil.cpu_times_percent()

    def get_type(self):
        return "io.mandelbrot.probe.SystemCPU"

    def configure(self, section):
        self.userfailed = section.get_percent("user failed threshold", None)
        self.userdegraded = section.get_percent("user degraded threshold", None)
        self.systemfailed = section.get_percent("system failed threshold", None)
        self.systemdegraded = section.get_percent("system degraded threshold", None)
        self.iowaitfailed = section.get_percent("iowait failed threshold", None)
        self.iowaitdegraded = section.get_percent("iowait degraded threshold", None)
        self.extended = section.get_bool("extended summary", False)
        ScalarProbe.configure(self, section)

    def probe(self):
        times = psutil.cpu_times_percent()
        items = sorted(times._asdict().items())
        if self.extended == False:
            showvals = ", ".join(["%.1f%% %s" % (v,n) for n,v in items if v != 0.0])
        else:
            showvals = ", ".join(["%.1f%% %s" % (v,n) for n,v in items])
        summary = "CPU utilization is " + showvals
        if self.userfailed is not None and times.user > self.userfailed:
            return Evaluation(Health.FAILED, summary)
        if self.systemfailed is not None and times.system > self.systemfailed:
            return Evaluation(Health.FAILED, summary)
        if self.iowaitfailed is not None and times.iowait > self.iowaitfailed:
            return Evaluation(Health.FAILED, summary)
        if self.userdegraded is not None and times.user > self.userdegraded:
            return Evaluation(Health.DEGRADED, summary)
        if self.systemdegraded is not None and times.system > self.systemdegraded:
            return Evaluation(Health.DEGRADED, summary)
        if self.iowaitdegraded is not None and times.iowait > self.iowaitdegraded:
            return Evaluation(Health.DEGRADED, summary)
        return Evaluation(Health.HEALTHY, summary)

class SystemMemory(ScalarProbe):
    """
    Check system memory utilization.

    Parameters:
    memory failed threshold   = USAGE: size
    memory degraded threshold = USAGE: size
    swap failed threshold     = USAGE: size
    swap degraded threshold   = USAGE: size
    """
    def get_type(self):
        return "io.mandelbrot.probe.SystemMemory"

    def configure(self, section):
        self.memoryfailed = section.get_size("memory failed threshold", None)
        self.memorydegraded = section.get_size("memory degraded threshold", None)
        self.swapfailed = section.get_size("swap failed threshold", None)
        self.swapdegraded = section.get_size("swap degraded threshold", None)
        ScalarProbe.configure(self, section)

    def probe(self):
        memory = psutil.virtual_memory()
        memused = memory.percent
        memtotal = size2string(memory.total)
        swap = psutil.swap_memory()
        swapused = swap.percent
        swaptotal = size2string(swap.total)
        summary = "%.1f%% used of %s of physical memory; %.1f%% used of %s of swap" % (memused,memtotal,swapused,swaptotal)
        if self.memoryfailed is not None and memory.used > self.memoryfailed:
            return Evaluation(Health.FAILED, summary)
        if self.swapfailed is not None and swap.used > self.swapfailed:
            return Evaluation(Health.FAILED, summary)
        if self.memorydegraded is not None and memory.used > self.memorydegraded:
            return Evaluation(Health.DEGRADED, summary)
        if self.swapdegraded is not None and swap.used > self.swapdegraded:
            return Evaluation(Health.DEGRADED, summary)
        return Evaluation(Health.HEALTHY, summary)

class SystemDiskUsage(ScalarProbe):
    """
    Check system disk utilization.

    Parameters:
    disk partition          = PATH: path = /
    disk failed threshold   = USAGE: size
    disk degraded threshold = USAGE: size
    """
    def get_type(self):
        return "io.mandelbrot.probe.SystemDiskUsage"

    def configure(self, section):
        self.partition = section.get_path("disk partition", "/")
        self.diskfailed = section.get_size("disk failed threshold", None)
        self.diskdegraded = section.get_size("disk degraded threshold", None)
        ScalarProbe.configure(self, section)

    def probe(self):
        disk = psutil.disk_usage(self.partition)
        diskused = disk.percent
        disktotal = size2string(disk.total)
        summary = "%.1f%% used of %s on %s" % (diskused,disktotal,self.partition)
        if self.diskfailed is not None and disk.used > self.diskfailed:
            return Evaluation(Health.FAILED, summary)
        if self.diskdegraded is not None and disk.used > self.diskdegraded:
            return Evaluation(Health.DEGRADED, summary)
        return Evaluation(Health.HEALTHY, summary)

class SystemDiskPerformance(ScalarProbe):
    """
    Check system disk performance.

    Parameters:
    disk device              = PATH: path
    read failed threshold    = USAGE: int
    read degraded threshold  = USAGE: int
    write failed threshold   = USAGE: int
    write degraded threshold = USAGE: int
    """
    def get_type(self):
        return "io.mandelbrot.probe.SystemDiskPerformance"

    def configure(self, section):
        self.device = section.get_path("disk device", None)
        self.readfailed = section.get_int("read failed threshold", None)
        self.readdegraded = section.get_int("read degraded threshold", None)
        self.writefailed = section.get_int("write failed threshold", None)
        self.writedegraded = section.get_int("write degraded threshold", None)
        ScalarProbe.configure(self, section)

    def probe(self):
        if self.device is not None:
            disk = psutil.disk_io_counters(perdisk=True)[self.device]
        else:
            disk = psutil.disk_io_counters(perdisk=False)
        reads = disk.read_count
        writes = disk.write_count
        if self.device is not None:
            summary = "%i reads, %i writes on %s" % (reads,writes,self.device)
        else:
            summary = "%i reads, %i writes across all devices" % (reads,writes)
        if self.readfailed is not None and reads > self.readfailed:
            return Evaluation(Health.FAILED, summary)
        if self.writefailed is not None and writes > self.writefailed:
            return Evaluation(Health.FAILED, summary)
        if self.readdegraded is not None and reads > self.readdegraded:
            return Evaluation(Health.DEGRADED, summary)
        if self.writedegraded is not None and writes > self.writedegraded:
            return Evaluation(Health.DEGRADED, summary)
        return Evaluation(Health.HEALTHY, summary)

class SystemNetPerformance(ScalarProbe):
    """
    Check system network performance.

    Parameters:
    net device              = DEVICE: str
    send failed threshold   = USAGE: int
    send degraded threshold = USAGE: int
    recv failed threshold   = USAGE: int
    recv degraded threshold = USAGE: int
    """
    def get_type(self):
        return "io.mandelbrot.probe.SystemNetPerformance"

    def configure(self, section):
        self.device = section.get_str("net device", None)
        self.sendfailed = section.get_int("send failed threshold", None)
        self.senddegraded = section.get_int("send degraded threshold", None)
        self.recvfailed = section.get_int("recv failed threshold", None)
        self.recvdegraded = section.get_int("recv degraded threshold", None)
        ScalarProbe.configure(self, section)

    def probe(self):
        if self.device is not None:
            net = psutil.net_io_counters(pernic=True)[self.device]
        else:
            net = psutil.net_io_counters(pernic=False)
        tx = net.packets_sent
        rx = net.packets_recv
        errin = net.errin
        errout = net.errout
        dropin = net.dropin
        dropout = net.dropout
        if self.device is not None:
            summary = "%i packets sent, %i packets received on %s" % (tx,rx,self.device)
        else:
            summary = "%i packets sent, %i packets received across all devices" % (tx,rx)
        if self.sendfailed is not None and tx > self.sendfailed:
            return Evaluation(Health.FAILED, summary)
        if self.recvfailed is not None and rx > self.recvfailed:
            return Evaluation(Health.FAILED, summary)
        if self.senddegraded is not None and tx > self.senddegraded:
            return Evaluation(Health.DEGRADED, summary)
        if self.recvdegraded is not None and rx > self.recvdegraded:
            return Evaluation(Health.DEGRADED, summary)
        return Evaluation(Health.HEALTHY, summary)

