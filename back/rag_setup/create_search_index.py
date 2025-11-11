from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    ScoringProfile,
    TagScoringFunction,
    TagScoringParameters,
    SemanticSearch,
)
import os
from azure.core.credentials import AzureKeyCredential
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
    SearchField(name="parent_id", type=SearchFieldDataType.String),
    SearchField(name="title", type=SearchFieldDataType.String),
    SearchField(
        name="locations",
        type=SearchFieldDataType.Collection(SearchFieldDataType.String),
        filterable=True,
    ),
    SearchField(
        name="chunk_id",
        type=SearchFieldDataType.String,
        key=True,
        sortable=True,
        filterable=True,
        facetable=True,
        analyzer_name="keyword",
    ),
    SearchField(
        name="chunk",
        type=SearchFieldDataType.String,
        sortable=False,
        filterable=False,
        facetable=False,
    ),
    SearchField(
        name="text_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        vector_search_dimensions=1536,
        vector_search_profile_name="myHnswProfile",
    ),
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
        title_field=SemanticField(field_name="title"),
        keywords_fields=[
            SemanticField(field_name="locations")
        ],  # キーワード候補として使用するフィールド
        content_fields=[SemanticField(field_name="chunk")],
    ),
)
semantic_search = SemanticSearch(configurations=[semantic_config])

# スコアリングプロファイル
scoring_profile = [
    ScoringProfile(
        name="my-scoring-profile",
        functions=[
            TagScoringFunction(
                field_name="locations",
                boost=5.0,
                parameters=TagScoringParameters(tags_parameter="tags"),
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
    scoring_profiles=scoring_profile,
)
result = index_client.create_or_update_index(index)
print(f"{result.name} created")
