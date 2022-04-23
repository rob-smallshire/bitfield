from weakref import WeakKeyDictionary


class BitFieldBase:

    def __init__(self, **kwargs):
        self._validate_arg_names(kwargs)
        #self._validate_arg_values(kwargs)

        for field_name in type(self)._field_widths.keys():
            setattr(self, field_name, 0)

        for keyword, value in kwargs.items():
            setattr(self, keyword, value)

    def _validate_arg_names(self, kwargs):
        mismatched_args = frozenset(kwargs).difference(type(self)._field_widths)
        if len(mismatched_args) != 0:
            raise TypeError(
                "{}.__init__() got unexpected keyword argument{}: {}".format(
                    type(self).__name__,
                    "" if len(mismatched_args) == 1 else "s",
                    ", ".join(
                        repr(arg_name) for arg_name in kwargs
                         if arg_name in mismatched_args
                    )
                )
            )

    # def _validate_arg_values(self, kwargs):
    #     for keyword, value in kwargs.items():
    #         width = type(self)._field_widths[keyword]
    #         min_value = 0
    #         max_value = 2 ** width - 1
    #         if not (min_value <= value <= max_value):
    #             raise ValueError(
    #                 f"{type(self).__name__} field {keyword!r} "
    #                 f"got value {value!r} which is out of "
    #                 f"range {min_value}-{max_value} for a {width}-bit field"
    #             )

    def __int__(self):
        accumulator = 0
        shift = 0
        for name, width in type(self)._field_widths.items():
            value = getattr(self, name)
            accumulator |= value << shift
            shift += width
        return accumulator


    def to_bytes(self):
        v = int(self)
        num_bytes = (sum(self._field_widths.values()) + 7) // 8
        return v.to_bytes(
            length=num_bytes,
            byteorder="little",
            signed=False,
        )


class BitFieldMeta(type):

    def __new__(mcs, name, bases, namespace, **kwargs):
        print(f"  {mcs = }")
        print(f"  {name = }")
        print(f"  {bases = }")
        print(f"  {namespace = }")
        print(f"  {kwargs = }")
        field_widths = namespace.get("__annotations__", {})
        if len(field_widths) == 0:
            raise TypeError(f"{name} with metaclass {mcs.__name__} has no fields")

        for field_name, width in field_widths.items():

            if field_name.startswith("_"):
                raise TypeError(
                    f"{name} field {field_name!r} begins with an underscore"
                )

            if not isinstance(width, int):
                raise TypeError(
                    f"{name} field {field_name!r} has annotation "
                    f"{width!r} that is not an integer"
                )

            if width < 1:
                raise TypeError(
                    f"{name} field {field_name!r} has non-positive "
                    f"field width {width}"
                )


        namespace["_field_widths"] = field_widths

        for field_name, width in field_widths.items():
            namespace[field_name] = BitFieldDescriptor(field_name, width)

        bases = (BitFieldBase,) + bases
        return super().__new__(mcs, name, bases, namespace)


class BitFieldDescriptor:

    def __init__(self, name, width):
        self._name = name
        self._width = width
        self._instance_data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self._instance_data[instance]

    def __set__(self, instance, value):
        min_value = 0
        max_value = 2 ** self._width - 1
        if not (min_value <= value <= max_value):
            raise ValueError(
                f"{type(instance).__name__} field {self._name!r} "
                f"got value {value!r} which is out of "
                f"range {min_value}-{max_value} for a {self._width}-bit field"
            )
        self._instance_data[instance] = value


