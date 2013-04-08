#
# The contents of this file are subject to the terms of the
# Common Development and Distribution License (the "License").
# You may not use this file except in compliance with the License.
#
# See the License for the specific language governing permissions
# and limitations under the License.
#
#
# Copyright 2011 Grigale Ltd. All rigths reserved.
# Use is sujbect to license terms.
#
import ctypes as C


KSTAT_TYPE_RAW = 0
KSTAT_TYPE_NAMED = 1
KSTAT_TYPE_INTR = 2
KSTAT_TYPE_IO = 3
KSTAT_TYPE_TIMER = 4

kstat_type_names = {
    KSTAT_TYPE_RAW: 'raw',
    KSTAT_TYPE_NAMED: 'named',
    KSTAT_TYPE_INTR: 'intr',
    KSTAT_TYPE_IO: 'io',
    KSTAT_TYPE_TIMER: 'timer'
}

KSTAT_STRLEN = 31

hrtime_t = C.c_longlong
kid_t = C.c_int
kstat_string = C.c_char * KSTAT_STRLEN

class kstat(C.Structure):
    pass

kstat_p = C.POINTER(kstat)

kstat._fields_ = [
    ('ks_crtime', hrtime_t),
    ('ks_next', kstat_p),
    ('ks_kid', kid_t),
    ('ks_module', kstat_string),
    ('ks_resv', C.c_ubyte),
    ('ks_instance', C.c_int),
    ('ks_name', kstat_string),
    ('ks_type', C.c_ubyte),
    ('ks_class', kstat_string),
    ('ks_flags', C.c_ubyte),
    ('ks_data', C.c_void_p),
    ('ks_ndata', C.c_uint),
    ('ks_data_size', C.c_size_t),
    ('ks_snaptime', hrtime_t),

    ('ks_update', C.c_void_p),
    ('ks_private', C.c_void_p),
    ('ks_snapshot', C.c_void_p),
    ('ks_lock', C.c_void_p)
]


#/*
# * kstat_open() returns a pointer to a kstat_ctl_t.
# * This is used for subsequent libkstat operations.
# */
#typedef struct kstat_ctl {
#        kid_t   kc_chain_id;    /* current kstat chain ID       */
#        kstat_t *kc_chain;      /* pointer to kstat chain       */
#        int     kc_kd;          /* /dev/kstat descriptor        */
#} kstat_ctl_t;

class kstat_ctl(C.Structure):
    _fields_ = [
        ('kc_chain_id', kid_t),
        ('kc_chain', C.POINTER(kstat)),
        ('kc_kd', C.c_int)
    ]


#typedef struct kstat_named {
#        char    name[KSTAT_STRLEN];     /* name of counter */
#        uchar_t data_type;              /* data type */
#        union {
#                char            c[16];  /* enough for 128-bit ints */
#                int32_t         i32;
#                uint32_t        ui32;
#                struct {
#                        union {
#                                char            *ptr;   /* NULL-term string */
#                                char            __pad[8]; /* 64-bit padding */
#                        } addr;
#                        uint32_t        len;    /* # bytes for strlen + '\0' */
#                } str;
#/*
# * The int64_t and uint64_t types are not valid for a maximally conformant
# * 32-bit compilation environment (cc -Xc) using compilers prior to the
# * introduction of C99 conforming compiler (reference ISO/IEC 9899:1990).
# * In these cases, the visibility of i64 and ui64 is only permitted for
# * 64-bit compilation environments or 32-bit non-maximally conformant
# * C89 or C90 ANSI C compilation environments (cc -Xt and cc -Xa). In the
# * C99 ANSI C compilation environment, the long long type is supported.
# * The _INT64_TYPE is defined by the implementation (see sys/int_types.h).
# */
##if defined(_INT64_TYPE)
#                int64_t         i64;
#                uint64_t        ui64;
##endif
#                long            l;
#                ulong_t         ul;
#
#                /* These structure members are obsolete */
#
#                longlong_t      ll;
#                u_longlong_t    ull;
#                float           f;
#                double          d;
#        } value;                        /* value of counter */
#} kstat_named_t;

KSTAT_DATA_CHAR = 0
KSTAT_DATA_INT32 = 1
KSTAT_DATA_UINT32 = 2
KSTAT_DATA_INT64 = 3
KSTAT_DATA_UINT64 = 4
KSTAT_DATA_STRING = 9

class addr_union(C.Union):
    _fields_ = [
        ('ptr', C.c_char_p),
        ('__pad', C.c_char * 8),
    ]


class str_struct(C.Structure):
    _fields_ = [
        ('addr', addr_union),
        ('len', C.c_uint32),
    ]


