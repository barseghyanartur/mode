from typing import AsyncContextManager, Generic
from mode import Service, ServiceT
from mode.services import ServiceBase
from mode.utils.objects import cached_property, iter_mro_reversed
import pytest


class D(Service):
    ...


class C(D):
    ...


class B(C):
    ...


class A(B):
    ...


@pytest.mark.parametrize('cls,stop,expected_mro', [
    (A, Service, [D, C, B, A]),
    (B, Service, [D, C, B]),
    (C, Service, [D, C]),
    (D, Service, [D]),
    (A, object, [
        Generic, AsyncContextManager,
        ServiceT, ServiceBase, Service,
        D, C, B, A,
    ]),
    (A, B, [A]),
    (A, C, [B, A]),
    (A, D, [C, B, A]),
])
def test_iter_mro_reversed(cls, stop, expected_mro):
    assert list(iter_mro_reversed(cls, stop=stop)) == expected_mro


class test_cached_property:

    class X(object):

        @cached_property
        def foo(self):
            return 42

    class X_setter(object):
        _foo = 1

        @cached_property
        def foo(self):
            return self._foo

        @foo.setter
        def foo(self, value):
            self._foo = value
            return value

    class X_deleter(object):
        _foo = 1

        @cached_property
        def foo(self):
            return self._foo

        @foo.deleter
        def foo(self, value):
            assert value == 1
            self._foo = None

    @pytest.fixture()
    def x(self):
        return self.X()

    @pytest.fixture()
    def x_setter(self):
        return self.X_setter()

    @pytest.fixture()
    def x_deleter(self):
        return self.X_deleter()

    def test_get(self, x):
        assert 'foo' not in x.__dict__
        assert x.foo == 42
        assert x.__dict__['foo'] == 42
        assert x.foo == 42

    def test_get_class(self, x):
        assert type(x).foo.__get__(None) is type(x).foo

    def test_get_setter(self, x_setter):
        assert x_setter.foo == 1

    def test_set(self, x):
        assert x.foo == 42
        x.foo = 303
        assert x.foo == 303
        assert x.__dict__['foo'] == 303

    def test_set_setter(self, x_setter):
        assert x_setter.foo == 1
        x_setter.foo = 2
        assert x_setter.foo == 2
        assert x_setter._foo == 2

    def test_del(self, x):
        assert 'foo' not in x.__dict__
        assert x.foo == 42
        assert 'foo' in x.__dict__
        del x.foo
        assert 'foo' not in x.__dict__

    def test_del_deleter(self, x_deleter):
        del x_deleter.foo
        assert x_deleter._foo == 1
        assert x_deleter.foo == 1
        del x_deleter.foo
        assert x_deleter._foo is None
