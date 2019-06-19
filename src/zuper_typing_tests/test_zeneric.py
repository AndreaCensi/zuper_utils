from typing import ClassVar, Type, TypeVar, Generic

from nose.tools import raises, assert_equal

from zuper_typing.constants import enable_type_checking
from zuper_typing.annotations_tricks import is_ClassVar, get_ClassVar_arg, is_Type, get_Type_arg
from zuper_typing.monkey_patching_typing import my_dataclass as dataclass
from zuper_typing.subcheck import can_be_used_as2


def test_basic():
    U = TypeVar('U')

    T = Generic[U]

    print(T.mro())

    assert_equal(T.__name__, 'Generic[U]')
    print('inheriting C(T)')

    @dataclass
    class C(T):
        ...

    print(C.mro())

    assert_equal(C.__name__, 'C[U]')
    print('subscribing C[int]')
    D = C[int]

    assert_equal(D.__name__, 'C[int]')


@raises(TypeError)
def test_dataclass_can_preserve_init():
    X = TypeVar('X')

    @dataclass
    class M(Generic[X]):
        x: int

    M(x=2)


def test_isClassVar():
    X = TypeVar('X')

    A = ClassVar[Type[X]]
    assert is_ClassVar(A)
    assert get_ClassVar_arg(A) == Type[X]


def test_isType():
    X = TypeVar('X')

    A = Type[X]
    # print(type(A))
    # print(A.__dict__)
    assert is_Type(A)
    assert get_Type_arg(A) == X

    # assert_object_roundtrip(x, {})


@raises(TypeError)
def test_check_bound1():
    @dataclass
    class Animal:
        a: int

    assert not can_be_used_as2(int, Animal, {}).result
    assert not issubclass(int, Animal)

    X = TypeVar('X', bound=Animal)

    @dataclass
    class CG(Generic[X]):
        a: X

    _ = CG[int]  # boom, int !< Animal


@raises(TypeError)
def test_check_bound2():
    @dataclass
    class Animal:
        a: int

    class Not:
        b: int

    assert not can_be_used_as2(Not, Animal, {}).result

    X = TypeVar('X', bound=Animal)

    @dataclass
    class CG(Generic[X]):
        a: X

    _ = CG[Not]  # boom, Not !< Animal

    # assert_type_roundtrip(CG, {})
    # assert_type_roundtrip(CG[int], {})
    #


if enable_type_checking:
    @raises(ValueError, TypeError)  # typerror in 3.6
    def test_check_value():
        @dataclass
        class CG(Generic[()]):
            a: int

        CG[int](a="a")

if __name__ == '__main__':
    test_check_bound1()