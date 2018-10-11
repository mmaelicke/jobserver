"""
This is a class implementing the most important CRUD operations to the
MongoDB instance defined in the app.py. Can be inherited by the actual data
models.
"""
from bson import ObjectId
from bson.errors import InvalidId
from flask_pymongo import PyMongo

mongo = PyMongo()


class MongoModel(object):
    mongo = mongo
    collection = None

    def __init__(self, **kwargs):
        self.__dict__['_id'] = None
        self.__dict__['_doc'] = dict()
        self.__dict__['db'] = mongo.db
        for key in kwargs.keys():
#            self._doc[key] = kwargs[key]
            setattr(self, key, kwargs[key])

    @classmethod
    def id_exists(cls, _id):
        if not isinstance(_id, ObjectId):
            _id = ObjectId(_id)

        # check if this id already exists
        return cls.mongo.db[cls.collection].count_documents({'_id': _id}) > 0

    @property
    def id(self):
        return self._id

    def create(self):
        # prepare the dict
        d = self._doc

        # check if instance is created with id
        # this might cause an error
        if self.id is not None:
            d['_id'] = self.id

        new_id = self.db[self.collection].insert_one(d).inserted_id

        # set the new id, if it is new
        self._id = new_id

    def update(self, data={}):
        # update this instance if necessary
        self._doc.update(data)

        # prepare the dict
        d = self._doc

        self.db[self.collection].update_one(
            {'_id': self.id},
            {'$set': d}
        )

    def save(self):
        if self.id is not None:
            self.update()
        else:
            self.create()

    def to_dict(self, stringify=False):
        # load the document
        d = self._doc

        # append id if set
        if self.id is not None:
            d.update({'_id': self.id})

        # stringify all values
        def _stringify(val):
            if isinstance(val, dict):
                return {k: _stringify(v) for k, v in val.items()}
            return str(val)

        if stringify:
            return _stringify(d)
        else:
            return d

    def delete(self):
        res = self.db[self.collection].delete_one({'_id': self.id})

        if res.deleted_count == 0:
            return False
        else:
            return True

    @classmethod
    def get(cls, _id, filter={}, fields=None):
        if cls.collection is None:
            raise ValueError('No collection set on child class')

        if not isinstance(_id, ObjectId):
            try:
                _id = ObjectId(_id)
            except InvalidId:
                return None

        # update filter
        filter.update({'_id': _id})

        res = cls.mongo.db[cls.collection].find_one(filter, fields)
        if res is None:
            return None

        return cls(**res)

    @classmethod
    def get_all(cls, filter={}, fields=None):
        if cls.collection is None:
            raise ValueError('No collection set on child class')

        # load all docs in this collection
        all_docs = cls.mongo.db[cls.collection].find(filter, fields)

        return [cls(**doc) for doc in all_docs]

    def __getattr__(self, item):
        return self._doc.get(item, None)

    def __setattr__(self, key, value):
        if key.lower() == '_id' or key.lower() == 'id':
            if isinstance(value, ObjectId):
                self.__dict__['_id'] = value
            else:
                self.__dict__['_id'] = ObjectId(value)
        else:
            self._doc.update({key: value})

    def __delattr__(self, item):
        if item.lower() == '_id' or item.lower() == 'id':
            raise ValueError('This would delete the whole object.' +
                             ' Please use the delete method')
        else:
            del self._doc[item]

    @classmethod
    def delete_all(cls, filter={}):
        jobs = cls.get_all(filter=filter)

        # total operations
        tot = [job.delete() for job in jobs]

        # successful operation
        suc = [_ for _ in tot if _]

        return len(suc), len(tot)