class value_union(C.Union):
    _fields_ = [
        ('c', C.c_char * 16),
        ('i32', C.c_int32),
        ('ui32', C.c_uint32),
        ('i64', C.c_int64),
        ('ui64', C.c_uint64),
        ('str', str_struct),
    ]


class kstat_named(C.Structure):
    _fields_ = [
        ('name', kstat_string),
        ('data_type', C.c_ubyte),
        ('value', value_union),
    ]

kstat_named_p = C.POINTER(kstat_named)

#typedef struct kstat_io {
#
#	/*
#	 * Basic counters.
#	 *
#	 * The counters should be updated at the end of service
#	 * (e.g., just prior to calling biodone()).
#	 */
#
#	u_longlong_t	nread;		/* number of bytes read */
#	u_longlong_t	nwritten;	/* number of bytes written */
#	uint_t		reads;		/* number of read operations */
#	uint_t		writes;		/* number of write operations */
#
#	/*
#	 * Accumulated time and queue length statistics.
#	 *
#	 * Accumulated time statistics are kept as a running sum
#	 * of "active" time.  Queue length statistics are kept as a
#	 * running sum of the product of queue length and elapsed time
#	 * at that length -- i.e., a Riemann sum for queue length
#	 * integrated against time.  (You can also think of the active time
#	 * as a Riemann sum, for the boolean function (queue_length > 0)
#	 * integrated against time, or you can think of it as the
#	 * Lebesgue measure of the set on which queue_length > 0.)
#	 *
#	 *		^
#	 *		|			_________
#	 *		8			| i4	|
#	 *		|			|	|
#	 *	Queue	6			|	|
#	 *	Length	|	_________	|	|
#	 *		4	| i2	|_______|	|
#	 *		|	|	    i3		|
#	 *		2_______|			|
#	 *		|    i1				|
#	 *		|_______________________________|
#	 *		Time->	t1	t2	t3	t4
#	 *
#	 * At each change of state (entry or exit from the queue),
#	 * we add the elapsed time (since the previous state change)
#	 * to the active time if the queue length was non-zero during
#	 * that interval; and we add the product of the elapsed time
#	 * times the queue length to the running length*time sum.
#	 *
#	 * This method is generalizable to measuring residency
#	 * in any defined system: instead of queue lengths, think
#	 * of "outstanding RPC calls to server X".
#	 *
#	 * A large number of I/O subsystems have at least two basic
#	 * "lists" of transactions they manage: one for transactions
#	 * that have been accepted for processing but for which processing
#	 * has yet to begin, and one for transactions which are actively
#	 * being processed (but not done). For this reason, two cumulative
#	 * time statistics are defined here: wait (pre-service) time,
#	 * and run (service) time.
#	 *
#	 * All times are 64-bit nanoseconds (hrtime_t), as returned by
#	 * gethrtime().
#	 *
#	 * The units of cumulative busy time are accumulated nanoseconds.
#	 * The units of cumulative length*time products are elapsed time
#	 * times queue length.
#	 *
#	 * Updates to the fields below are performed implicitly by calls to
#	 * these five functions:
#	 *
#	 *	kstat_waitq_enter()
#	 *	kstat_waitq_exit()
#	 *	kstat_runq_enter()
#	 *	kstat_runq_exit()
#	 *
#	 *	kstat_waitq_to_runq()		(see below)
#	 *	kstat_runq_back_to_waitq()	(see below)
#	 *
#	 * Since kstat_waitq_exit() is typically followed immediately
#	 * by kstat_runq_enter(), there is a single kstat_waitq_to_runq()
#	 * function which performs both operations.  This is a performance
#	 * win since only one timestamp is required.
#	 *
#	 * In some instances, it may be necessary to move a request from
#	 * the run queue back to the wait queue, e.g. for write throttling.
#	 * For these situations, call kstat_runq_back_to_waitq().
#	 *
#	 * These fields should never be updated by any other means.
#	 */
#
#	hrtime_t wtime;		/* cumulative wait (pre-service) time */
#	hrtime_t wlentime;	/* cumulative wait length*time product */
#	hrtime_t wlastupdate;	/* last time wait queue changed */
#	hrtime_t rtime;		/* cumulative run (service) time */
#	hrtime_t rlentime;	/* cumulative run length*time product */
#	hrtime_t rlastupdate;	/* last time run queue changed */
#
#	uint_t	wcnt;		/* count of elements in wait state */
#	uint_t	rcnt;		/* count of elements in run state */
#
#} kstat_io_t;

