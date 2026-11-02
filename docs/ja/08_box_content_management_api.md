# 第08章：Box コア API 実践ガイド —— Content Management 19大モジュール完全網羅

> **【技術ポジショニング】**
>
> クラウドストレージおよびエンタープライズコンテンツコラボレーションシステムの根底は、HTTP プロトコルを介して公開される**管理されたステートマシンとリソースモデル**です。
>
> Box プラットフォームにおいて、**Content Management（コンテンツ管理）** は絶対的な中核を担います。ファイル作成、チャンク分割レジュームアップロード、ディレクトリエクスプローラー、世代管理（バージョン管理）、同時実行制御ロック、ごみ箱ライフサイクル管理に至るまで、あらゆる機能がこのカテゴリに集約されています。
>
> 本章では、業務上の前提を排した**純粋なエンジニアリング視点**で、Content Management に属する**全19モジュール**を徹底解剖します。「CRUD 能力マトリックス」と「API 4要素カード」により、堅牢なメンタルモデルと本番水準の実装指針を提供します。

---

## 8.1 公式 Content Management アーキテクチャ全景

Box 公式開発者ポータル（`developer.box.com/reference`）を直接検証すると、Content Management アコーディオン配下には厳密に 19 個の独立リソースモジュールが定義されています：

![Box Content Management 公式 19 大モジュール全景（上部）](/images/08_step_01_content_management_cards_full.png)
*図 8.1：Box 開発者コンソール Content Management リソースパネル（上部）*

![Box Content Management 公式 19 大モジュール全景（下部）](/images/08_step_02_content_management_cards_lower.png)
*図 8.2：Box 開発者コンソール Content Management リソースパネル（下部）*

---

## 8.2 Content Management 19大モジュール CRUD マトリックス

下表は Content Management 全 19 モジュールの機能全景マトリックスです。各モジュールの HTTP メソッド（GET / POST / PUT / DELETE）対応状況および権限境界を一目で確認できます。

