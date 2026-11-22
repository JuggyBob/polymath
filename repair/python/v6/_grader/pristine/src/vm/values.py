"""Value helpers shared by the VM and its output layer."""


def truthy(value):
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        return True
    if isinstance(value, list):
        return len(value) != 0
    return True


def format_value(value):
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "[" + ", ".join(repr(item) for item in value) + "]"
    return str(value)


def deep_key(value):
    if value is None:
        return ("null",)
    if value is True:
        return ("bool", True)
    if value is False:
        return ("bool", False)
    if isinstance(value, int):
        return ("int", value)
    if isinstance(value, str):
        return ("str", value)
    if isinstance(value, list):
        return ("array", tuple(deep_key(item) for item in value))
    return ("other", repr(value))


def equal(left, right):
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(
            equal(a, b) for a, b in zip(left, right))
    if type(left) is not type(right):
        return False
    return left == right
