from datetime import datetime
from flask import g, abort


class Model:
    def tablename(self):
        return self.Meta.table

    def non_auto_fields(self):
        return [f for f in self.Meta.fields if f not in self.Meta.auto_fields]

    def __iter__(self):
        return (getattr(self, col) for col in self.non_auto_fields())

    def insert(self, cursor=None):
        if cursor is None:
            cursor = g.cursor
        query = 'INSERT INTO %s (%s) VALUES (%s)' % (
            self.tablename(),
            ','.join(self.non_auto_fields()),
            ','.join(['%s'] * len(self.non_auto_fields()))
        )

        cursor.execute(query, list(self))
        if self.Meta.pk in self.Meta.auto_fields:
            cursor.execute("SELECT LASTVAL() FROM %s" % self.tablename())
            pk = cursor.fetchone()[0]
            setattr(self, self.Meta.pk, pk)

    def update(self, cursor=None):
        if cursor is None:
            cursor = g.cursor
        params = ', '.join(["{}=%s".format(field) for field in self.non_auto_fields()])
        cursor.execute(
            "UPDATE %s SET %s WHERE %s=%%s" % (self.tablename(), params, self.Meta.pk),
            list(self) + [self.pk]
        )

    @property
    def pk(self):
        return getattr(self, self.Meta.pk)

    @classmethod
    def from_dict(klass, d, is_top=True):
        our_fields = {
            k.split(".")[-1]: v for k, v in d.items()
            if k.startswith(klass.tablename(klass) + ".") or '.' not in k and is_top
        }
        instance = klass(**our_fields)
        for submodel in klass.Meta.foreign_models:
            try:
                submodel_instance = submodel.from_dict(d, is_top=False)
            except Exception as e:
                submodel_instance = None
                print(e)
            setattr(instance, submodel.__name__.lower(), submodel_instance)

        return instance

    @classmethod
    def star(klass):
        return ','.join(['{0}.{1} AS "{0}.{1}"'.format(klass.Meta.table, col) for col in klass.Meta.fields])


class User(Model):
    def __init__(self, id=None, username=None, email=None, password=None, created=None):
        self.id = int(id) if id is not None else None
        self.username = username
        self.email = email
        self.password = password
        if created is None:
            created = datetime.now()
        self.created = created

    def is_authenticated(self):
        return True

    class Meta:
        fields = ['id', "username", "email", "password", "created"]
        auto_fields = ['id']
        pk = 'id'
        table = 'users'
        foreign_models = []


class AnonymousUser:
    def is_authenticated(self):
        return False

    @property
    def is_admin(self):
        return False

    @property
    def id(self):
        return -1


class Task(Model):
    def __init__(self, id=None, text=None, created=None, user_id=None):
        self.id = int(id) if id is not None else None
        self.text = text
        if created is None:
            created = datetime.now()
        self.created = created
        self.user_id = user_id

    class Meta:
        fields = ['id', 'text', 'created', 'user_id']
        auto_fields = ['id']
        pk = 'id'
        table = 'task'
        foreign_models = [User]


def get_or_404(query, params, model):
    g.cursor.execute(query, params)
    row = g.cursor.fetchone()
    if row is None:
        return abort(404)
    return model.from_dict(row)


def list_of(query, params, model):
    g.cursor.execute(query, params)
    rows = g.cursor.fetchall()

    def map_to_model(r):
        m = model.from_dict(r)
        m.extra = r
        return m
    return [map_to_model(r) for r in rows]
