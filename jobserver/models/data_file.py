"""
Model for handling data files
"""
import os
from glob import glob

import pandas as pd
from flask import current_app

from jobserver.models.data import BaseDataModel


class DataFile(BaseDataModel):
    allowed_mime = ['.csv', '.dat', '.txt']
    _type = 'datafile'

    @classmethod
    def storage(cls):
        if not hasattr(cls, 'store'):
            setattr(cls, 'store', current_app.config.get('DATA_PATH'))
        return getattr(cls, 'store')

    def __init__(self, path, strict=True):
        super(DataFile, self).__init__()
        self.path = path

        if strict and not DataFile.is_allowed(path):
            raise ValueError('The file type is not allowed. Use {}.'.format(
                DataFile.allowed_mime
            ))

    @classmethod
    def file_exists(cls, path):
        return os.path.exists(path)

    @classmethod
    def name_exists(cls, name):
        return os.path.exists(os.path.join(DataFile.storage(), name))

    @classmethod
    def is_allowed(cls, path):
        return os.path.splitext(path)[1].lower() in cls.allowed_mime

    @classmethod
    def find_all(cls):
        file_list = glob(os.path.join(DataFile.storage(), '*'))

        # filter
        return [DataFile(path=f) for f in file_list if cls.is_allowed(f)]

    @classmethod
    def get(cls, path, strict=True):
        return DataFile(path=path, strict=strict)

    @classmethod
    def get_from_name(cls, name):
        path = os.path.join(DataFile.storage(), name)
        if DataFile.file_exists(path=path):
            return DataFile(path=path)
        else:
            return None

    @classmethod
    def upload(cls, file_name, file_pointer):
        path = os.path.join(DataFile.storage(), file_name)
        file_pointer.save(path)

        return DataFile(path=path)

    def read(self):
        """
        Only development. Does only work for pandas DataFrames

        Returns
        -------

        """
        return pd.read_csv(self.path)

    def name(self):
        return os.path.basename(self.path)

    def size(self):
        # https://stackoverflow.com/questions/14996453/python-libraries-to-calculate-human-readable-filesize-from-bytes
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        size = os.path.getsize(self.path)
        i = 0
        while size >= 1024 and i < len(suffixes) - 1:
            size /= 1024.
            i += 1
        fmt = ('%.2f' % size).rstrip('0').rstrip('.')
        return '%s %s' % (fmt, suffixes[i])

    def delete(self):
        os.remove(self.path)

    def to_dict(self):
        return {
            'type': self._type,
            'path': self.path,
            'name': self.name(),
            'size': self.size()
        }