class kstat_io(C.Structure):
    _fields_ = [
        ('nread', C.c_ulonglong),
        ('nwritten', C.c_ulonglong),
        ('reads', C.c_uint),
        ('writes', C.c_uint),
        ('wtime', hrtime_t),
        ('wlentime', hrtime_t),
        ('wlastupdate', hrtime_t),
        ('rtime', hrtime_t),
        ('rlentime', hrtime_t),
        ('rlastupdate', hrtime_t),
        ('wcnt', C.c_uint),
        ('rcnt', C.c_uint),
    ]

kstat_io_p = C.POINTER(kstat_io)

#/*
# * Interrupt statistics.
# *
# * An interrupt is a hard interrupt (sourced from the hardware device
# * itself), a soft interrupt (induced by the system via the use of
# * some system interrupt source), a watchdog interrupt (induced by
# * a periodic timer call), spurious (an interrupt entry point was
# * entered but there was no interrupt condition to service),
# * or multiple service (an interrupt condition was detected and
# * serviced just prior to returning from any of the other types).
# *
# * Measurement of the spurious class of interrupts is useful for
# * autovectored devices in order to pinpoint any interrupt latency
# * problems in a particular system configuration.
# *
# * Devices that have more than one interrupt of the same
# * type should use multiple structures.
# */
#
##define	KSTAT_INTR_HARD			0
##define	KSTAT_INTR_SOFT			1
##define	KSTAT_INTR_WATCHDOG		2
##define	KSTAT_INTR_SPURIOUS		3
##define	KSTAT_INTR_MULTSVC		4
#
##define	KSTAT_NUM_INTRS			5
#
#typedef struct kstat_intr {
#	uint_t	intrs[KSTAT_NUM_INTRS];	/* interrupt counters */
#} kstat_intr_t;

KSTAT_INTR_HARD = 0
KSTAT_INTR_SOFT = 1
KSTAT_INTR_WATCHDOG = 2
KSTAT_INTR_SPURIOUS = 3
KSTAT_INTR_MULTSVC = 4
KSTAT_NUM_INTRS = 5

class kstat_intr(C.Structure):
    _fields_ = [
        ('intrs', KSTAT_NUM_INTRS * C.c_uint)
    ]

kstat_intr_p = C.POINTER(kstat_intr)

#/*
# * Event timer statistics - cumulative elapsed time and number of events.
# *
# * Updates to these fields are performed implicitly by calls to
# * kstat_timer_start() and kstat_timer_stop().
# */
#
#typedef struct kstat_timer {
#	char		name[KSTAT_STRLEN];	/* event name */
#	uchar_t		resv;			/* reserved */
#	u_longlong_t	num_events;		/* number of events */
#	hrtime_t	elapsed_time;		/* cumulative elapsed time */
#	hrtime_t	min_time;		/* shortest event duration */
#	hrtime_t	max_time;		/* longest event duration */
#	hrtime_t	start_time;		/* previous event start time */
#	hrtime_t	stop_time;		/* previous event stop time */
#} kstat_timer_t;

class kstat_timer(C.Structure):
    _fields_ = [
        ('name', kstat_string),
        ('resv', C.c_ubyte),
        ('num_events', C.c_ulonglong),
        ('elapsed_time', hrtime_t),
        ('min_time', hrtime_t),
        ('max_time', hrtime_t),
        ('start_time', hrtime_t),
        ('stop_time', hrtime_t),
    ]

kstat_timer_p = C.POINTER(kstat_timer)


_libkstat = C.CDLL('libkstat.so.1')

kstat_ctl_p = C.POINTER(kstat_ctl)

kstat_open = _libkstat.kstat_open
kstat_open.argtypes = []
kstat_open.restype = kstat_ctl_p


kstat_close = _libkstat.kstat_close
kstat_close.argtypes = [kstat_ctl_p]


kstat_read = _libkstat.kstat_read
kstat_read.argtypes = [kstat_ctl_p, kstat_p, C.c_void_p]
kstat_read.restype = kid_t


kstat_write = _libkstat.kstat_write
kstat_write.argtypes = [kstat_ctl_p, kstat_p, C.c_void_p]
kstat_write.restype = kid_t


kstat_chain_update = _libkstat.kstat_chain_update
kstat_chain_update.argtypes = [kstat_ctl_p]
kstat_chain_update.restype = kid_t


kstat_lookup = _libkstat.kstat_lookup
kstat_lookup.argtypes = [kstat_ctl_p, C.c_char_p, C.c_int, C.c_char_p]
kstat_lookup.restype = kstat_p


kstat_data_lookup = _libkstat.kstat_data_lookup
kstat_data_lookup.argtypes = [kstat_p]
kstat_data_lookup.restype = C.c_void_p

