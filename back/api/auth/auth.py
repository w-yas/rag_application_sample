import asyncio
import os
from time import time

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWKClient
from pydantic import BaseModel

from back.api.utils.logging import logger


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
AUDIENCE = os.getenv("AUDIENCE")
ISSUER = os.getenv("ISSUER")
WELL_KNOWN = os.getenv("WELL_KNOWN")


class TokenClaims(BaseModel):
    claims: dict


class JwksProvider:
    def __init__(self, well_known_url: str, ttl: int = 60):
        self.well_known_url = well_known_url
        self.ttl = ttl
        self.jwks_client: PyJWKClient | None = None
        self._fetched_at: float = 0.0
        self._lock = asyncio.Lock()

    async def _fetch_jwks_uri(self) -> str:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(self.well_known_url)
            response.raise_for_status()
            return response.json()["jwks_uri"]

    async def get_client(self) -> PyJWKClient:
        current_time = time()
        if self.jwks_client and (current_time - self._fetched_at) <= self.ttl:
            return self.jwks_client

        async with self._lock:
            current_time = time()
            if self.jwks_client and (current_time - self._fetched_at) <= self.ttl:
                return self.jwks_client
            jwks_uri = await self._fetch_jwks_uri()
            self.jwks_client = PyJWKClient(jwks_uri)
            self._fetched_at = current_time
            return self.jwks_client

    async def refresh_client(self) -> None:
        async with self._lock:
            jwks_uri = await self._fetch_jwks_uri()
            self.jwks_client = PyJWKClient(jwks_uri)
            self._fetched_at = time()
            return self.jwks_client

    async def get_signing_key_with_retry(self, token: str):
        try:
            client = await self.get_client()
            clients = client.get_signing_key_from_jwt(token)
            return clients
        except Exception as e:
            logger.error(f"First attempt failed. Exception: {type(e).__name__}: {e}")
            try:
                # 鍵リストの更新を試みる
                await self.refresh_client()
            except httpx.HTTPError:
                logger.error("Http Error has Occuered")
                raise
            await asyncio.sleep(0.5)
            try:
                # 新しいクライアントを取得
                client = await self.get_client()
                clients_retry = client.get_signing_key_from_jwt(token)
                return clients_retry
            except Exception as e_retry:
                # 2回目の失敗も鍵が見つからない場合、サーバー側の問題として HTTPException を送出
                logger.error(
                    f"Second attempt failed. Exception: {type(e_retry).__name__}: {e_retry}"
                )
                raise  # get_token の例外処理でキャッチされる


_jwks_provider = JwksProvider(WELL_KNOWN, ttl=3600)


async def get_token(id_token: str = Depends(oauth2_scheme)) -> TokenClaims:
    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="認証トークンが提供されていません"
        )
    try:
        signing_key = await _jwks_provider.get_signing_key_with_retry(id_token)
        options = {
            "verify_signature": True,
            "verify_exp": True,
            "verify_nbf": True,  # Not Before の検証を有効化
            "require": ["exp", "iat", "nbf"],  # exp, iat, nbf クレームの存在を要求
        }
        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER,
            options=options,
        )
        logger.info("Auth Token Verified")
        return TokenClaims(claims=claims)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="トークンの有効期限が切れています"
        )
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="無効なオーディエンス"
        )
    except jwt.InvalidIssuerError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="無効な発行者")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="無効なトークン")
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="認証サービスに接続できません"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="トークンの検証に失敗しました"
        )
