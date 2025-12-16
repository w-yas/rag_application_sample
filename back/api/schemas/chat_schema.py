from datetime import datetime
from enum import Enum
from typing import Annotated, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class SearchMode(str, Enum):
    FULL = "full"
    HYBRID = "hybrid"
    SEMANTIC = "semantic"


class RagChatResponse(BaseModel):
    query: Annotated[str, Field(..., description="ユーザーからの問い合わせ内容")]
    response: Annotated[str, Field(..., description="RAGを経由した応答")]
    documents: Annotated[list[str], Field(..., description="応答生成に使用されたドキュメントのリスト")]
    search_mode: Annotated[str, Field(..., description="サーチモード")]


class RagChatRequest(BaseModel):
    query: Annotated[str, Field(..., description="ユーザーからの問い合わせ内容")]
    top_k: Annotated[Optional[int], Field(ge=1, le=50, description="取得するドキュメントの上位K件数")]
    search_mode: Annotated[Optional[SearchMode], Field(SearchMode.FULL, description="サーチモードの指定")]
    model: Annotated[str, Field("gpt-4o", description="使用する言語モデルの指定")]


class ChatMessage(BaseModel):
    id: Annotated[str, Field(default_factory=lambda: str(uuid4()), description="メッセージの一意な識別子")]
    thread_id: Annotated[str, Field(..., description="メッセージが属するチャットスレッドの識別子")]
    text: Annotated[str, Field(..., description="メッセージの内容")]
    sender: Annotated[str, Field(..., description="メッセージの送信者（例: 'user', 'bot'）")]
    timestamp: datetime = Field(default_factory=datetime.now, description="メッセージの送信日時")

    # 属性からの読み取りを許可
    class Config:
        from_attributes = True


class ChatThread(BaseModel):
    id: Annotated[
        str,
        Field(default_factory=lambda: str(uuid4()), description="チャットスレッドの一意な識別子"),
    ]
    user_id: Annotated[str, Field(..., description="チャットスレッドの所有者であるユーザーの識別子")]
    title: Annotated[str, Field(..., description="チャットスレッドのタイトル")]
    created_at: datetime = Field(default_factory=datetime.now, description="チャットスレッドの作成日時")
    messages: Annotated[
        list[ChatMessage],
        Field(default_factory=list, description="チャットスレッド内のメッセージ一覧"),
    ]

    # 属性からの読み取りを許可
    class Config:
        from_attributes = True
