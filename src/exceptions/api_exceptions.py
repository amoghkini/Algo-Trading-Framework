class APIException(Exception):
    pass


class DataException(Exception):
    pass


class DatabaseWriteError(Exception):
    pass


class DuplicateEntryError(Exception):
    pass