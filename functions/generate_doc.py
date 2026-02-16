import requests
from bs4 import BeautifulSoup
import os
import difflib
from azure.storage.blob import BlobServiceClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def main():
    # 1. 最新のWhat's Newを取得
    url = "https://learn.microsoft.com/en-us/azure/ai-services/openai/whats-new"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    current_lines = [line.strip() for line in soup.find('main').get_text().splitlines() if line.strip()]
    current_content = "\n".join(current_lines)

    # 2. Blobクライアントとコンテナの準備
    connstr = os.getenv("BLOBSTORSGECONNECTIONSTRING")
    blob_service_client = BlobServiceClient.from_connection_string(connstr)

    # コンテナ設定
    doc_container_name = "documents"
    diff_container_name = "diffs"

    for c_name in [doc_container_name, diff_container_name]:
        c_client = blob_service_client.get_container_client(c_name)
        if not c_client.exists():
            c_client.create_container()

    doc_container_client = blob_service_client.get_container_client(doc_container_name)
    diff_container_client = blob_service_client.get_container_client(diff_container_name)

    # 3. 日付とパスの設定
    now = datetime.now()
    path_suffix = f"{now.strftime('%Y')}/{now.strftime('%m')}/{now.strftime('%Y%m%d')}"
    new_doc_name = f"{path_suffix}_whatsnew.txt"
    new_diff_name = f"{path_suffix}_diff.txt"

    # 4. 前回のデータを取得
    blob_list = list(doc_container_client.list_blobs())
    previous_content = ""

    if blob_list:
        latest_blob_info = sorted(blob_list, key=lambda x: x.name)[-1]
        latest_blob_client = doc_container_client.get_blob_client(latest_blob_info.name)
        previous_content = latest_blob_client.download_blob().readall().decode('utf-8')

    # 5. 比較と保存
    if current_content != previous_content:
        # --- 差分(diff)の作成 ---
        if not previous_content:
            diff_content = "初期キャプチャーのため差分なし"
        else:
            diff = difflib.unified_diff(
                previous_content.splitlines(),
                current_content.splitlines(),
                lineterm='',
                fromfile='previous',
                tofile='current'
            )
            # 追加された行（+）のみを抽出してテキスト化
            added_lines = [line[1:] for line in diff if line.startswith('+') and not line.startswith('+++')]
            diff_content = "\n".join(added_lines) if added_lines else "テキストの変更のみ検出されました"

        # 6. 両方のコンテナに保存
        # フルテキストの保存
        doc_container_client.get_blob_client(new_doc_name).upload_blob(current_content, overwrite=True)
        # 差分テキストの保存
        diff_container_client.get_blob_client(new_diff_name).upload_blob(diff_content, overwrite=True)

        print(f"変更が検知され、ファイルが作成されました。\nDoc: {new_doc_name}\nDiff: {new_diff_name}")
    else:
        print("変更は検出されませんでした。")

if __name__ == "__main__":
    main()
