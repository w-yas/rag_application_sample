import os

from back.api.auth.auth import TokenClaims, get_token
from back.api.db.db import get_db
from back.api.models import Thread
from back.api.schemas.chat_schema import ChatThread, RagChatRequest, RagChatResponse, ThreadResponse
from back.api.services.rag_client import RagClient
from back.api.utils.logging import logger
from fastapi import APIRouter, Depends, HTTPException, status  # 追加
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session


router = APIRouter()


# 環境変数を取得し、Noneの場合はエラーにするヘルパー関数 (または RagClient 内部で処理)
def get_env_or_raise(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"環境変数 '{key}' が設定されていません。")
    return value


@router.get("/")
async def get_root(token: TokenClaims = Depends(get_token)) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={"message": "API is running"},
        headers={"X-Custom-Header": "value"},
    )


@router.post("/chat", response_model=RagChatResponse)
async def chat(
    request: RagChatRequest, token: TokenClaims = Depends(get_token)
) -> RagChatResponse | dict[str, str]:
    try:
        search_endpoint = get_env_or_raise("SEARCH_ENDPOINT")
        search_api_key = get_env_or_raise("SEARCH_API_KEY")
        search_index_name = get_env_or_raise("SEARCH_INDEX_NAME")
        openai_endpoint = get_env_or_raise("OPENAI_ENDPOINT")
        openai_api_key = get_env_or_raise("OPENAI_API_KEY")
        api_version = get_env_or_raise("API_VERSION")

        rag_client = RagClient(
            search_endpoint=search_endpoint,
            search_api_key=search_api_key,
            search_index_name=search_index_name,
            openai_endpoint=openai_endpoint,
            openai_api_key=openai_api_key,
            deployment_name=request.model,
            api_version=api_version,
            top_k=request.top_k,
            search_mode=request.search_mode,
        )
        query = request.query
        results = rag_client.get_response_with_rag(query)
    except Exception as e:
        return {"error": str(e)}

    return RagChatResponse(
        query=results["query"],
        response=results["response"],
        documents=results["documents"],
        search_mode=results["search_mode"],
    )


@router.get("/threads", response_model=ThreadResponse, status_code=status.HTTP_200_OK)
def get_user_chat_history(
    token: TokenClaims = Depends(get_token), db: Session = Depends(get_db)
) -> ThreadResponse:
    try:
        stmt = select(Thread).where(Thread.user_id == token.claims.get("sub"))
        result = db.scalars(stmt)
        threads = result.all()
        chat_threads = [ChatThread.model_validate(t) for t in threads]
        return ThreadResponse(threads=chat_threads)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/thread", response_model=ChatThread, status_code=status.HTTP_201_CREATED)
def create_thread(
    token: TokenClaims = Depends(get_token), db: Session = Depends(get_db)
) -> ChatThread:
    try:
        user_id = token.claims.get("sub")
        new_thread = Thread(user_id=user_id, title="New Chat Thread")

        db.add(new_thread)
        db.commit()
        db.refresh(new_thread)

        return ChatThread.model_validate(new_thread)

    except Exception as e:
        db.rollback()
        logger.error(f"Thread creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/thread/{thread_id}/title", status_code=status.HTTP_200_OK)
def update_thread_title(
    thread_id: str,
    new_title: str,
    token: TokenClaims = Depends(get_token),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        stmt = select(Thread).where(
            Thread.id == thread_id, Thread.user_id == token.claims.get("sub")
        )
        result = db.execute(stmt)
        thread = result.scalar_one_or_none()

        if thread is None:
            raise HTTPException(status_code=404, detail="Thread not found")

        thread.title = new_title
        db.commit()
        return {"message": "Thread title updated successfully"}

    except HTTPException:
        raise
    except Exception as e:

        db.rollback()
        logger.error(f"Failed to update thread title: {e}")
        raise HTTPException(status_code=500, detail=str(e))
