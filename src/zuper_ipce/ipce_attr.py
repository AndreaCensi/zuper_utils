from typing import List


# IPCE_REPR_ATTR = '__ipce_


class SchemaCache:
    key2schema = {}


def make_key(x):
    k0 = id(type(x))
    k1 = getattr(x, '__qualname__', None)
    k2 = getattr(x, '__name__', None)
    k2b = getattr(x, '__dict_type__', None)
    k2c = getattr(x, '__set_type__', None)
    k2d = getattr(x, '__list_type__', None)
    k3 = id(x)
    # if hasattr(x, '__dict__'):
    #     k4 = id(x.__dict__)
    # else:
    #     k4 = None
    # try:
    #     k5 = x.__hash__()
    # except:
    #     k5 = None
    # k5 = None
    k = (k0, k1, k2, k2b, k2c, k2d, k3)
    return k


# def make_key_ipce(x, processing: List[str]):
#     k = make_key(x)
#     k += tuple(processing)
#     return k

# def has_ipce_repr_attr(x: Any, processing: List[str]):
#     k = make_key_ipce(x, processing)
#     # logger.debug(k)
#     return k in SchemaCache.key2schema
#
#
# def get_ipce_repr_attr(x: Any, processing: List[str]):
#     k = make_key_ipce(x, processing)
#     res = SchemaCache.key2schema[k]
#     # logger.debug(f'Found schema cache for {x} processing = {processing}')
#     return res
#
#
# def set_ipce_repr_attr(x: object, processing: List[str], a):
#     k = make_key_ipce(x, processing)
#     if k in SchemaCache.key2schema:
#         prev = SchemaCache.key2schema[k]
#         if prev != a:
#             msg = f'INCONSISTENT setting of schema cache for {x}:\n'
#             # msg += side_by_side([yaml.dump(prev)[:400], ' ', yaml.dump(a)[:400]])
#             raise ValueError(msg)
#         else:
#             pass
#
#             # logger.debug(f'Double Setting schema cache for {x} processing = {processing}')
#     else:
#         # logger.debug(f'Setting schema cache for {x}  processing = {processing}\n{k}')
#         SchemaCache.key2schema[k] = a
#
