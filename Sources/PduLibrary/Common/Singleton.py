import threading

_singletons = set()
_lock = threading.RLock()
_lockWhileCreation = threading.RLock()


def _create_instance(cls, args, kwargs):
    _lockWhileCreation.acquire()

    try:
        if cls.b_instantiated():
            return

        instance = cls.__new__(cls)

        try:
            instance.__init__(*args, **kwargs)
        except TypeError as e:
            print(str(e))
            if str(e).find('__init__() takes') != -1:
                raise Exception('Pass __init__ args on first call to get_instance()')
            else:
                raise
        cls.cInstance = instance
        _add(cls)
    finally:
        _lockWhileCreation.release()


def _add(cls):
    _lock.acquire()
    try:
        assert cls not in _singletons
        _singletons.add(cls)
    finally:
        _lock.release()


def _remove(cls):
    _lock.acquire()
    try:
        if cls in _singletons:
            _singletons.remove(cls)
    finally:
        _lock.release()


def release_instances():
    _lock.acquire()
    try:
        for cls in _singletons.copy():
            cls._release_class_instances_for_testing()

            # Try once more to make sure new processes are added while releasing
            len_singletons = len(_singletons)
            if len_singletons > 0:
                for _cls in _singletons.copy():
                    _cls._release_class_instances_for_testing()
                    len_singletons -= 1
                    assert len_singletons == len(_singletons), 'Added a singleton while releasing ' + str(cls)
            assert len(_singletons) == 0, _singletons

    finally:
        _lock.release()


class SingletonMeta(type):
    def __new__(mcs, name, tuple_bases, dct):
        if '__new__' in dct:
            raise Exception('Cannot override __new__ in a Singleton')
        return super(SingletonMeta, mcs).__new__(mcs, name, tuple_bases, dct)

    def __call__(cls, *args, **kwargs):
        raise Exception('Singletons may be instantiated only through getInstances()')


class Singleton(object, metaclass=SingletonMeta):

    cInstance = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._b_instantiated():
            if (args or kwargs) and not hasattr(cls, 'ignoreSubsequent'):
                raise Exception('Singleton already instantiated, but get_instance() called with args')
        else:
            _create_instance(cls, args, kwargs)

        return cls.cInstance

    @classmethod
    def _b_instantiated(cls):

        return 'cInstance' in cls.__dict__

    b_instantiated = _b_instantiated

    @classmethod
    def _release_class_instances_for_testing(cls):
        """
        This is designed for convenience in testing
        Sometimes we want to gt rid of a singleton during testing code
        to see things happening when we call get_instance()

        To really delete the object, all external references needs to be deleted as well.
        """
        try:
            if hasattr(cls.cInstance, '_prepare_to_forget_singleton'):
                cls.cInstance._prepare_to_forget_singleton()
            del cls.cInstance
            _remove(cls)
        except AttributeError:
            for baseClass in cls.__bases__:
                if issubclass(baseClass, Singleton):
                    baseClass._release_class_instances_for_testing()
