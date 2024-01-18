import copy

class TweenChange:
    def __init__(self, field_name, start_value, end_value):
        self.field_name = field_name
        self.start_value = start_value
        self.end_value = end_value
   
    field_name: str 
    start_value: float
    end_value: float


def produce_tweens(start, end, steps: int = 10):
    # Assumptions:
    #   start.__class__ == end.__class__
    #   field types are floats
    #   linear interpolation between start and end values for each field that has a delta

    # First, calculate all the fields that need tweenin
    changes: list[(TweenChange, delta)] = []
    for field_name in start.__dict__.keys():
        start_value = getattr(start, field_name)
        end_value = getattr(end, field_name)
        if start_value != end_value:
            delta = (end_value - start_value) / (steps - 1)
            changes.append((TweenChange(field_name, start_value, end_value), delta))

    results = []
    for step in range(steps):
        if step == 0:
            results.append(copy.deepcopy(start))
        elif step == steps - 1:
            results.append(copy.deepcopy(end))
        else:
            new_tween = copy.deepcopy(start)
            # linear interpolation
            for change, delta in changes:
                setattr(
                    new_tween,
                    change.field_name,
                    getattr(start, change.field_name) + step * delta,
                )
            results.append(new_tween)
    return results


if __name__ == "__main__":

    class TestValue:
        a: float = 0.0
        b: float = 0.0
        c: float = 0.0

    tv1 = TestValue()
    tv2 = TestValue(10.0, 5.0, 0.0)

    result = produce_tweens(tv1, tv2, 11)
    print(result)
