# -*- coding: utf8 -*-

import serial
import sys
import threading

__all__ = ('Chy506R', )


class Chy506R(threading.Thread):
    def __init__(self, tty, output, timeout=4):
        super().__init__()
        self._lock = threading.RLock()
        with self._lock:
            self._tty = tty
            self._output = output
            self._timeout = timeout
            self._done = False
            self._break = False
            self._count = 0

    @property
    def done(self):
        """Whether measurements are done as user requested"""
        return self._done

    @property
    def count(self):
        """Number of entries written to the output file"""
        return self._count

    def open_tty(self):
        """Open TTY (self._tty) and return its descriptor"""
        with self._lock:
            setup = {
                'baudrate': 1200,
                'bytesize': serial.SEVENBITS,
                'parity': serial.PARITY_EVEN,
                'stopbits': serial.STOPBITS_ONE,
                'timeout': self._timeout,
            }
            return serial.Serial(self._tty, **setup)

    def open_output(self):
        """Open output file (self._output) and return its descriptor"""
        with self._lock:
            if self._output == '-':
                return sys.stdout
            else:
                return open(self._output, 'wt')

    def stop(self):
        """Stop iteration/finish measurements"""
        with self._lock:
            self._break = True

    def _parse_temperature(self, s, i):
        off = 0 if i==1 else 8
        return (-1 if s[off] == '-' else 1) * int(s[1+off:7+off], 16)/1000

    def _parse_timestamp(self, s):
        return (int(s[16:18]), int(s[18:20]), int(s[20:22]))

    def _parse_status(self, s):
        return s[22:]

    def _average_buff(self, buff):
        return tuple(sum(s)/len(buff) for s in zip(*buff))

    def run(self):
        last = (0, 0, -1)
        buff = []  # multiple measurements at same time (H:M:S) get collected here
        with self.open_output() as out, self.open_tty() as tty:
            tty.write("A\n".encode())
            try:
                with self._lock:
                    self._break = False
                    self._done = False
                    self._count = 0
                out.write("TIME;T1;T2\n")
                for line in tty:
                    l = line.strip()
                    if len(l) != 30:
                        sys.stderr.write("warning: protocol error: %s (len = %d)\n" % (repr(l), len(l)))
                        continue  # I've seen, some lines can be broken
                    t1 = self._parse_temperature(l, 1)
                    t2 = self._parse_temperature(l, 2)
                    h, m, s = self._parse_timestamp(l)
                    status = self._parse_status(l)
                    if last < (h, m, s):
                        last = (h, m, s)
                        if buff:
                            m1, m2 = self._average_buff(buff)
                            buff = []
                            out.write("%02d:%02d:%02d;%f;%f\n" % (h, m, s, m1, m2))
                            out.flush()
                            with self._lock:
                                self._count += 1
                    buff.append((t1, t2))
                    with self._lock:
                        if self._break:
                            self._done = True
                            break
                if not self._done:
                    sys.stderr.write("warning: timeout occurred, is the device connected to your PC?\n")
            except KeyboardInterrupt:
                pass
            finally:
                tty.write("B\n".encode())

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
