# server.py
import asyncio
from GameNetAPI import GameNetAPI

# -------------------- Message Callback --------------------
async def on_message(data, reliable, proto):
    """
    Called whenever a packet is delivered from the client.
    - data: {'seq_no': int, 'timestamp': int, 'payload': dict}
    - reliable: True if packet is RELIABLE
    - proto: GameServerProtocol instance
    """
    print(f"[SERVER CALLBACK] {data}")

# -------------------- Main --------------------
async def main():
    api = GameNetAPI(
        isClient=False,
        host="localhost",
        port=4433,
        certfile="cert.pem",
        keyfile="key.pem",
    )

    api.set_message_callback(on_message)

    # Track connected server protocols
    api.server_protocols = []

    # Wrapper to track protocols automatically
    def protocol_wrapper(*args, **kwargs):
        from GameServerProtocol import GameServerProtocol
        proto = GameServerProtocol(*args, on_message=api.on_message, **kwargs)
        api.server_protocols.append(proto)
        return proto

    try:
        print("Starting QUIC server...")
        await api.start_server(create_protocol=protocol_wrapper)  # runs forever
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        # Print statistics once for all connected protocols
        if hasattr(api, "server_protocols"):
            for proto in api.server_protocols:
                proto.print_statistics()
        await api.close()

# -------------------- Entry Point --------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
