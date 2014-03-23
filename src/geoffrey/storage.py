from bsddb3 import db


class Storage:
    def __init__(self, path):
        self.path = path

        self.env = db.DBEnv()
        self.events = db.DB(self.env)
        self.status = db.DB(self.env)

        self.cursors = []

    def __enter__(self):
        self.env.open(self.path,
                      db.DB_INIT_MPOOL | db.DB_CREATE | db.DB_THREAD)
        self.events.open('events', dbtype=db.DB_RECNO, flags=db.DB_CREATE)
        self.status.open('status', dbtype=db.DB_BTREE, flags=db.DB_CREATE)
        return self

    def __exit__(self, type, value, tb):
        for cursor in self.cursors:
            cursor.close()
        self.status.close()
        self.events.close()
        self.env.close()
