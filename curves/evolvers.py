from curves.base import shift_attraction_curve


def constant(person):
    return person.attraction_curve


def cycle_decreasing(decrement):
    def func(person, _sim):
        return shift_attraction_curve(person.attraction_curve, -decrement)

    return func
