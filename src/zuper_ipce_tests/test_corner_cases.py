from typing import Any, ClassVar, Dict, Generic, List, NewType, Optional, Sequence, Set, Tuple, Type, TypeVar, Union

import yaml
from nose.tools import assert_equal, raises

from zuper_ipce import logger
from zuper_ipce.conv_ipce_from_object import ipce_from_object
from zuper_ipce.conv_ipce_from_typelike import ipce_from_typelike
from zuper_ipce.conv_object_from_ipce import object_from_ipce
from zuper_ipce.conv_typelike_from_ipce import typelike_from_ipce
from zuper_ipce_tests.test_utils import (NotEquivalent, assert_equivalent_types, assert_object_roundtrip,
                                         assert_type_roundtrip)
from zuper_typing import dataclass
from zuper_typing.annotations_tricks import (get_NewType_arg, get_NewType_name, get_NewType_repr, is_Any, is_NewType,
                                             is_Type, name_for_type_like)
from zuper_typing.my_dict import get_CustomSet_arg, get_ListLike_arg, make_set
from zuper_typing.subcheck import can_be_used_as2
from zuper_typing_tests.test_utils import known_failure


def test_corner_cases01():
    assert None is object_from_ipce(None, {}, {}, expect_type=Optional[int])


def test_corner_cases02():
    assert 2 == object_from_ipce(2, {}, {}, expect_type=Optional[int])


def test_corner_cases03():
    assert None is object_from_ipce(None, {}, {}, expect_type=None)


def test_corner_cases04():
    ipce_from_object({1: 2}, {}, suggest_type=None)


def test_corner_cases05():
    ipce_from_object(12, {}, suggest_type=Optional[int])


@raises(ValueError)
def test_corner_cases09():
    ipce_from_typelike(None, {})


@raises(ValueError)
def test_property_error():
    @dataclass
    class MyClass32:
        a: int

    ok = can_be_used_as2(str, int, {})
    assert not ok.result

    # noinspection PyTypeChecker
    ob = MyClass32('not an int')
    # ipce_to_object(ob, {}, {}, expect_type=MyClass32)
    res = ipce_from_object(ob, {}, {})
    # print(yaml.dump(res))


@raises(NotImplementedError)
def test_not_know():
    class C:
        pass

    ipce_from_object(C(), {}, {})


@raises(TypeError)
def test_corner_cases07():
    can0 = can_be_used_as2(int, bool, {})
    assert not can0, can0

    T = Union[bool, str]
    can = can_be_used_as2(int, T, {})
    assert not can, can
    object_from_ipce(12, {}, expect_type=T)


@raises(TypeError)
def test_corner_cases08():
    T = Optional[bool]
    assert not can_be_used_as2(int, T, {}).result
    object_from_ipce(12, {}, expect_type=Optional[bool])


def test_newtype1():
    T = NewType('a', int)
    assert is_NewType(T)
    assert_equal(get_NewType_arg(T), int)
    assert_equal(get_NewType_name(T), 'a')
    assert_equal(get_NewType_repr(T), "NewType('a', int)")
    assert_equal(name_for_type_like(T), "NewType('a', int)")


def test_newtype2():
    T = NewType('a', Any)
    assert is_NewType(T)
    assert is_Any(get_NewType_arg(T))
    assert_equal(get_NewType_repr(T), "NewType('a')")
    assert_equal(name_for_type_like(T), "NewType('a')")


def test_list0():
    v = get_ListLike_arg(list)
    assert is_Any(v)


def test_set0():
    a = get_CustomSet_arg(make_set(int))
    assert a is int


def test_default1():
    @dataclass
    class C:
        a: bool = False

    assert_type_roundtrip(C, {})

    ipce1 = ipce_from_typelike(C, {})
    C2 = typelike_from_ipce(ipce1, {}, {})
    # print(debug_print(C))
    # print(debug_print(C2))
    ipce2 = ipce_from_typelike(C2, {})
    assert ipce1 == ipce2


