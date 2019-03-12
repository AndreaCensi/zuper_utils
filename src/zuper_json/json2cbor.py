import json
import select
import time
import traceback
from json import JSONDecodeError

import cbor2

from zuper_json.json_utils import decode_bytes_before_json_deserialization, encode_bytes_before_json_serialization
from . import logger

__all__ = [
    'read_cbor_or_json_objects',
    'json2cbor_main',
    'cbor2json_main',
]


def json2cbor_main():
    fo = open('/dev/stdout', 'wb')
    fi = open('/dev/stdin', 'rb')
    for j in read_cbor_or_json_objects(fi):
        c = cbor2.dumps(j)
        fo.write(c)
        fo.flush()


def cbor2json_main():
    fo = open('/dev/stdout', 'wb')
    fi = open('/dev/stdin', 'rb')
    for j in read_cbor_or_json_objects(fi):
        j = encode_bytes_before_json_serialization(j)
        ob = json.dumps(j)
        ob = ob.encode('utf-8')
        fo.write(ob)
        fo.write(b'\n')
        fo.flush()


def read_cbor_or_json_objects(f, timeout=None):
    """ Reads cbor or line-separated json objects from the binary file f."""
    while True:
        try:
            ob = read_next_either_json_or_cbor(f, timeout=timeout)
            yield ob
        except StopIteration:
            break
        except TimeoutError:
            raise


def read_next_either_json_or_cbor(f, timeout=None, waiting_for: str = None):
    """ Raises StopIteration if it is EOF.
        Raises TimeoutError if over timeout"""
    fs = [f]
    t0 = time.time()
    intermediate_timeout = 3.0
    while True:
        readyr, readyw, readyx = select.select(fs, [], fs, intermediate_timeout)
        if readyr:
            break
        elif readyx:
            logger.warning('Exceptional condition on input channel %s' % readyx)
        else:
            delta = time.time() - t0
            if (timeout is not None) and (delta > timeout):
                msg = 'Timeout after %.1f s.' % delta
                logger.error(msg)
                raise TimeoutError(msg)
            else:
                msg = 'I have been waiting %.1f s.' % delta
                if timeout is None:
                    msg += ' I will wait indefinitely.'
                else:
                    msg += ' Timeout will occurr at %.1f s.' % timeout
                if waiting_for:
                    msg += '\n' + waiting_for
                logger.warning(msg)

    first = f.peek(1)[:1]
    if len(first) == 0:
        msg = 'Detected EOF on %s.' % f
        if waiting_for:
            msg += ' ' + waiting_for
        raise StopIteration(msg)

    # logger.debug(f'first char is {first}')
    if first in [b' ', b'\n', b'{']:
        line = f.readline()
        line = line.strip()
        if not line:
            msg = 'Read empty line. Re-trying.'
            logger.warning(msg)
            return read_next_either_json_or_cbor(f)
        # logger.debug(f'line is {line!r}')
        try:
            j = json.loads(line)
        except JSONDecodeError:
            msg = f'Could not decode line {line!r}: {traceback.format_exc()}'
            logger.error(msg)
            return read_next_either_json_or_cbor(f)
        j = decode_bytes_before_json_deserialization(j)
        return j

    else:

        j = cbor2.load(f)
        return j
