import asyncio
import os
from argparse import ArgumentParser

import uvicorn

from .app import app as FASTAPI_APP


async def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("MCPING_BFF_HOST") or "127.0.0.1",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=os.environ.get("MCPING_BFF_PORT") or 5000,
    )

    app = FASTAPI_APP

    args = parser.parse_args()
    host: str = args.host
    port: int = args.port

    server = uvicorn.Server(
        config=uvicorn.Config(
            app=app,
            host=host,
            port=port,
        )
    )
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
