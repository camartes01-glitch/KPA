import asyncio
import uvicorn

if __name__ == "__main__":
    print("Starting KPA debug server...")

    config = uvicorn.Config(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="debug",
    )

    server = uvicorn.Server(config)

    print("should_exit before run:", server.should_exit)

    try:
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        print("KeyboardInterrupt received")
    except BaseException as exc:
        print("SERVER EXCEPTION:", repr(exc))
        raise
    finally:
        print("should_exit after run:", server.should_exit)
        print("KPA debug server stopped")
