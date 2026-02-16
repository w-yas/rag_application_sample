import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    HnswAlgorithmConfiguration,
    ScoringProfile,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    TagScoringFunction,
    TagScoringParameters,
    VectorSearch,
    VectorSearchProfile,
    FreshnessScoringFunction,
    FreshnessScoringParameters,
    ScoringFunctionAggregation

)
from dotenv import load_dotenv


load_dotenv()


AZURE_STORAGE_CONNECTION = os.getenv("AZURE_STORAGE_CONNECTION")
AZURE_SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE")
AZURE_OPENAI_ACCOUNT = os.getenv("AZURE_OPENAI_ACCOUNT")
credential = AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))

# Create a search index
index_name = "py-rag-tutorial-idx"
index_client = SearchIndexClient(endpoint=AZURE_SEARCH_SERVICE, credential=credential)
fields = [

    SearchField(name="parent_id", type=SearchFieldDataType.String, filterable=True),
    SearchField(
        name="chunk_id",
        type=SearchFieldDataType.String,
        key=True,
        sortable=True,
        filterable=True,
        facetable=True,
        # analyzer_name="keyword",
    ),
    SearchField(name="chunk", type=SearchFieldDataType.String, searchable=True, analyzer_name="ja.microsoft"),

    # ベクトルフィールド
    SearchField(
        name="text_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        vector_search_dimensions=1536,
        vector_search_profile_name="myHnswProfile",
    ),
    SearchField(name="source_file", type=SearchFieldDataType.String, filterable=True),
    SearchField(name="content_type", type=SearchFieldDataType.String, filterable=True, facetable=True), # "full" or "diff"
    SearchField(name="scraped_at", type=SearchFieldDataType.DateTimeOffset, sortable=True, filterable=True),
    SearchField(name="release_date", type=SearchFieldDataType.String, filterable=True, facetable=True),
    SearchField(name="models", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True, facetable=True),
]

# Configure the vector search configuration
vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(name="myHnsw"),
    ],
    profiles=[
        VectorSearchProfile(
            name="myHnswProfile",
            algorithm_configuration_name="myHnsw",
            vectorizer_name="myOpenAI",
        )
    ],
    vectorizers=[
        AzureOpenAIVectorizer(
            vectorizer_name="myOpenAI",
            kind="azureOpenAI",
            parameters=AzureOpenAIVectorizerParameters(
                resource_url=AZURE_OPENAI_ACCOUNT,
                deployment_name="text-embedding-ada-002",
                model_name="text-embedding-ada-002",
            ),
        ),
    ],
)

# セマンティック検索の設定インスタンスを作成
semantic_config = SemanticConfiguration(
    name="my-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(  # 検索時に優先されるフィールド
        content_fields=[SemanticField(field_name="chunk")],
        keywords_fields=[
            SemanticField(field_name="models"),
            SemanticField(field_name="release_date")
        ],  # キーワード候補として使用するフィールド

    ),
)
semantic_search = SemanticSearch(configurations=[semantic_config])

# スコアリングプロファイル
# 最新の情報を上位に、かつ「差分(diff)」ファイルを優先的に評価する設定
scoring_profiles = [
    ScoringProfile(
        name="freshness-boost",
        function_aggregation=ScoringFunctionAggregation.SUM,
        functions=[
            # 1. 日付が新しいほどスコアを上げる (Freshness)
            FreshnessScoringFunction(
                field_name="scraped_at",
                boost=10.0,
                parameters=FreshnessScoringParameters(boosting_duration="P30D") # 30日以内の情報を重視
            ),
            # 2. content_type が 'diff' の場合にスコアを上げる (Tag)
            TagScoringFunction(
                field_name="content_type",
                boost=2.0,
                parameters=TagScoringParameters(tags_parameter="typeTag")
            )
        ],
    )
]

# Create the search index
index = SearchIndex(
    name=index_name,
    fields=fields,
    vector_search=vector_search,
    semantic_search=semantic_search,
    scoring_profiles=scoring_profiles,
)
result = index_client.create_or_update_index(index)
print(f"{result.name} created")
