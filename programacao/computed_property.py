from typing import Any, Callable, Optional, Type


class computed_property:
    """
    Propriedade computada com cache baseado em dependências.
    Recalcula o valor apenas quando os atributos dependentes mudam.
    """

    def __init__(self, *dependencies: str) -> None:
        self.dependencies: set[str] = set(dependencies)
        self.fget: Optional[Callable[[Any], Any]] = None
        self.fset: Optional[Callable[[Any, Any], None]] = None
        self.fdel: Optional[Callable[[Any], None]] = None
        self.__doc__: Optional[str] = None
        self.attr_name: Optional[str] = None

    def __call__(self, func: Callable[[Any], Any]) -> 'computed_property':
        self.fget = func
        self.__doc__ = func.__doc__
        return self

    def __set_name__(self, owner: Type, name: str) -> None:
        self.attr_name = name

        # Armazena docstring para exibição em help()
        if self.__doc__:
            if not hasattr(owner, '__doc_properties__'):
                owner.__doc_properties__ = {}
            owner.__doc_properties__[name] = self.__doc__

    def __get__(self, instance: Any, owner: Optional[Type] = None) -> Any:
        if instance is None:
            return self  # acesso via classe

        if not hasattr(instance, '__computed_cache__'):
            instance.__computed_cache__ = {}
            instance.__computed_deps__ = {}

        cache: dict[str, Any] = instance.__computed_cache__
        state: dict[str, dict[str, Any]] = instance.__computed_deps__

        current_deps = {
            dep: getattr(instance, dep, object())
            for dep in self.dependencies
        }

        if (self.attr_name in cache and
                state.get(self.attr_name) == current_deps):
            return cache[self.attr_name]

        assert self.fget is not None, f"Getter not defined for '{self.attr_name}'"
        value = self.fget(instance)
        cache[self.attr_name] = value
        state[self.attr_name] = current_deps
        return value

    def __set__(self, instance: Any, value: Any) -> None:
        if self.fset is None:
            raise AttributeError(f"can't set attribute '{self.attr_name}'")
        self.fset(instance, value)

    def __delete__(self, instance: Any) -> None:
        if self.fdel is None:
            raise AttributeError(f"can't delete attribute '{self.attr_name}'")
        self.fdel(instance)

    def setter(self, func: Callable[[Any, Any], None]) -> 'computed_property':
        self.fset = func
        return self

    def deleter(self, func: Callable[[Any], None]) -> 'computed_property':
        self.fdel = func
        return self



from math import sqrt

class Vector:
    def __init__(self, x, y, z, color=None):
        self.x, self.y, self.z = x, y, z
        self.color = color

    @computed_property('x', 'y', 'z')
    def magnitude(self):
        print('Computing magnitude...')
        return sqrt(self.x**2 + self.y**2 + self.z**2)

v = Vector(3, 4, 0)
print(v.magnitude)  # computing...
print(v.magnitude)  # cache
v.y = 8
print(v.magnitude)  # recomputing...

help(Vector)