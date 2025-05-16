# async_helpers.py
import redis.asyncio as redis
from . import get_connection

AUTO_FETCH_QUEUE='auto_fetch'
FETCH_BASE_MODELS ='update_base_data'

r = get_connection()

async def get_api_info(id):
    return await r.hgetall(f'api_info:{id}')


"""class FredAndLup:
    def __init__(self):
        self.lup    = None
        self.fred   = None
        self.isStop = True
        self.denZukunft:List[asyncio.Future] = []
        
    def is_alive(self):
        return True if self.lup.is_running() and self.fred.is_alive() else False
    
    def start(self):
        if self.isStop:
            if not self.lup or self.lup.is_closed():
                self.lup=asyncio.new_event_loop()

            if not self.fred or not self.fred.is_alive():
                self.fred   = threading.Thread(target=lambda: (self.lup.set_debug(False), self.lup.run_forever()),daemon=True)
                self.fred.start()
            self.isStop = False

    def add(self, coro):
        if not self.isStop:
            self.denZukunft.append(asyncio.run_coroutine_threadsafe(coro, self.lup))
        else:
            raise Exception('Du weisst nicht was du wills! Iss einen Pilz.')
        
    def wait_finish(self):
        if not self.isStop:
            self.isStop=True
            denVergangenheit = List[Any] = []
            
            for i in self.denZukunft:
                denVergangenheit.append(i.result())
            self.lup.close()
            self.fred.daemon=False
            return denVergangenheit
        
    def stop(self):
        if not self.isStop:
            self.isStop=True
            
            for i in self.denZukunft:
                i.cancel()
            self.fred.daemon=False
            self.lup.close()"""