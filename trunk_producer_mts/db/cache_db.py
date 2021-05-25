import sqlite3

import datetime


class Trunk:

    def __init__(self, provider, obj, trunk_username, trunk_name,
                 trunk_password, lines, phone=None, attributes=None):
        self.trunk_name = trunk_name
        self.trunk_username = trunk_username
        self.provider = provider
        self.obj = obj
        self.trunk_password = trunk_password
        self.phone = phone
        self.active = bool(self.phone)
        self.attributes = attributes
        self.updated = str(datetime.datetime.utcnow())
        self.lines = lines


class CacheDB:

    def __init__(self):
        self.con = sqlite3.connect("cache.db")
        self.cur = self.con.cursor()
        self.cur = self.cur.execute("create table if not exists trunkcache (provider text, obj text, trunk_name text, trunk_username text, trunk_password text, phone text, active int, attributes json, updated timestamp, lines int)") # noqa
        # self.con.close()

    def compare_rows(self, row, data):
        if (row[5] != data.phone
            or row[6] != data.active
                or row[7] != data.attributes):
            return 0
        return 1

    def check_update(self, data):
        self.cur.execute("select * from trunkcache where trunk_name=:trunk_name", {"trunk_name": data.trunk_name}) # noqa
        row = self.cur.fetchone()
        if not row:
            return self.insert_db(data)
        if not self.compare_rows(row, data):
            return self.update_db(data)
        return 0

    def _check_all(self):
        self.cur.execute("select * from trunkcache")
        row = self.cur.fetchall()
        for i in row:
            print(i)

    def insert_db(self, data):
        test_list = (
            data.provider,
            data.obj,
            data.trunk_name,
            data.trunk_username,
            data.trunk_password,
            data.phone,
            data.active,
            str(data.attributes),
            data.updated,
            data.lines)
        self.cur.execute("insert into trunkcache values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", test_list) # noqa
        self.con.commit()
        return 1

    def update_db(self, data):
        query = """update trunkcache SET phone = ? , active = ? ,attributes = ? , updated = ? where trunk_name = ?""" # noqa
        test_list = (
            data.phone,
            data.active,
            str(data.attributes),
            data.updated,
            data.trunk_name)
        self.cur.execute(query, test_list)
        self.con.commit()
        return 1

# db = CacheDB()

# some_data = {"provider" : "megafon","obj" : "some_obj",
# "trunk_name" : "1admin1", "trunk_username" : "1admin1",
# "trunk_password": "some_pass", "phone" : "99998888",
# "attributes": "testaatr", "lines": 2}
# some_data = Trunk(**some_data)
# db.insert_db(some_data)
# db.check_update(some_data)
# db._check_all()
