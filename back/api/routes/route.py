import os

from back.api.auth.auth import TokenClaims, get_token
from back.api.schemas.chat_schema import RagChatRequest, RagChatResponse
from back.api.services.rag_client import RagClient
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse


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
async def chat(request: RagChatRequest) -> RagChatResponse | dict[str, str]:
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
