import functools
import inspect

class computed_property:
    def __init__(self, *dependencies):
        self.dependencies = set(dependencies)

    def __call__(self, func):
        self.func = func
        self.__doc__ = func.__doc__

        attr_name = f'_cached_{func.__name__}'
        deps_name = f'_deps_{func.__name__}'

        @property
        @functools.wraps(func)
        def wrapper(instance):
            # inicializa armazenamento se necessário
            if not hasattr(instance, '__computed_cache__'):
                instance.__computed_cache__ = {}
                instance.__computed_deps__ = {}

            # pega o cache e os valores anteriores das dependências
            cache = instance.__computed_cache__
            prev_deps = instance.__computed_deps__.get(func.__name__, {})

            # captura os valores atuais das dependências
            current_deps = {
                dep: getattr(instance, dep, object())
                for dep in self.dependencies
            }

            # compara com o estado anterior
            if func.__name__ in cache and current_deps == prev_deps:
                return cache[func.__name__]

            # atualiza e computa
            value = func(instance)
            cache[func.__name__] = value
            instance.__computed_deps__[func.__name__] = current_deps
            return value

        self._prop = wrapper
        return self

    def setter(self, func):
        self._prop = self._prop.setter(func)
        return self

    def deleter(self, func):
        self._prop = self._prop.deleter(func)
        return self

    def __get__(self, instance, owner=None):
        return self._prop.__get__(instance, owner)

    def __set__(self, instance, value):
        return self._prop.__set__(instance, value)

    def __delete__(self, instance):
        return self._prop.__delete__(instance)

    def __set_name__(self, owner, name):
        self._prop.__set_name__(owner, name)
