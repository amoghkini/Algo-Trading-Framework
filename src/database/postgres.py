import psycopg2
from typing import Any, Dict, List


class PostgresSql:

    conn = None
    cur = None
    conf = None

    def __init__(self, **kwargs) -> None:
        self.conf = kwargs
        self.conf['host'] = kwargs.get("host", "127.0.0.1")
        self.conf['port'] = kwargs.get("port", 5432)
        self.conf['db'] = kwargs.get("db")
        self.conf['user'] = kwargs.get("user")
        self.conf['password'] = kwargs.get("password")
        self.connect()

    def connect(self) -> None:
        try:
            self.conn = psycopg2.connect(host=self.conf.get('host'),
                                         database=self.conf.get('db'),
                                         user=self.conf.get('user'),
                                         password=self.conf.get('password'),
                                         port=self.conf.get('port'))
            self.cur = self.conn.cursor()

        except Exception as e:
            print("Postgres connection failed")
            raise ValueError("Connection to the database failed.",e)

    def insert(self,
               schema: str,
               table: str,
               data) -> int:
        query = self.__serialize_insert(data)
        sql = "INSERT INTO %s.%s (%s) VALUES(%s)" % (
            schema, table, query[0], query[1])
        return self.query(sql, tuple(data.values())).rowcount

    def get_one(self,
                schema: str,
                table: str = None,
                fields='*',
                where=None,
                order=None,
                limit=(1, 0)) -> Dict:
        cur = self.__select(schema, table, fields, where, order, limit)
        result = cur.fetchone()
        row = None
        if result:
            fields = [f[0] for f in cur.description]
            row = zip(fields, result)
            return dict(row)
        else:
            return None

    def get_all(self,
                schema: str,
                table: str=None,
                fields='*',
                where=None,
                order=None,
                limit=None) -> List:
        cur = self.__select(schema, table, fields, where, order, limit)
        result = cur.fetchall()

        rows = None
        if result:
            fields = [f[0] for f in cur.description]
            rows = [dict(zip(fields, r)) for r in result]
        return rows

    def update(self, 
               schema: str, 
               table: str, 
               data, 
               where=None) -> int:
        query = self.__serialize_update(data)

        sql = "UPDATE %s.%s SET %s" % (schema, table, query)

        if where and len(where) > 0:
            sql += " WHERE %s" % where[0]
        values = tuple(data.values())

        return self.query(sql, values + where[1] if where and len(where) > 1 else values).rowcount

    def insert_or_update(self,
                         schema: str,
                         table: str,
                         data: Dict,
                         keys: str) -> int:
        insert_data = data.copy()

        data = {k: data[k] for k in data if k not in keys}

        insert = self.__serialize_insert(insert_data)
        update = self.__serialize_update(data)

        sql = "INSERT INTO %s.%s (%s) VALUES(%s) ON CONFLICT (%s) DO UPDATE SET %s" % (
            schema, table, insert[0], insert[1], keys, update)

        return self.query(sql, tuple(insert_data.values()) + tuple(data.values())).rowcount
        
    def __serialize_insert(self,
                           data: Dict[str, Any]) -> List[str]:
        keys = ",".join(data.keys())
        vals = ",".join(["%s" for k in data])
        return [keys, vals]

    def __select(self,
                 schema=None,
                 table=None,
                 fields=(),
                 where=None,
                 order=None,
                 limit=None):
        sql = "SELECT %s FROM %s.%s" % (",".join(fields), schema, table)
        # where conditions
        if where and len(where) > 0:
            sql += " WHERE %s" % where[0]

        # order
        if order:
            sql += " ORDER BY %s" % order[0]
            if len(order) > 1:
                sql += " %s" % order[1]

        # limit
        if limit:
            sql += " LIMIT %s" % limit[0]
            if len(limit) > 1:
                sql += " OFFSET %s" % limit[1]
        return self.query(sql, where[1] if where and len(where) > 1 else None)

    def __serialize_update(self, data):
        return "=%s,".join(data.keys()) + "=%s"

    def query(self, query: str, params=None):
        # Write a connetion decorator here. If connection is not alive then try for reconnect. Max retries are 3.
        # This method should also handle all the execeptions raised by the database.
        try:
            self.cur.execute(query, params)
        except Exception as e:
            raise
        return self.cur

    def last_id(self):
        return self.cur.lastrowid

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()

    def is_closed(self):
        return self.conn.closed

    def end(self):
        self.cur.close()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.end()
