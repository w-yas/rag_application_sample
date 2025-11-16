#!/usr/bin/env bash
set -euo pipefail

# 必要な環境変数チェック
: "${TenantId:?TenantId is required}"

# ログイン（テナント指定）
az login -t "$TenantId" 

# Searchサービスの存在確認（なければ作成）
if ! az search service show \
  --name "$SERVICE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  >/dev/null 2>&1; then
  echo "Azure AI Search が存在しないため作成します: $SERVICE_NAME"

  az search service create \
    --name "$SERVICE_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --sku "$SKU" \
    --partition-count 1 \
    --replica-count 1

  KEY=$(az search admin-key show \
  --service-name "$SERVICE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query primaryKey -o tsv)
else
  echo "Azure AI Search は既に存在します: $SERVICE_NAME"
fi

ENVFILE=".env"

if grep -q '^AZURE_SEARCH_KEY=' "$ENVFILE"; then
  sed -i.bak "s#^AZURE_SEARCH_KEY=.*#AZURE_SEARCH_KEY=\"$KEY\"#" "$ENVFILE"
else
  printf '\nAZURE_SEARCH_KEY="%s"\n' "$KEY" >> "$ENVFILE"
fi

# インデックス作成関連のPythonスクリプト実行
python3.12 create_datasource_connection.py
python3.12 create_search_index.py
python3.12 create_skillset.py
python3.12 create_indexer.py

# クリーンアップ例（必要ならコメント解除）
# az search service delete -
# clean up
# az search service delete \
#   --name "test-ai-search" \
#   --resource-group "test-rg"