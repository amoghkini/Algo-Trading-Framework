# Reference of singletone class. Refer https://www.youtube.com/watch?v=Wiw7oOgBjFs&t=107s at 12:30 for the same.

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
