"""
Data Model base class
"""


class BaseDataModel:
    _type = 'BaseDataModel'

    def __init__(self, data=None):
        self._data = data

    def read(self):
        """
        The child class should override this method

        Returns
        -------
        Content of the _data argument

        """
        return self._data

    def to_dict(self):
        return {'type': self._type, 'data': self._data}
