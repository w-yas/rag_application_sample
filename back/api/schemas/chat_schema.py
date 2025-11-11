from typing import Annotated, Optional
from pydantic import BaseModel, Field
from enum import Enum


class SearchMode(str, Enum):
    FULL = "full"
    HYBRID = "hybrid"
    SEMANTIC = "semantic"


class RagChatResponse(BaseModel):
    query: Annotated[str, Field(..., description="ユーザーからの問い合わせ内容")]
    response: Annotated[str, Field(..., description="RAGを経由した応答")]
    documents: Annotated[
        list[str], Field(..., description="応答生成に使用されたドキュメントのリスト")
    ]
    search_mode: Annotated[str, Field(..., description="サーチモード")]


class RagChatRequest(BaseModel):
    query: Annotated[str, Field(..., description="ユーザーからの問い合わせ内容")]
    top_k: Annotated[
        Optional[int], Field(ge=1, le=50, description="取得するドキュメントの上位K件数")
    ]
    search_mode: Annotated[
        Optional[SearchMode], Field(SearchMode.FULL, description="サーチモードの指定")
    ]
    model: Annotated[str, Field("gpt-4o", description="使用する言語モデルの指定")]
