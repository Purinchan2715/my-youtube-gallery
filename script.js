/**
 * 動画データを読み込み、HTMLに表示するプログラム
 */

// HTMLの読み込みが完了したら実行する
document.addEventListener('DOMContentLoaded', () => {
    const galleryElement = document.getElementById('gallery');
    
    // videos.json からデータを取得（非同期通信）
    fetch('videos.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('データの読み込みに失敗しました');
            }
            return response.json(); // JSONデータとして解釈
        })
        .then(videos => {
            // データ取得成功時の処理
            
            // ローディングの文字を消す
            galleryElement.innerHTML = '';
            
            if (videos.length === 0) {
                galleryElement.innerHTML = '<p class="loading">動画が見つかりませんでした。</p>';
                return;
            }
            
            // 動画データを1件ずつ処理してHTMLを生成
            videos.forEach(video => {
                // 日付を見やすい形式に変換 (例: 2026/07/01)
                const dateObj = new Date(video.published_at);
                const dateStr = dateObj.toLocaleDateString('ja-JP');
                
                // 動画へのリンクURL
                const videoUrl = `https://www.youtube.com/watch?v=${video.id}`;
                // YouTubeのサムネイル画像URL
                const thumbnailUrl = `https://img.youtube.com/vi/${video.id}/mqdefault.jpg`;
                
                // カードのHTML要素を作成
                const cardHtml = `
                    <a href="${videoUrl}" target="_blank" rel="noopener noreferrer" class="video-card">
                        <img src="${thumbnailUrl}" alt="${video.title}" class="video-thumbnail" loading="lazy">
                        <div class="video-info">
                            <h3 class="video-title">${video.title}</h3>
                            <div class="video-meta">
                                <span class="video-channel">${video.channel}</span>
                                <span class="video-date">${dateStr}</span>
                            </div>
                        </div>
                    </a>
                `;
                
                // ギャラリー領域に追加
                galleryElement.insertAdjacentHTML('beforeend', cardHtml);
            });
        })
        .catch(error => {
            // エラーが発生した場合の処理
            console.error('エラー:', error);
            galleryElement.innerHTML = `<p class="loading">エラーが発生しました: ${error.message}</p>`;
        });
});
