from reactive.shared import current_observers

class ReactiveException(Exception):
    pass

class Reactive:
    def __init__(self, obj):
        try:
            if not isinstance(obj, dict):
                raise ReactiveException("Reactive object must be initialized with a dictionary.")
            object.__setattr__(self, "_data", obj)
            object.__setattr__(self, "_observers", [])
        except ReactiveException as e:
            print(f"Initialization Error: {e}")


    def __getattr__(self, key):
        try:
            if key not in self._data:
                raise KeyError(f"Key '{key}' not found in reactive object.")
            if len(current_observers) > 0:
                current_observer = current_observers[-1]
                self._observers.append(current_observer)
                current_observer._deps.append(self)
            return self._data[key]
        except KeyError as e:
            print(f"Attribute Error: {e}")
            return None

    def __setattr__(self, key, value):
        self._data[key] = value
        self._trigger()

    def _trigger(self):
        try:
            if not self._observers:
                raise ReactiveException("No observers to trigger.")
            for observer in self._observers:
                observer._effect()
        except ReactiveException as e:
            print(f"Trigger Error: {e}")

