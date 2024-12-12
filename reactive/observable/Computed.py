from .Reactive import Reactive
from reactive.observer import Watch

class Computed(Reactive):
    def __init__(self, compute):
        super().__init__({"value": None})
        object.__setattr__(self, "_compute", compute)
        object.__setattr__(self, "_compute_watch", Watch(
            lambda: self._update()
        ))

    def __setattr__(self, key, value):
        raise Exception("Computed value cannot be set")
    
    def _update(self):
        try:
            res = self._compute()
            if res != object.__getattribute__(self, '_data')['value']:
                object.__getattribute__(self,'_data')['value'] = res
                self._trigger()
        except Exception as e:
            print(f"Update Error: {e}")