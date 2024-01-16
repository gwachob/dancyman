import dataclasses
from dataclasses import dataclass
from collections import namedtuple


@dataclass
class TweenChange:
    field: dataclasses.Field
    start_value: float
    end_value: float


def produce_tweens(start, end, steps: int = 10):
    # Assumptions:
    #   start.__class__ == end.__class__
    #   field types are floats
    #   linear interpolation between start and end values for each field that has a delta

    # First, calculate all the fields that need tweenin
    changes: list[(TweenChange, delta)] = []
    for field in dataclasses.fields(start):
        start_value = getattr(start, field.name)
        end_value = getattr(end, field.name)
        if start_value != end_value:
            delta = (end_value - start_value) / (steps - 1)
            changes.append((TweenChange(field, start_value, end_value), delta))

    results = []
    for step in range(steps):
        if step == 0:
            results.append(dataclasses.replace(start))
        elif step == steps - 1:
            results.append(dataclasses.replace(end))
        else:
            new_tween = dataclasses.replace(start)
            # linear interpolation
            for change, delta in changes:
                setattr(
                    new_tween,
                    change.field.name,
                    getattr(start, change.field.name) + step * delta,
                )
            results.append(new_tween)
    return results


if __name__ == "__main__":

    @dataclass
    class TestValue:
        a: float = 0.0
        b: float = 0.0
        c: float = 0.0

    tv1 = TestValue()
    tv2 = TestValue(10.0, 5.0, 0.0)

    result = produce_tweens(tv1, tv2, 11)
    print(result)
