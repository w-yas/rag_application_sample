from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
)
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential

load_dotenv()

AZURE_STORAGE_CONNECTION = os.getenv("AZURE_STORAGE_CONNECTION")
AZURE_SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")

credential = AzureKeyCredential(AZURE_SEARCH_KEY)

# データソースの作成
indexer_client = SearchIndexerClient(endpoint=AZURE_SEARCH_SERVICE, credential=credential)
container = SearchIndexerDataContainer(name="essa-ebooks-pdfs-all")
data_source_connection = SearchIndexerDataSourceConnection(
    name="py-rag-tutorial-ds",
    type="azureblob",
    connection_string=AZURE_STORAGE_CONNECTION,
    container=container,
)
# データソースの接続を作成またはupdate
data_source = indexer_client.create_or_update_data_source_connection(data_source_connection)

print(f"Data source '{data_source.name}' created or updated.")
