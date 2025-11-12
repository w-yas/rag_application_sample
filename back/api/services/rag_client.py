import os
from azure.search.documents import SearchClient
from openai import AzureOpenAI
from azure.search.documents.models import VectorizableTextQuery
from azure.core.credentials import AzureKeyCredential
from back.api.utils.logging import logger


class RagClient:
    def __init__(
        self,
        search_endpoint: str,
        search_api_key: str,
        search_index_name: str,
        openai_endpoint: str,
        openai_api_key: str,
        deployment_name: str,
        api_version: str,
        top_k: int = 3,
        search_mode: str = "default",
    ):

        self.search_endpoint = search_endpoint or os.getenv("AZURE_SEARCH_ENDPOINT")
        self.search_api_key = search_api_key or os.getenv("AZURE_SEARCH_KEY")
        self.search_index_name = search_index_name or os.getenv("INDEX_NAME")
        self.openai_endpoint = openai_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.openai_api_key = openai_api_key or os.getenv("AZURE_OPENAI_KEY")
        self.deployment_name = deployment_name or os.getenv("DEPLOYMENT_NAME")
        self.api_version = api_version or os.getenv("API_VERSION")
        self.top_k = top_k
        self.search_mode = search_mode
        self.content_field = os.getenv("CONTENT_FIELD", "chunk")
        self.title_field = os.getenv("TITLE_FIELD", "title")
        try:
            self._init_cients()
        except Exception:
            logger.error("RagClientの初期化に失敗しました。")
            raise

    def _init_cients(self) -> None:
        if not all(
            [
                self.search_endpoint,
                self.search_api_key,
                self.search_index_name,
                self.openai_endpoint,
                self.openai_api_key,
                self.deployment_name,
                self.api_version,
            ]
        ):
            logger.error("クライアントの初期化に必要な環境変数が不足しています。")
            raise ValueError("クライアントの初期化に必要な環境変数が不足しています。")

        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.search_index_name,
            credential=AzureKeyCredential(self.search_api_key),
        )

        self.openai_client = AzureOpenAI(
            azure_endpoint=self.openai_endpoint,
            api_key=self.openai_api_key,
            api_version=self.api_version,
        )

    def find_documents(self, query: str, top_k: int = 3) -> list:
        try:
            # ベクトルクエリの設定
            vector_query = VectorizableTextQuery(
                text=query, k_nearest_neighbors=50, fields="text_vector"
            )

            # 検索モードに基づいて検索を実行
            search_results = None  # 初期化
            if (
                self.search_mode == "semantic"
            ):  # セマンティック検索+ハイブリット検索 + スコアリング
                search_results = self.search_client.search(
                    search_text=query,
                    query_type="semantic",
                    scoring_profile="my-scoring-profile",
                    semantic_configuration_name="my-semantic-config",
                    scoring_parameters=["tags-ocean, 'sea surface', seas, surface"],
                    vector_queries=[vector_query],
                    select="*",
                    top=top_k,
                )
            elif self.search_mode == "hybrid":  # ハイブリット検索
                search_results = self.search_client.search(
                    search_text=query,
                    vector_queries=[vector_query],
                    select="*",
                    top=top_k,
                )
            else:  # デフォルトのフルテキスト検索
                search_results = self.search_client.search(
                    search_text="*",
                    select="*",
                    top=top_k,
                )

            # 検索結果がNoneの場合のチェック
            if search_results is None:
                logger.error("検索結果が取得できませんでした")
                return []

            # 検索結果の処理
            documents = []
            for result in search_results:
                doc = {
                    "content": result.get("chunk", ""),
                    "title": result.get("title", ""),
                    "score": result.get("@search.score", 0.0),
                    "locations": result.get("locations", []),
                }
                documents.append(doc)

            return documents

        except Exception as e:
            logger.error(f"検索エラーの詳細: {str(e)}")
            raise Exception(f"ドキュメント検索中にエラーが発生しました: {e}")

    def create_response(self, query: str, documents: list) -> str:
        try:
            context = self._generate_context_from_documents(documents)
            system_message = """
            あなたは有能なアシスタントです。以下のコンテキスト情報を使用して、ユーザーの質問に回答してください。
            """
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"コンテキスト情報:\n{context}\n\n質問: {query}"},
            ]

            # FIXME: 必要ならResponse API形式に変更
            response = self.openai_client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=(
                    0.3 if self.search_mode == "hybrid" or self.search_mode == "semantic" else 0.7
                ),
                max_tokens=1024,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"応答生成中にエラーが発生しました: {e}")
            return "申し訳ありませんが、現在質問に答えることができません。後でもう一度お試しください。"

    def _generate_context_from_documents(self, documents: list) -> str:
        context_parts = []
        for doc in documents:
            context_parts.append(
                f"タイトル: {doc['title']}\n内容: {doc['content']}\nスコア: {doc['score']:.2f}\n"
            )
        return "\n---\n".join(context_parts)

    def get_response_with_rag(self, query: str) -> dict:
        documents = self.find_documents(query, top_k=self.top_k)
        response = self.create_response(query, documents)
        return {
            "query": query,
            "response": response,
            "documents": documents,
            "search_mode": self.search_mode,
        }
