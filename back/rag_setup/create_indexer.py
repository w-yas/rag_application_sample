from azure.search.documents.indexes.models import SearchIndexer, FieldMapping
from azure.search.documents.indexes import SearchIndexerClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

load_dotenv()

AZURE_SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
credential = AzureKeyCredential(AZURE_SEARCH_KEY)


# インデクサーの作成
indexer_name = "py-rag-tutorial-idxr"
index_name = "py-rag-tutorial-idx"
skillset_name = "py-rag-tutorial-ss"
indexer_params = None

indexer = SearchIndexer(
    name=indexer_name,
    description="ドキュメントのインデックスと埋め込みの生成を実行するインデクサー",
    skillset_name=skillset_name,
    target_index_name=index_name,
    data_source_name="py-rag-tutorial-ds",
    field_mappings=[
        # metadata_storage_nameをtitleフィールドにマッピング
        FieldMapping(
            source_field_name="metadata_storage_name", target_field_name="title"
        )
    ],
    parameters=indexer_params,
)

# インデクサーの作成と実行
indexer_client = SearchIndexerClient(
    endpoint=AZURE_SEARCH_SERVICE, credential=credential
)
indexer_result = indexer_client.create_or_update_indexer(indexer)

print(
    f"{indexer_name} は作成し実行されてます。 クエリを実行するには数分かかる場合があります。"
)
