import ujson
import uasyncio
import btree
import gc

from debug import log
debug = True

class Database():

    def __init__(self, data_id="other"):
        self.id = data_id

        try:
            f = open('btree.db', 'rb')
        except:
            f = open('btree.db', 'wb')
            
        self.db = btree.open(f)
        self.db['busy'] = b'' + '{"status": 0}'
        self.db.close()
        f.close()
    
    def save_data(self, data, amount_to_keep_locally=10):

        try:
            f = open('btree.db', 'rb')
        except:
            f = open('btree.db', 'wb')
        self.db = btree.open(f)
                
        while ujson.loads(self.db['busy'])["status"]:
            uasyncio.sleep_ms(50)
        self.db['busy'] = b'' + '{"status": 1}'

        try:
            db_data = ujson.loads(self.db['data'])
        except:
            db_data = {}
        
        try:
            db_data[self.id].append(data)
        except:
            db_data[self.id] = []
        
        db_data[self.id] = db_data[self.id][-amount_to_keep_locally:]
        
        log("------------------------DB MEMORY-----------------------", debug)
        log("Processing: {0}".format(self.id), debug)

        log("Memory BEFORE     UJSON DUMP - FREE: {0} | ALLOCATED: {1}".format(gc.mem_free(), gc.mem_alloc()), debug)
        
        all_data = ujson.dumps(db_data)

        log("--------------------------------------------------------", debug)
        log("Memory AFTER      UJSON DUMP - FREE: {0} | ALLOCATED: {1}".format(gc.mem_free(), gc.mem_alloc()), debug)
        
        gc.collect()

        log("--------------------------------------------------------", debug)
        log("Memory AFTER GARBAGE COLLECT - FREE: {0} | ALLOCATED: {1}".format(gc.mem_free(), gc.mem_alloc()), debug)
        log("--------------------------------------------------------", debug)

        self.db['data'] = all_data
        self.db['busy'] = b'' + '{"status": 0}'
        self.db.close()
        f.close()
    
    def load_data_all(self):
        try:
            f = open('btree.db', 'rb')
        except:
            f = open('btree.db', 'wb')
        self.db = btree.open(f)

        data = ujson.loads(self.db['data'])
        
        self.db.close()
        f.close()
        
        return data