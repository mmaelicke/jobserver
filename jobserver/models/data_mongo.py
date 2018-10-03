"""
Data model for data stored in the MongoDB
"""
from datetime import datetime as dt

import pandas as pd

from .data import BaseDataModel
from .mongo import MongoModel


class DataMongo(MongoModel, BaseDataModel):
    collection = 'data'

    def __init__(self, data=None, datatype=None, **kwargs):
        super(DataMongo, self).__init__(**kwargs)
        self.data = data
        self.datatype = datatype

    def read(self):
        """Return the file content

        The function will switch the self.type property and cast the
        self.data content according to the type into a corresponding Python
        type. If the type is None, not known or not supported, the self.data
        content will be returned as JSON.

        Returns
        -------

        """
        if self.datatype is None:
            return self.data
        elif self.datatype == 'timeseries' or self.datatype == 'dataframe':
            return pd.DataFrame(self.data)
        else:
            return self.data

    def create(self):
        if self.created is None:
            self.created = dt.utcnow()
        super(DataMongo, self).create()

    def update(self, data={}):
        self.edited = dt.utcnow()
        super(DataMongo, self).update(data=data)
