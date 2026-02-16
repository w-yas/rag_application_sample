import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexer,
    IndexingParameters,
    IndexingParametersConfiguration,
    FieldMapping
)
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# 設定情報の取得
endpoint = os.getenv("AZURE_SEARCH_SERVICE")
key = os.getenv("AZURE_SEARCH_KEY")
credential = AzureKeyCredential(key)

# 1. クライアントの作成
indexer_client = SearchIndexerClient(endpoint=endpoint, credential=credential)

# 2. インデクサーのパラメータ設定（拡張子とパースモードの指定）
indexer_parameters = IndexingParameters(
    configuration=IndexingParametersConfiguration(
        parsing_mode="text",               # ファイルをテキストとして読み込む
        indexed_file_name_extensions=".txt"  # .txtのみを対象
    )
)

# 3. インデクサーの定義
indexer_name = "aoai-whatsnew-indexer"
indexer = SearchIndexer(
    name=indexer_name,
    data_source_name="py-rag-ds",  # 作成済みのデータソース名
    skillset_name="py-rag-ss",  # 作成済みのスキルセット名に合わせる
    target_index_name="aoai-whatsnew-idx", # 作成済みのインデックス名に合わせる
    parameters=indexer_parameters,
    field_mappings=[
        # source_field_name: Blob側の属性名
        # target_field_name: インデックス側のフィールド名、またはスキルセットが参照する名前
        FieldMapping(source_field_name="metadata_storage_name", target_field_name="source_file"),

        # Blobアップロード時に設定したカスタムメタデータをインデックス（またはスキルセット）に渡す
        FieldMapping(source_field_name="content_type", target_field_name="content_type"),
        FieldMapping(source_field_name="scraped_at", target_field_name="scraped_at")
    ]
)

# 4. インデクサーの作成と実行
# create_or_update は、存在しなければ作成、あれば更新します
indexer_result = indexer_client.create_or_update_indexer(indexer)

# 手動で実行を開始させる場合
indexer_client.run_indexer(indexer_name)

print(f"Indexer '{indexer_name}' は正常に作成・更新されました。")
print("現在バックグラウンドで処理を実行中です。完了まで数分かかる場合があります。")

# 5. (オプション) 実行ステータスの確認
status = indexer_client.get_indexer_status(indexer_name)
print(f"現在のステータス: {status.status}")