def test_default2():
    X = TypeVar('X')

    @dataclass
    class C(Generic[X]):
        a: bool = False

    assert_type_roundtrip(C, {})

    ipce1 = ipce_from_typelike(C, {})
    C2 = typelike_from_ipce(ipce1, {}, {})
    # print(debug_print(C))
    print(yaml.dump(ipce1))
    assert ipce1['properties']['a']['default'] == False
    # print(debug_print(C2))
    ipce2 = ipce_from_typelike(C2, {})
    assert ipce1 == ipce2


def test_type1():
    assert_type_roundtrip(type, {})
    assert_object_roundtrip(type, {})


def test_parsing():
    schema_bool = """{$schema: 'http://json-schema.org/draft-07/schema#', type: boolean}"""
    ipce = yaml.load(schema_bool)
    T0 = typelike_from_ipce(ipce, {}, {})
    assert T0 is bool, T0
    T0 = object_from_ipce(ipce, {})
    assert T0 is bool, T0
    a = """\
$schema:
  $id: http://invalid.json-schema.org/M#
  $schema: http://json-schema.org/draft-07/schema#
  __module__: zuper_ipce_tests.test_bool
  description: 'M(a: bool)'
  order: [a]
  properties:
    a: {$schema: 'http://json-schema.org/draft-07/schema#', type: boolean}
  required: [a]
  title: M
  type: object
  __qualname__: misc
a: true
    """
    ipce = yaml.load(a)

    T = typelike_from_ipce(ipce['$schema'], {}, {})
    print(T)
    print(T.__annotations__)
    assert T.__annotations__['a'] is bool, T.__annotations__

    ob = object_from_ipce(ipce, {})


def test_Type1():
    T = Type[int]
    assert is_Type(T)


@raises(TypeError)
def test_error_list1():
    a = [1, 2, 3]
    S = int
    ipce_from_object(a, suggest_type=S)


@raises(TypeError)
def test_error_list2():
    a = [1, 2, 3]
    S = Union[int, str]
    ipce_from_object(a, suggest_type=S)


@raises(TypeError)
def test_error_list2b():
    a = [1, 2, 3]
    S = Union[int, str]
    object_from_ipce(a, {}, {}, expect_type=S)


@raises(TypeError)
def test_error_scalar1():
    a = 's'
    S = Union[int, bool]
    ipce = ipce_from_object(a, suggest_type=S)


@raises(TypeError)
def test_error_scalar2():
    a = 's'
    S = Union[int, bool]
    object_from_ipce(a, {}, {}, expect_type=S)


def test_corner_optional():
    a = {}
    S = Optional[Dict[str, int]]
    object_from_ipce(a, {}, {}, expect_type=S)


@raises(TypeError)
def test_corner_union():
    a = {}
    S = Union[str, int]
    object_from_ipce(a, {}, {}, expect_type=S)


@raises(TypeError)
def test_corner_noclass():
    a = {}

    class S:
        pass

    object_from_ipce(a, {}, {}, expect_type=S)


def test_classvars():
    @dataclass
    class MyConstant:
        a: Any

    @dataclass
    class MyNominal:
        op1: MyConstant
        op2: MyConstant
        nominal = True

    assert_type_roundtrip(MyNominal, {})
    a = MyNominal(MyConstant(1), MyConstant(2))

    assert_object_roundtrip(a, {})


def test_corner_optional_with_default():
    @dataclass
    class MyCD:
        a: Optional[bool] = True

    assert_type_roundtrip(MyCD, {})
    a = MyCD()

    assert_object_roundtrip(a, {})

    ipce = ipce_from_typelike(MyCD, {})
    logger.info('yaml:\n\n' + yaml.dump(ipce))
    assert ipce['properties']['a']['default'] == True
    assert 'required' not in ipce


def test_corner_optional_with_default2():
    @dataclass
    class MyCD2:
        a: bool = True

    assert_type_roundtrip(MyCD2, {})
    a = MyCD2()

    assert_object_roundtrip(a, {})

    ipce = ipce_from_typelike(MyCD2, {})
    logger.info('yaml:\n\n' + yaml.dump(ipce))
    assert ipce['properties']['a']['default'] == True
    assert 'required' not in ipce


def test_sequence():
    a = Sequence[int]
    b = List[int]

    ipce1 = ipce_from_typelike(a, {}, {})
    ipce2 = ipce_from_typelike(b, {}, {})
    assert ipce1 == ipce2


