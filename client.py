import asyncio


class CommandNotFoundError(Exception): pass


class RedisError(Exception): pass


# todo add dictionary/map support
class RedisClient:
    def __init__(self):
        self._handler = {
            b'+': self._handle_simple_string,
            b'-': self._handle_error,
            b':': self._handle_integer,
            b'$': self._handle_bulk_string,
            b'*': self._handle_array,
            # b'%': self._handle_dict, #todo enable dictionary/map support
            b'_': self._handle_null,
            b'#': self._handle_boolean,
            b',': self._handle_float,
            b'(': self._handle_integer
        }
        # allowing only 1 process to read/write to stream at a time
        self.semaphore = asyncio.Semaphore(1)

    async def _handle_array(self):
        array_len = await self._handle_integer()
        return [await self._read_reply() for _ in range(array_len)]

    async def _handle_float(self):
        result = await self._handle_read()
        return float(result)

    async def _handle_null(self):
        return None

    async def _handle_boolean(self):
        result = await self._handle_read()
        return True if result == 't' else False

    async def _handle_error(self):
        result = await self._handle_read()
        raise RedisError(result)

    async def _handle_integer(self):
        result = await self._handle_read()
        return int(result)

    async def _handle_simple_string(self):
        return await self._handle_read()

    async def _handle_bulk_string(self):
        length = await self._handle_read()
        if length == '-1':
            return None
        length = int(length) + 2
        result = await self.r.read(length)
        return result[:-2].decode()

    async def _handle_read(self):
        ch = b""
        result = b""
        while ch != b"\n":
            ch = await self.r.read(1)
            result += ch
        result = result[:-2]
        return result.decode()

    async def send(self, *args):
        async with self.semaphore:
            resp = "".join([f"${len(i)}\r\n{i}\r\n" for i in args])
            self.w.write(f"*{len(args)}\r\n{resp}".encode())
            await self.w.drain()
            return await self._read_reply()

    async def _read_reply(self):
        tag = await self.r.read(1)
        if tag in self._handler:
            return await self._handler[tag]()
        raise CommandNotFoundError(f'Unknown command: {tag.decode()}')

    async def set(self, key, val):
        return await self.send("SET", key, val)

    async def get(self, key):
        return await self.send("GET", key)

    async def incr(self, key):
        return await self.send("INCR", key)

    async def delete(self, key):
        return await self.send("DEL", key)

    async def decr(self, key):
        return await self.send("DECR", key)

    async def exists(self, key):
        return await self.send("EXISTS", key)

    async def connect(self, host, port):
        self.r, self.w = await asyncio.open_connection(host, port)
