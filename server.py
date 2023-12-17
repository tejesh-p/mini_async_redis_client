# Note: The below code is not working properly.
# import asyncio
# import ssl
#
#
# async def handle_client(reader, writer):
#     ssl_context = ssl.create_default_context()
#     await writer.start_tls(ssl_context)
#     while True:
#         print("I did get there")
#         data = await reader.readuntil(b'\r\n')
#         command = data.decode().strip()
#
#         if command.upper() == 'QUIT':
#             print("Client disconnected.")
#             break
#
#         response = execute_command(command)
#         writer.write(response.encode())
#         await writer.drain()
#
#     writer.close()
#
#
# def execute_command(command):
#     # Implement basic command handling
#     if command.upper() == 'PING':
#         return "+PONG\r\n"
#     elif command.upper() == 'INFO':
#         return "+Server Info: Async Redis Clone\r\n"
#     else:
#         return "-Unknown Command\r\n"
#
#
# async def main():
#     ssl_context = ssl.create_default_context()
#     server = await asyncio.start_server(handle_client, '0.0.0.0', 6379, ssl=ssl_context, ssl_handshake_timeout=5,
#                                         start_serving=False)
#
#     addr = server.sockets[0].getsockname()
#     print(f'Serving on {addr}')
#
#     try:
#         async with server:
#             await server.serve_forever()
#     except KeyboardInterrupt:
#         print("^C received, shutting down the server")
#         server.close()
#
#
# if __name__ == "__main__":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     asyncio.run(main())