| 番号 | モジュール名 (Module) | 公式定義 (Official Description) | 日本語直感定義 | コアスコープ (Scope) | GET | POST | PUT | DELETE | クイックジャンプ |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **01** | **Files** | Core file operations and management | ファイルメタデータ CRUD・複製・移動 | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [詳細解説へ](#_01-files) |
| **02** | **Folders** | Organizing and structuring content | ディレクトリ階層の作成・探索・移動 | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [詳細解説へ](#_02-folders) |
| **03** | **File versions** | Version history and recovery | 過去バージョンの復元・昇格・完全削除 | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [詳細解説へ](#_03-file-versions) |
| **04** | **File requests** | Secure file collection workflows | ログイン不要のファイル提出リンク設定 | `manage_file_requests` | ✅ | ✅ | ✅ | ✅ | [詳細解説へ](#_04-file-requests) |
| **05** | **Uploads** | Direct standard file ingestion | 小容量ファイル単一アップロード (< 50MB) | `root_readwrite` | ❌ | ✅ | ❌ | ❌ | [詳細解説へ](#_05-uploads) |
| **06** | **Uploads (Chunked)** | Large file multipart sessions | 大容量ファイル分割・並列アップロード (≥ 50MB) | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [詳細解説へ](#_06-uploads-chunked) |
| **07** | **Downloads** | Binary content streaming | バイナリストリーム取得と 302 リダイレクト | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [詳細解説へ](#_07-downloads) |
| **08** | **Zip Downloads** | Multi-item batch packaging | 複数ファイル・フォルダの一括 Zip 圧縮ダウンロード | `root_readonly` | ✅ | ✅ | ❌ | ❌ | [詳細解説へ](#_08-zip-downloads) |
| **09** | **Folder Locks** | Concurrency and mutation freeze | フォルダ削除・移動防止ロック | `root_readwrite` | ✅ | ✅ | ❌ | ✅ | [詳細解説へ](#_09-folder-locks) |
| **10** | **Collections** | Tagging and virtual grouping | お気に入り等の仮想グルーピング管理 | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [詳細解説へ](#_10-collections) |
| **11** | **Recent items** | Audit and access recency stream | 最近アクセスしたアイテムの履歴照会 | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [詳細解説へ](#_11-recent-items) |
| **12** | **Transfer folders** | Content ownership migration | ユーザー所有ルートディレクトリの完全移譲 | `manage_users` | ❌ | ❌ | ✅ | ❌ | [詳細解説へ](#_12-transfer-folders) |
| **13** | **Web links** | External URL pointers in directory | フォルダ内への外部リンク配置・管理 | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [詳細解説へ](#_13-web-links) |
| **14** | **App item associations** | Third-party app binding relations | サードパーティアプリとファイル/フォルダの紐付け | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [詳細解説へ](#_14-app-item-associations) |
| **15** | **Trashed files** | Soft-deleted file lifecycle | ごみ箱内ファイルの確認・復元・完全消去 | `root_readwrite` | ✅ | ✅ | ❌ | ✅ | [詳細解説へ](#_15-trashed-files) |
| **16** | **Trashed folders** | Soft-deleted directory lifecycle | ごみ箱内フォルダの確認・復元・完全消去 | `root_readwrite` | ✅ | ✅ | ❌ | ✅ | [詳細解説へ](#_16-trashed-folders) |
| **17** | **Trashed items** | Global recycle bin indexing | ごみ箱内アイテムの一覧取得・ページング | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [詳細解説へ](#_17-trashed-items) |
| **18** | **Trashed web links** | Soft-deleted pointer recovery | ごみ箱内外部リンクの復元・完全消去 | `root_readwrite` | ✅ | ✅ | ❌ | ✅ | [詳細解説へ](#_18-trashed-web-links) |
| **19** | **Archives** | Long-term cold data lifecycle | コールドデータ自動アーカイブ管理 (v2025.0) | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [詳細解説へ](#_19-archives) |

---

## 8.3 共通接続仕様と前提要件

Box API を呼び出す際は、全クライアントで以下の通信契約を遵守します：

```txt
1. Base API URL:       https://api.box.com/2.0
2. Base Upload URL:    https://upload.box.com/api/2.0  (Uploads モジュール専用)
3. 認証ヘッダー:       Authorization: Bearer <ACCESS_TOKEN>
4. ペイロード形式:     Content-Type: application/json (バイナリ送信時を除く)
5. ルートフォルダID:   "0" (Box のルート ID は文字列の "0" であり、"/" や "root" ではありません)
```

---

## 8.4 各 API モジュール 4 要素カード解説

---

### 01. Files

#### 要素1：技術的本質と中核能力
Files モジュールは Box 内の**ファイルメタデータ**を管理します。ファイル属性の参照、サムネイル取得、別フォルダへの複製、名称変更・フォルダ移動、ごみ箱への論理削除を提供します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| ファイルメタデータ取得 | `GET` | `/files/{file_id}` | [Official Spec](https://developer.box.com/reference/get-files-id) |
| サムネイル画像取得 | `GET` | `/files/{file_id}/thumbnail.{extension}` | [Official Spec](https://developer.box.com/reference/get-files-id-thumbnail-id) |
| ファイルの複製 | `POST` | `/files/{file_id}/copy` | [Official Spec](https://developer.box.com/reference/post-files-id-copy) |
| メタデータ更新・移動 | `PUT` | `/files/{file_id}` | [Official Spec](https://developer.box.com/reference/put-files-id) |
| ファイル削除（ごみ箱へ） | `DELETE` | `/files/{file_id}` | [Official Spec](https://developer.box.com/reference/delete-files-id) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [GET メタデータ取得]
curl -s -X GET "https://api.box.com/2.0/files/123456789" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [POST 複製]
curl -s -X POST "https://api.box.com/2.0/files/123456789/copy" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "backup_2026.parquet",
       "parent": { "id": "987654321" }
     }'
```

```bash [PUT 名称変更・移動]
curl -s -X PUT "https://api.box.com/2.0/files/123456789" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "renamed_data.parquet",
       "parent": { "id": "0" }
     }'
```

```bash [DELETE 削除]
curl -s -X DELETE "https://api.box.com/2.0/files/123456789" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素4：アンチパターンと回避策
> [!CAUTION] **同時更新の競合防止 (412 Precondition Failed)**
> 分散環境下でメタデータを更新する際は、GET 時に取得した `ETag` を PUT リクエストのヘッダー `If-Match: "3"` に付与してください。他プロセスが先に更新していた場合、Box は即座に `412` を返し、意図しない上書きを阻止します。

---

### 02. Folders

#### 要素1：技術的本質と中核能力
Folders モジュールはツリー状の**ディレクトリ階層構造**を司ります。新規フォルダの作成、配下アイテムのカーソルページング探索、フォルダ全体の複製や移動、再帰的削除をサポートします。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| フォルダ情報取得 | `GET` | `/folders/{folder_id}` | [Official Spec](https://developer.box.com/reference/get-folders-id) |
| 配下アイテム一覧取得 | `GET` | `/folders/{folder_id}/items` | [Official Spec](https://developer.box.com/reference/get-folders-id-items) |
| フォルダ新規作成 | `POST` | `/folders` | [Official Spec](https://developer.box.com/reference/post-folders) |
| フォルダの複製 | `POST` | `/folders/{folder_id}/copy` | [Official Spec](https://developer.box.com/reference/post-folders-id-copy) |
| フォルダ更新・移動 | `PUT` | `/folders/{folder_id}` | [Official Spec](https://developer.box.com/reference/put-folders-id) |
| フォルダ削除（再帰含む） | `DELETE` | `/folders/{folder_id}?recursive=true` | [Official Spec](https://developer.box.com/reference/delete-folders-id) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [POST フォルダ作成]
curl -s -X POST "https://api.box.com/2.0/folders" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Raw_Lake_Data",
       "parent": { "id": "0" }
     }'
```

```bash [GET カーソル探索]
curl -s -X GET "https://api.box.com/2.0/folders/987654321/items?limit=100&usemarker=true" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [PUT フォルダ移動]
curl -s -X PUT "https://api.box.com/2.0/folders/987654321" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Archive_2026",
       "parent": { "id": "0" }
     }'
```

```bash [DELETE 再帰削除]
curl -s -X DELETE "https://api.box.com/2.0/folders/987654321?recursive=true" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素4：アンチパターンと回避策
> [!WARNING] **大規模ディレクトリでの Offset ページング性能劣化**
> アイテム数が 1 万件を超える場合、従来の `offset` は急激に性能劣化します。本番スクリプトでは必ず `usemarker=true` を指定し、レスポンスの `next_marker` を用いたカーソルページングを採用してください。

---

### 03. File versions

#### 要素1：技術的本質と中核能力
同名ファイルの再アップロード時、Box は古いファイルを上書きせず**バージョンチェーン**として保持します。本モジュールでは過去の履歴一覧の取得、旧バージョンの現行版への昇格、不要なバージョンの完全削除を行います。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| バージョン一覧取得 | `GET` | `/files/{file_id}/versions` | [Official Spec](https://developer.box.com/reference/get-files-id-versions) |
| 特定バージョン詳細 | `GET` | `/files/{file_id}/versions/{version_id}` | [Official Spec](https://developer.box.com/reference/get-files-id-versions-id) |
| 旧バージョンの昇格 | `POST` | `/files/{file_id}/versions/current` | [Official Spec](https://developer.box.com/reference/post-files-id-versions-current) |
| バージョンの復元 | `PUT` | `/files/{file_id}/versions/{version_id}` | [Official Spec](https://developer.box.com/reference/put-files-id-versions-id) |
| バージョンの完全消去 | `DELETE` | `/files/{file_id}/versions/{version_id}` | [Official Spec](https://developer.box.com/reference/delete-files-id-versions-id) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [GET バージョン一覧]
curl -s -X GET "https://api.box.com/2.0/files/123456789/versions" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [POST バージョン昇格]
curl -s -X POST "https://api.box.com/2.0/files/123456789/versions/current" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "type": "file_version",
       "id": "5566778899"
     }'
```

```bash [DELETE バージョン消去]
curl -s -X DELETE "https://api.box.com/2.0/files/123456789/versions/5566778899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素4：アンチパターンと回避策
> [!NOTE] **Current（現行）バージョンは直接削除不可**
> DELETE エンドポイントで直接削除できるのは過去世代のみです。現在アクティブなバージョンを削除しようとすると `400 Bad Request` になります。別のバージョンを `current` に昇格させた後に削除してください。

---

### 04. File requests

#### 要素1：技術的本質と中核能力
外部ユーザーや未認証クライアントから指定フォルダへ安全にファイルをアップロードさせる**提出用ゲートウェイ**を設定します。アップロード者は他の既存ファイルを閲覧できません。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| ファイルリクエスト取得 | `GET` | `/file_requests/{file_request_id}` | [Official Spec](https://developer.box.com/reference/get-file-requests-id) |
| リクエストリンク複製 | `POST` | `/file_requests/{file_request_id}/copy` | [Official Spec](https://developer.box.com/reference/post-file-requests-id-copy) |
| 設定更新・有効化 | `PUT` | `/file_requests/{file_request_id}` | [Official Spec](https://developer.box.com/reference/put-file-requests-id) |
| リクエスト削除 | `DELETE` | `/file_requests/{file_request_id}` | [Official Spec](https://developer.box.com/reference/delete-file-requests-id) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 設定取得]
curl -s -X GET "https://api.box.com/2.0/file_requests/123456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [PUT 設定変更]
curl -s -X PUT "https://api.box.com/2.0/file_requests/123456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Daily Data Ingestion Dropzone",
       "status": "active"
     }'
```

```bash [DELETE 削除]
curl -s -X DELETE "https://api.box.com/2.0/file_requests/123456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素4：アンチパターンと回避策
> [!WARNING] **紐付け先フォルダの存在確認**
> ファイルリクエストは実在する `folder_id` に依存します。フォルダが削除またはロックされていると、外部からのアップロードは失敗します。

---

### 05. Uploads

#### 要素1：技術的本質と中核能力
50MB 未満の小容量ファイルを対象とした、標準的な `multipart/form-data` による**直接アップロード**です。事前検証用の OPTIONS プリフライトもサポートします。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| アップロード事前検証 | `OPTIONS` | `https://upload.box.com/api/2.0/files/content` | [Official Spec](https://developer.box.com/reference/options-files-content) |
| 単一ファイルアップロード | `POST` | `https://upload.box.com/api/2.0/files/content` | [Official Spec](https://developer.box.com/reference/post-files-content) |
| 新バージョンアップロード | `POST` | `https://upload.box.com/api/2.0/files/{file_id}/content` | [Official Spec](https://developer.box.com/reference/post-files-id-content) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [POST ファイル直接送信]
curl -s -X POST "https://upload.box.com/api/2.0/files/content" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -F attributes='{"name":"node_config.json", "parent":{"id":"0"}}' \
     -F file=@./node_config.json
```

```bash [POST 新バージョン送信]
curl -s -X POST "https://upload.box.com/api/2.0/files/123456789/content" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -F file=@./node_config_v2.json
```
:::

#### 要素4：アンチパターンと回避策
> [!IMPORTANT] **エンドポイントドメインの相違（upload.box.com）**
> ファイルアップロード専用の Base URL は `https://upload.box.com/api/2.0` です。誤って `api.box.com` へ送信するとリクエストが拒否されます。

---

### 06. Uploads (Chunked)

#### 要素1：技術的本質と中核能力
50MB 以上の大容量ファイル向けの**分割並列セッション型アップロード**です。「セッション初期化 → 各パート送信 → コミット（結合） → アボート」の 4 フェーズステートマシンにより、ネットワーク断絶時のレジューム再開を保証します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| セッション作成 | `POST` | `https://upload.box.com/api/2.0/files/upload_sessions` | [Official Spec](https://developer.box.com/reference/post-files-upload-sessions) |
| 既存ファイル用セッション | `POST` | `https://upload.box.com/api/2.0/files/{file_id}/upload_sessions` | [Official Spec](https://developer.box.com/reference/post-files-id-upload-sessions) |
| パートデータの送信 | `PUT` | `https://upload.box.com/api/2.0/files/upload_sessions/{session_id}` | [Official Spec](https://developer.box.com/reference/put-files-upload-sessions-id) |
| 送信済パート一覧取得 | `GET` | `https://upload.box.com/api/2.0/files/upload_sessions/{session_id}/parts` | [Official Spec](https://developer.box.com/reference/get-files-upload-sessions-id-parts) |
| 最終コミット（結合） | `POST` | `https://upload.box.com/api/2.0/files/upload_sessions/{session_id}/commit` | [Official Spec](https://developer.box.com/reference/post-files-upload-sessions-id-commit) |
| セッション破棄 | `DELETE` | `https://upload.box.com/api/2.0/files/upload_sessions/{session_id}` | [Official Spec](https://developer.box.com/reference/delete-files-upload-sessions-id) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 1. セッション初期化]
curl -s -X POST "https://upload.box.com/api/2.0/files/upload_sessions" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "folder_id": "0",
       "file_size": 104857600,
       "file_name": "data_dump_100MB.tar.gz"
     }'
```

```bash [PUT 2. パート送信]
curl -s -X PUT "https://upload.box.com/api/2.0/files/upload_sessions/D3A1B2C3D4/part" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Range: bytes 0-8388607/104857600" \
     -H "Digest: sha=FPuS8b...base64sha1==" \
     -H "Content-Type: application/octet-stream" \
     --data-binary @part_0.bin
```

```bash [POST 3. 結合コミット]
curl -s -X POST "https://upload.box.com/api/2.0/files/upload_sessions/D3A1B2C3D4/commit" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Digest: sha=OverallSha1Base64==" \
     -H "Content-Type: application/json" \
     -d '{
       "parts": [
         { "part_id": "01", "offset": 0, "size": 8388608, "sha1": "FPuS8b..." }
       ]
     }'
```
:::

#### 要素4：アンチパターンと回避策
> [!CAUTION] **パートサイズの一致と Digest チェック**
> 各パートのサイズは、セッション初期化時に返される `part_size`（通常 8MB）と厳密に一致させる必要があります（最終パートを除く）。各パートには Base64 形式の SHA-1 Digest ヘッダーが必要です。

---

### 07. Downloads

#### 要素1：技術的本質と中核能力
実体ファイルの**バイナリストリーム**をダウンロードします。本 API は大容量トラフィックを効率化するため、直ちにバイト列を返さず `302 Found` リダイレクトにより最寄りのエッジ CDN URL へ誘導します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| ファイルコンテンツ取得 | `GET` | `/files/{file_id}/content` | [Official Spec](https://developer.box.com/reference/get-files-id-content) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [GET リダイレクト追従ダウンロード]
curl -L -X GET "https://api.box.com/2.0/files/123456789/content" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -o "./downloaded_file.parquet"
```
:::

#### 要素4：アンチパターンと回避策
> [!WARNING] **リダイレクト先へのトークン漏洩防止**
> 302 リダイレクト先は署名付き CDN URL です。クライアントライブラリを使用する際、Box の Bearer トークンを CDN ドメインに透過送信しないよう注意してください。

---

### 08. Zip Downloads

#### 要素1：技術的本質と中核能力
複数ファイルやディレクトリツリーを**非同期で単一 Zip アーカイブに圧縮**し、一括ダウンロードする機能です。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| Zip 作成要求 | `POST` | `/zip_downloads` | [Official Spec](https://developer.box.com/reference/post-zip-downloads) |
| ステータス確認 | `GET` | `/zip_downloads/{id}/status` | [Official Spec](https://developer.box.com/reference/get-zip-downloads-id-status) |
| Zip ダウンロード | `GET` | `https://dl.boxcloud.com/2.0/zip_downloads/{id}/content` | [Official Spec](https://developer.box.com/reference/get-zip-downloads-id-content) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 作成要求]
curl -s -X POST "https://api.box.com/2.0/zip_downloads" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "download_file_name": "batch_export_2026.zip",
       "items": [
         { "type": "file", "id": "123456" }
       ]
     }'
```

```bash [GET ダウンロード]
curl -L -X GET "https://dl.boxcloud.com/2.0/zip_downloads/z1a2b3/content" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -o "./batch_export_2026.zip"
```
:::

#### 要素4：アンチパターンと回避策
> [!CAUTION] **上限制限（10,000 ファイル / 32GB）**
> 1 回のリクエストで圧縮可能なアイテム数は最大 10,000 個、解凍前合計サイズは最大 32GB です。

---

### 09. Folder Locks

#### 要素1：技術的本質と中核能力
データパイプライン処理中などに、他ユーザーによるフォルダの削除や移動を防止する**排他ロック機能**です。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| ロック一覧取得 | `GET` | `/folder_locks?folder_id={folder_id}` | [Official Spec](https://developer.box.com/reference/get-folder-locks) |
| フォルダロック設定 | `POST` | `/folder_locks` | [Official Spec](https://developer.box.com/reference/post-folder-locks) |
| フォルダロック解除 | `DELETE` | `/folder_locks/{folder_lock_id}` | [Official Spec](https://developer.box.com/reference/delete-folder-locks-id) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [POST ロック設定]
curl -s -X POST "https://api.box.com/2.0/folder_locks" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "folder": { "type": "folder", "id": "987654321" },
       "locked_operations": { "move": true, "delete": true }
     }'
```

```bash [DELETE ロック解除]
curl -s -X DELETE "https://api.box.com/2.0/folder_locks/889900" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素4：アンチパターンと回避策
> [!IMPORTANT] **ロック解除の権限境界**
> 作成者本人または管理者権限を持つアカウントでのみロック解除が可能です。

---

### 10. Collections

#### 要素1：技術的本質と中核能力
「お気に入り」等に代表される**仮想グルーピング**です。物理的な配置ツリーを変更せずインデックスを作成します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| コレクション一覧 | `GET` | `/collections` | [Official Spec](https://developer.box.com/reference/get-collections) |
| 配下アイテム一覧 | `GET` | `/collections/{collection_id}/items` | [Official Spec](https://developer.box.com/reference/get-collections-id-items) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 一覧照会]
curl -s -X GET "https://api.box.com/2.0/collections" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素4：アンチパターンと回避策
> [!NOTE] **アイテム追加はファイル側の PUT を使用**
> コレクションへの追加は、対象ファイルに対して `PUT /files/{id}` を実行し `collections` フィールドを更新します。

---

### 11. Recent items

#### 要素1：技術的本質と中核能力
実行ユーザーが最近アクセス・変更したアイテムの一覧を**時系列で取得**します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 最近のアイテム照会 | `GET` | `/recent_items` | [Official Spec](https://developer.box.com/reference/get-recent-items) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 履歴照会]
curl -s -X GET "https://api.box.com/2.0/recent_items?limit=20" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素4：アンチパターンと回避策
> [!WARNING] **監査ログ用途には非推奨**
> 数分程度の反映遅延があるため、完全な監査が必要な場合は Enterprise Events API を利用してください。

---

### 12. Transfer folders

#### 要素1：技術的本質と中核能力
退職時などに、特定ユーザーのルートディレクトリ配下の全データを別ユーザーへ**一括所有権移転**します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| フォルダ所有権移譲 | `PUT` | `/users/{user_id}/folders/0` | [Official Spec](https://developer.box.com/reference/put-users-id-folders-0) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [PUT 所有権移譲]
curl -s -X PUT "https://api.box.com/2.0/users/11223344/folders/0" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{ "owned_by": { "id": "99887766" } }'
```
:::

#### 要素4：アンチパターンと回避策
> [!CAUTION] **管理者権限必須かつ不可逆**
> 実行には管理者権限が必要です。また移譲先ユーザーの容量上限に注意してください。

---

### 13. Web links

#### 要素1：技術的本質と中核能力
Box フォルダ内に**外部 URL へのポインタノード**を設置します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| リンク作成 | `POST` | `/web_links` | [Official Spec](https://developer.box.com/reference/post-web-links) |
| リンク取得 | `GET` | `/web_links/{web_link_id}` | [Official Spec](https://developer.box.com/reference/get-web-links-id) |
| リンク削除 | `DELETE` | `/web_links/{web_link_id}` | [Official Spec](https://developer.box.com/reference/delete-web-links-id) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [POST リンク作成]
curl -s -X POST "https://api.box.com/2.0/web_links" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://docs.snowflake.com",
       "parent": { "id": "0" },
       "name": "Snowflake Docs"
     }'
```
:::

#### 要素4：アンチパターンと回避策
> [!NOTE] **URL スキーム必須**
> `https://` や `http://` が必須です。

---

### 14. App item associations

#### 要素1：技術的本質と中核能力
ファイルやフォルダと外部 SaaS アプリケーション間の**連携メタデータ関係**を管理します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| ファイルのアプリ紐付け照会 | `GET` | `/files/{file_id}/app_item_associations` | [Official Spec](https://developer.box.com/reference/get-files-id-app-item-associations) |
| フォルダのアプリ紐付け照会 | `GET` | `/folders/{folder_id}/app_item_associations` | [Official Spec](https://developer.box.com/reference/get-folders-id-app-item-associations) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 照会]
curl -s -X GET "https://api.box.com/2.0/files/123456789/app_item_associations" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素4：アンチパターンと回避策
> [!WARNING] **アプリ認証前提**
> Box Admin Console で連携が許可されていない場合、常に空リストが返されます。

---

### 15. Trashed files

#### 要素1：技術的本質と中核能力
通常削除によって**ごみ箱に入ったファイル**の確認、復元、完全抹消を制御します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| ごみ箱ファイル取得 | `GET` | `/files/{file_id}/trash` | [Official Spec](https://developer.box.com/reference/get-files-id-trash) |
| ファイル復元 | `POST` | `/files/{file_id}` | [Official Spec](https://developer.box.com/reference/post-files-id) |
| 完全消去 | `DELETE` | `/files/{file_id}/trash` | [Official Spec](https://developer.box.com/reference/delete-files-id-trash) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 復元]
curl -s -X POST "https://api.box.com/2.0/files/123456789" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{}'
```

```bash [DELETE 完全削除]
curl -s -X DELETE "https://api.box.com/2.0/files/123456789/trash" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素4：アンチパターンと回避策
> [!CAUTION] **同名ファイル衝突時の 409 Conflict**
> 削除中に元の場所に同名ファイルが作られた場合、復元時に `409` となります。POST の Body で別の `parent` や `name` を指定してください。

---

### 16. Trashed folders

#### 要素1：技術的本質と中核能力
ごみ箱内の**フォルダツリー全体の復元および完全物理抹消**を管理します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| ごみ箱フォルダ取得 | `GET` | `/folders/{folder_id}/trash` | [Official Spec](https://developer.box.com/reference/get-folders-id-trash) |
| フォルダツリー復元 | `POST` | `/folders/{folder_id}` | [Official Spec](https://developer.box.com/reference/post-folders-id) |
| 完全消去 | `DELETE` | `/folders/{folder_id}/trash` | [Official Spec](https://developer.box.com/reference/delete-folders-id-trash) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [POST フォルダ復元]
curl -s -X POST "https://api.box.com/2.0/folders/987654321" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{}'
```
:::

#### 要素4：アンチパターンと回避策
> [!WARNING] **非同期クリーンアップ**
> 巨大フォルダの物理削除はバックグラウンドで行われます。

---

### 17. Trashed items

#### 要素1：技術的本質と中核能力
ごみ箱内の全アイテム（ファイル・フォルダ・リンク）を**横断的にページング一覧取得**します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| ごみ箱一覧取得 | `GET` | `/folders/trash/items` | [Official Spec](https://developer.box.com/reference/get-folders-trash-items) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 一覧取得]
curl -s -X GET "https://api.box.com/2.0/folders/trash/items?limit=100" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素4：アンチパターンと回避策
> [!NOTE] **保持期間満了による自動パージ**
> 管理ポリシー（例: 30日）を過ぎたものは自動で完全削除されます。

---

### 18. Trashed web links

#### 要素1：技術的本質と中核能力
ごみ箱に入った**外部リンクの復元および完全抹消**です。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| リンク取得 | `GET` | `/web_links/{web_link_id}/trash` | [Official Spec](https://developer.box.com/reference/get-web-links-id-trash) |
| リンク復元 | `POST` | `/web_links/{web_link_id}` | [Official Spec](https://developer.box.com/reference/post-web-links-id) |
| リンク完全消去 | `DELETE` | `/web_links/{web_link_id}/trash` | [Official Spec](https://developer.box.com/reference/delete-web-links-id-trash) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 復元]
curl -s -X POST "https://api.box.com/2.0/web_links/778899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{}'
```
:::

#### 要素4：アンチパターンと回避策
> [!NOTE] **メタデータノードの即時反映**
> ストレージブロックの移動を伴わないため、復元は高速に完了します。

---

### 19. Archives

#### 要素1：技術的本質と中核能力
公式 v2025.0 仕様に基づく**コールドデータアーカイブ管理**です。アクセス頻度の低いデータを低コスト層へ隔離・保存します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| アーカイブ一覧照会 | `GET` | `/archives` | [Official Spec](https://developer.box.com/reference/v2025.0/get-archives) |
| アーカイブ新規作成 | `POST` | `/archives` | [Official Spec](https://developer.box.com/reference/v2025.0/post-archives) |
| アーカイブ設定更新 | `PUT` | `/archives/{archive_id}` | [Official Spec](https://developer.box.com/reference/v2025.0/put-archives-id) |
| アーカイブ解除 | `DELETE` | `/archives/{archive_id}` | [Official Spec](https://developer.box.com/reference/v2025.0/delete-archives-id) |

#### 要素3：ハンズオン実行例 (cURL)
::: code-group
```bash [POST アーカイブ作成]
curl -s -X POST "https://api.box.com/2.0/archives" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Cold_Tier_Backup_2026",
       "source_folder_id": "987654321"
     }'
```
:::

#### 要素4：アンチパターンと回避策
> [!CAUTION] **エンタープライズライセンス要件**
> 高度なアーカイブ機能を有効化しているテナントでのみ利用可能です。

---

## 8.5 実務チェックリスト

本番環境で Box API を安定運用するための「6重セルフチェック」：

```txt
┌──────────────────────────────────────────────────────────────┐
│                Box API 本番インテグレーション点検項目        │
├──────────────────────────────────────────────────────────────┤
│ [ ] 1. ドメイン振分け: 通常APIは api.box.com、アップロードは upload.box.com
│ [ ] 2. ルートディレクトリ: ルートIDは厳密に "0" を指定（"/" や "root" は不可）
│ [ ] 3. 大容量ファイル: 50MB 超過時は Chunked セッションプロトコルを採用
│ [ ] 4. 同時実行保護: 重要な更新処理には ETag と If-Match ヘッダーを使用
│ [ ] 5. 探索ページング: 大規模フォルダでは usemarker=true（カーソル方式）を採用
│ [ ] 6. 二段階削除境界: DELETE(ごみ箱移動) と /trash(完全物理削除) を明確に区別
└──────────────────────────────────────────────────────────────┘
```

