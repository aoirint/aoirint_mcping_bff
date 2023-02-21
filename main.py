import os
from urllib.parse import urljoin

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, parse_obj_as

MCPING_BFF_CORS_ALLOW_ORIGINS = os.environ["MCPING_BFF_CORS_ALLOW_ORIGINS"].split(",")

MCPING_WEB_API_URL = os.environ["MCPING_WEB_API_URL"]
MCPING_WEB_API_READ_API_KEY = os.environ["MCPING_WEB_API_READ_API_KEY"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=MCPING_BFF_CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BedrockServer(BaseModel):
    id: str
    name: str
    host: str
    port: int


class JavaServer(BaseModel):
    id: str
    name: str
    host: str
    port: int


class BedrockPingRecord(BaseModel):
    id: str
    bedrock_server_id: str
    timeout: float
    is_timeout: bool
    is_refused: bool
    version_protocol: int | None
    version_brand: str | None
    version_version: str | None
    latency: float | None
    players_online: int | None
    players_max: int | None
    motd: str | None
    map: str | None
    gamemode: str | None
    created_at: str
    updated_at: str


class JavaPingRecordPlayer(BaseModel):
    id: str
    java_ping_record_id: str
    player_id: str
    name: str


class JavaPingRecord(BaseModel):
    id: str
    java_server_id: str
    timeout: float
    is_timeout: bool
    is_refused: bool
    version_protocol: int | None
    version_name: str | None
    latency: float | None
    players_online: int | None
    players_max: int | None
    players_sample: list[JavaPingRecordPlayer] | None
    description: str | None
    favicon: str | None  # Data URL
    created_at: str
    updated_at: str


class BedrockServerResponseItem(BaseModel):
    id: str
    name: str
    host: str
    port: int
    ok: bool
    timestamp: str


class JavaServerResponseItem(BaseModel):
    id: str
    name: str
    host: str
    port: int
    ok: bool
    timestamp: str


@app.get("/bedrock_servers", response_model=list[BedrockServerResponseItem])
async def bedrock_servers():
    res = requests.post(
        urljoin(MCPING_WEB_API_URL, "bedrock_server/list"),
        headers={
            "X-Read-Api-Key": MCPING_WEB_API_READ_API_KEY,
        },
    )
    res.raise_for_status()
    bedrock_servers = parse_obj_as(list[BedrockServer], res.json())

    ret: list[BedrockServerResponseItem] = []
    for bedrock_server in bedrock_servers:
        res = requests.post(
            urljoin(MCPING_WEB_API_URL, "bedrock_ping_record/latest"),
            headers={
                "X-Read-Api-Key": MCPING_WEB_API_READ_API_KEY,
            },
            params={
                "bedrock_server_id": bedrock_server.id,
                "count": 1,
            },
        )
        res.raise_for_status()
        bedrock_ping_records = parse_obj_as(list[BedrockPingRecord], res.json())
        if len(bedrock_ping_records) == 0:
            continue

        bedrock_ping_record = bedrock_ping_records[0]
        is_ok = (
            not bedrock_ping_record.is_timeout and not bedrock_ping_record.is_refused
        )

        ret.append(
            BedrockServerResponseItem(
                id=bedrock_server.id,
                name=bedrock_server.name,
                host=bedrock_server.host,
                port=bedrock_server.port,
                ok=is_ok,
                timestamp=bedrock_ping_record.created_at,
            )
        )

    return ret


@app.get("/java_servers", response_model=list[JavaServerResponseItem])
async def java_servers():
    res = requests.post(
        urljoin(MCPING_WEB_API_URL, "java_server/list"),
        headers={
            "X-Read-Api-Key": MCPING_WEB_API_READ_API_KEY,
        },
    )
    res.raise_for_status()
    java_servers = parse_obj_as(list[JavaServer], res.json())

    ret: list[JavaServerResponseItem] = []
    for java_server in java_servers:
        res = requests.post(
            urljoin(MCPING_WEB_API_URL, "java_ping_record/latest"),
            headers={
                "X-Read-Api-Key": MCPING_WEB_API_READ_API_KEY,
            },
            params={
                "java_server_id": java_server.id,
                "count": 1,
            },
        )
        res.raise_for_status()
        java_ping_records = parse_obj_as(list[JavaPingRecord], res.json())
        if len(java_ping_records) == 0:
            continue

        java_ping_record = java_ping_records[0]
        is_ok = not java_ping_record.is_timeout and not java_ping_record.is_refused

        ret.append(
            JavaServerResponseItem(
                id=java_server.id,
                name=java_server.name,
                host=java_server.host,
                port=java_server.port,
                ok=is_ok,
                timestamp=java_ping_record.created_at,
            )
        )

    return ret
