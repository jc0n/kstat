
import ctypes as C

from operator import attrgetter

try:
    from collections import Iterator, Iterable
except ImportError:
    from collections.abc import Iterator, Iterable

import libkstat

KSTAT_UNMARSHALL = {
    libkstat.KSTAT_DATA_CHAR: attrgetter('c'),
    libkstat.KSTAT_DATA_INT32: attrgetter('i32'),
    libkstat.KSTAT_DATA_UINT32: attrgetter('ui32'),
    libkstat.KSTAT_DATA_INT64: attrgetter('i64'),
    libkstat.KSTAT_DATA_UINT64: attrgetter('ui64'),
    libkstat.KSTAT_DATA_STRING: attrgetter('str.addr.ptr', 'str.len'),
}

_MODULE__INSTANCE__NAME = attrgetter('ks_module', 'ks_instance', 'ks_name')

class KStatIterator(Iterator):
    def __init__(self, kstat):
        self.kstat = kstat
        self._ksp = kstat._context.contents.kc_chain

    def __iter__(self):
        return KStatIterator(self._kstat)

    def next(self):
        while True:
            if not self._ksp:
                raise StopIteration
            ks = self._ksp.contents
            self._ksp = ks.ks_next
            module, instance, name = module__instance__name = _MODULE__INSTANCE__NAME(ks)
            if ((self.kstat.module is None or self.kstat.module == module) and
                (self.kstat.instance is None or self.kstat.instance == instance) and
                (self.kstat.name is None or self.kstat.name == name)):
                return self.kstat[module__instance__name]

    __next__ = next


class KStatEntry(dict):
    def __init__(self, kstat, entry):
        self.kstat = kstat
        self.entry = entry
        self.INIT_TYPE[entry.ks_type](self, entry)

    def __init_raw(self, ks):
        # TODO
        pass

    def __init_named(self, entry):
        data = C.cast(entry.ks_data, C.POINTER(libkstat.kstat_named))
        for i in range(entry.ks_ndata):
            d = data[i]
            self[d.name] = KSTAT_UNMARSHALL[d.data_type](d.value);

    def __init_intr(self, entry):
        # TODO
        pass

    def __init_io(self, entry):
        # TODO
        pass

    def __init_timer(self, entry):
        # TODO
        pass

    @property
    def module(self):
        return self.entry.ks_module

    @property
    def instance(self):
        return self.entry.ks_instance

    @property
    def name(self):
        return self.entry.ks_name

    INIT_TYPE = {
        libkstat.KSTAT_TYPE_RAW: __init_raw,
        libkstat.KSTAT_TYPE_NAMED: __init_named,
        libkstat.KSTAT_TYPE_INTR: __init_intr,
        libkstat.KSTAT_TYPE_IO: __init_io,
        libkstat.KSTAT_TYPE_TIMER: __init_timer
    }


class KStat(Iterable):
    def __init__(self, module=None, instance=None, name=None):
        self._context = libkstat.kstat_open()
        self.module = bytes(module, 'ascii') if module else None
        self.instance = int(instance) if instance else None
        self.name = bytes(name, 'ascii') if name else None

    def __del__(self):
        libkstat.kstat_close(self._context)

    def __repr__(self):
        args = (type(self).__name__, self.module, self.instance, self.name)
        return '%s(%r, %r, %r)' % args

    def __getitem__(self, key):
        module, instance, name = key
        if not isinstance(module, bytes):
            module = bytes(module, 'ascii', 'ignore')
        if not isinstance(name, bytes):
            name = bytes(name, 'ascii', 'ignore')
        ksp = libkstat.kstat_lookup(self._context, module, instance, name)
        if ksp is None:
            raise KeyError(key)
        libkstat.kstat_read(self._context, ksp, None)
        return KStatEntry(self, ksp.contents)

    def __iter__(self):
        return KStatIterator(self)


# TODO: delete this
def main():
    import pprint as pp
    k = KStat()
    pp.pprint(k)
    pp.pprint(k['sd', 30, 'sd30'])
    pp.pprint(k['zfs', 0, 'zfetchstats'])
    k = KStat('link')
    pp.pprint([((k.module, k.instance, k.name), k) for k in list(k)])

# TODO: delete this
if __name__ == '__main__':
    main()
