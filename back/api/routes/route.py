import os

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from back.api.auth.auth import get_token
from back.api.schemas.chat_schema import RagChatRequest, RagChatResponse
from back.api.services.rag_client import RagClient


router = APIRouter()


@router.get("/")
async def get_root(token=Depends(get_token)):
    return JSONResponse(
        status_code=200,
        content={"message": "API is running"},
        headers={"X-Custom-Header": "value"},
    )


@router.post("/chat", response_model=RagChatResponse)
async def chat(request: RagChatRequest):
    try:
        rag_client = RagClient(
            search_endpoint=os.getenv("SEARCH_ENDPOINT"),
            search_api_key=os.getenv("SEARCH_API_KEY"),
            search_index_name=os.getenv("SEARCH_INDEX_NAME"),
            openai_endpoint=os.getenv("OPENAI_ENDPOINT"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            deployment_name=request.model,
            api_version=os.getenv("API_VERSION"),
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
