import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import os

# --- 設定 ---
CONFIG_FILE = 'config.json'
VIDEOS_FILE = 'videos.json'

def load_json(filepath):
    """JSONファイルを読み込む関数"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_json(filepath, data):
    """JSONファイルに保存する関数"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_rss(channel_id):
    """YouTubeのRSSフィードを取得して解析する関数"""
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        # URLからデータを取得
        response = urllib.request.urlopen(url)
        xml_data = response.read()
        # XMLとして解析
        root = ET.fromstring(xml_data)
        return root
    except Exception as e:
        print(f"エラー: {channel_id} のRSS取得に失敗しました。詳細: {e}")
        return None

def main():
    """プログラムの実行開始場所（メイン処理）"""
    print("--- 動画情報の取得を開始します ---")
    
    # 1. 設定ファイルと現在の動画データを読み込む
    config = load_json(CONFIG_FILE)
    existing_videos = load_json(VIDEOS_FILE)
    
    # 既存の動画IDをリストにしておく（重複チェック用）
    existing_ids = [video['id'] for video in existing_videos]
    
    new_videos = []
    
    # 2. 設定されたチャンネルごとに処理を行う
    for channel in config:
        channel_id = channel['channel_id']
        channel_name = channel['channel_name']
        keyword = channel['keyword']
        
        print(f"\nチャンネル確認中: {channel_name} (キーワード: {keyword})")
        
        # RSSフィードを取得
        root = fetch_rss(channel_id)
        if root is None:
            continue
            
        # 名前空間の定義（XMLのタグ検索に必要）
        namespace = {'ns': 'http://www.w3.org/2005/Atom', 'media': 'http://search.yahoo.com/mrss/'}
        
        # 最新の動画エントリーを順番に確認
        for entry in root.findall('ns:entry', namespace):
            video_id = entry.find('ns:id', namespace).text.replace('yt:video:', '')
            title = entry.find('ns:title', namespace).text
            published_at = entry.find('ns:published', namespace).text
            
            # メディアグループから概要欄（description）を取得
            media_group = entry.find('media:group', namespace)
            description = ""
            if media_group is not None:
                desc_element = media_group.find('media:description', namespace)
                if desc_element is not None and desc_element.text is not None:
                    description = desc_element.text
            
            # 3. フィルタリング（タイトルまたは概要欄にキーワードが含まれているか）
            if keyword in title or keyword in description:
                # 4. 重複チェック（すでに保存されていないか）
                if video_id not in existing_ids:
                    print(f"  -> [新規追加] {title}")
                    # 新しい動画データをリストに追加
                    new_videos.append({
                        "id": video_id,
                        "title": title,
                        "channel": channel_name,
                        "published_at": published_at
                    })
                else:
                    print(f"  -> [スキップ(取得済)] {title}")
    
    # 5. 更新と保存
    if new_videos:
        # 新しい動画を先頭にして、既存の動画と結合
        updated_videos = new_videos + existing_videos
        save_json(VIDEOS_FILE, updated_videos)
        print(f"\n合計 {len(new_videos)} 件の新しい動画を保存しました。")
    else:
        print("\n新しい動画はありませんでした。")
        
    print("--- 処理が完了しました ---")

# プログラムが直接実行された場合に main() を呼び出す
if __name__ == "__main__":
    main()
