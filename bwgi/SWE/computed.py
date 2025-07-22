class computed_property:
    def __init__(self, *dependencies):
        self.dependencies = set(dependencies)
        self.fget = None
        self.fset = None
        self.fdel = None
        self.__doc__ = None
        self.attr_name = None

    def __call__(self, func):
        self.fget = func
        self.__doc__ = func.__doc__
        return self

    def __set_name__(self, owner, name):
        self.attr_name = name

        # Atribui docstring na classe para aparecer em help(obj)
        if self.__doc__ and not hasattr(owner, '__doc_properties__'):
            owner.__doc_properties__ = {}
        if self.__doc__:
            owner.__doc_properties__[name] = self.__doc__

    def __get__(self, instance, owner=None):
        if instance is None:
            return self  # acesso via classe

        if not hasattr(instance, '__computed_cache__'):
            instance.__computed_cache__ = {}
            instance.__computed_deps__ = {}

        cache = instance.__computed_cache__
        state = instance.__computed_deps__

        current_deps = {
            dep: getattr(instance, dep, object())
            for dep in self.dependencies
        }

        if self.attr_name in cache and state.get(self.attr_name) == current_deps:
            return cache[self.attr_name]

        value = self.fget(instance)
        cache[self.attr_name] = value
        state[self.attr_name] = current_deps
        return value

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError(f"can't set attribute '{self.attr_name}'")
        self.fset(instance, value)

    def __delete__(self, instance):
        if self.fdel is None:
            raise AttributeError(f"can't delete attribute '{self.attr_name}'")
        self.fdel(instance)

    def setter(self, func):
        self.fset = func
        return self

    def deleter(self, func):
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