def test_union1():
    @dataclass
    class MyCD3:
        a: Union[int, bool]

    assert_type_roundtrip(MyCD3, {})

    assert_object_roundtrip(MyCD3, {})


def make_class(tl):
    @dataclass
    class MyCD4:
        a: tl

    # MyCD4.__name__ = MyCD4.__qualname__ = 'TestClass' + str(tl)
    return MyCD4


def make_class_default(tl, default):
    @dataclass
    class MyCD4:
        a: tl = default

    # MyCD4.__name__ = MyCD4.__qualname__ = 'TestClass' + str(tl)
    return MyCD4


@raises(NotEquivalent)
def test_not_equal1():
    T1 = Union[int, bool]
    T2 = Union[int, str]
    A = make_class(T1)
    B = make_class(T2)
    assert_equivalent_types(A, B, set())


@raises(NotEquivalent)
def test_not_equal2():
    T1 = Dict[int, bool]
    T2 = Dict[int, str]
    A = make_class(T1)
    B = make_class(T2)
    assert_equivalent_types(A, B, set())


@raises(NotEquivalent)
def test_not_equal3():
    T1 = Dict[str, bool]
    T2 = Dict[int, bool]
    A = make_class(T1)
    B = make_class(T2)
    assert_equivalent_types(A, B, set())


@raises(NotEquivalent)
def test_not_equal4():
    T1 = Set[str]
    T2 = Set[int]
    A = make_class(T1)
    B = make_class(T2)
    assert_equivalent_types(A, B, set())


@raises(NotEquivalent)
def test_not_equal5():
    T1 = List[str]
    T2 = List[int]
    A = make_class(T1)
    B = make_class(T2)
    assert_equivalent_types(A, B, set())


@raises(NotEquivalent)
def test_not_equal6():
    T1 = ClassVar[str]
    T2 = ClassVar[int]
    A = make_class(T1)
    B = make_class(T2)
    print(A.__annotations__)
    print(B.__annotations__)
    assert_equivalent_types(A, B, set())


@raises(NotEquivalent)
def test_not_equal7():
    T1 = ClassVar[str]
    T2 = ClassVar[int]
    assert_equivalent_types(T1, T2, set())


@raises(NotEquivalent)
def test_not_equal8():
    T = bool
    A = make_class_default(T, True)
    B = make_class_default(T, False)

    assert_equivalent_types(A, B, set())


@raises(NotEquivalent)
def test_not_equal9():
    T = Optional[bool]
    A = make_class_default(T, True)
    B = make_class_default(T, False)

    assert_equivalent_types(A, B, set())


@raises(NotEquivalent)
def test_not_equal10():
    T = Optional[bool]
    A = make_class_default(T, None)
    B = make_class_default(T, False)

    assert_equivalent_types(A, B, set())


def test_type():
    X = TypeVar('X')

    @dataclass
    class MyClass(Generic[X]):
        a: X
        XT: ClassVar[Type[X]]

    MyClassInt = MyClass[int]
    print(MyClassInt.__annotations__)
    assert_equal(MyClassInt.XT, int)

    assert_type_roundtrip(MyClass, {})


def test_corner_list1():
    x = [1, 2, 3]
    T = Optional[List[int]]
    ipce_from_object(x, globals_={}, suggest_type=T, with_schema=True)


@raises(TypeError)
def test_corner_list2():
    x = [1, 2, 3]
    T = Dict[str, str]
    ipce_from_object(x, suggest_type=T)


def test_corner_tuple1():
    x = (1, 2, 3)
    T = Optional[Tuple[int, ...]]
    ipce_from_object(x, suggest_type=T)


def test_corner_tuple2():
    x = (1, 'a')
    T = Optional[Tuple[int, str]]
    ipce_from_object(x, suggest_type=T)


@raises(TypeError)
def test_corner_tuple3():
    x = (1, 'a')
    T = Dict[str, str]
    ipce_from_object(x, suggest_type=T)


def test_corner_none3():
    x = None
    T = Any
    ipce_from_object(x, suggest_type=T)

@known_failure
@raises(TypeError)
def test_corner_int3():
    x = 1
    T = Dict[str, str]
    ipce_from_object(x, suggest_type=T)
