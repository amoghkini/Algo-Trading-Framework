from pymongo import MongoClient

class MongoDB:
    
    conn = None
    conf = None
    db = None
    
    def __init__(self, **kwargs) -> None:
        self.conf = kwargs
        self.conf['host'] = kwargs.get("host", "127.0.0.1")
        self.conf['port'] = kwargs.get('port', 27017)
        self.conf['db'] = kwargs.get('db','logindb')
        self.connect()
    
    def connect(self) -> None:
        try:        
            
            self.conn = MongoClient(self.conf.get('host'),
                               self.conf.get('post'))
            self.db = self.conn[str(self.conf.get('db'))]
        except Exception as e:
            print("Mongo DB connection failed")
            raise ValueError('Connection to mongo database is faild',e)
    
    def end(self):
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self):
        self.end()