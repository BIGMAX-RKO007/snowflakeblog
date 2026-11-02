# 第08-5講：Box コア API 実践ガイド —— Events & Webhooks（イベント監査・Webhook）

> **【技術ポジショニング】**
>
> イベント駆動型アーキテクチャとリアルタイム通知：ロングポーリングイベント、エンタープライズセキュリティ監査ストリーム、および署名検証付き Webhook v2 を徹底解剖します。

---

## 08-5.1 全景 CRUD 能力マトリックス

下表は本カテゴリにおける全モジュールの機能全景マトリックスです。各モジュールの HTTP メソッド対応状況および権限境界を示します。

<style>
.crud-matrix-wrapper table {
  width: 100% !important;
  display: table !important;
  font-size: 0.82rem;
}
.crud-matrix-wrapper th, .crud-matrix-wrapper td {
  padding: 6px 5px !important;
}
.crud-matrix-wrapper td code {
  font-size: 0.72rem !important;
  padding: 1px 3px !important;
}
</style>

<div class="crud-matrix-wrapper">

| 番号 | モジュール (Module) | 公式定義と日本語機能説明 | コアスコープ (Scope) | GET | POST | PUT | DEL | クイックジャンプ |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **01** | **Events** | **ロングポーリングイベントストリームと企業監査ログ取得**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Monitor Box events and activity</span> | `manage_events` | ✅ | ❌ | ❌ | ❌ | [直達](#01-events) |
| **02** | **Webhooks** | **リアルタイム Webhook 購読の作成・秘密鍵管理・検証**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Configure real-time event notifications</span> | `manage_webhooks` | ✅ | ✅ | ✅ | ✅ | [直達](#02-webhooks) |

</div>

---

## 08-5.2 共通接続仕様と前提要件

本カテゴリの API を呼び出す際は、全クライアントで以下の通信契約を遵守します：

```txt
1. Base API URL:       https://api.box.com/2.0
2. 认证凭证 Header:    Authorization: Bearer <ACCESS_TOKEN>
3. 内容交互 Header:    Content-Type: application/json (OAuth 表单或上传除外)
4. 租户企业标识:       企业管理员上下文或 As-User: <USER_ID> 代理标头
```

---

## 08-5.3 各 API モジュール 5 要素詳細解説

### <span id="01-events">01. Events</span>

#### 要素1：技術的本質と中核能力
Box の変更データキャプチャ（CDC）基盤です。ユーザー操作ログおよびセキュリティ監査イベントをストリーム形式でリアルタイム取得します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 拉取或长轮询事件流 | `GET` | `/events` | [Official Spec](https://developer.box.com/reference/get-events) |
| 获取长轮询服务器专用通道地址 | `OPTIONS` | `/events` | [Official Spec](https://developer.box.com/reference/options-events) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query** | `stream_type` | `enum` | **否** | 流类型：'all'（用户级）或 'admin_logs'（企业审计） |
| **Query** | `stream_position` | `string` | **否** | 起始游标（填 'now' 获取当前最新） |
| **Query** | `limit` | `integer` | **否** | 单次拉取最大事件数（最大 500） |
| **Query** | `event_type` | `string` | **否** | 按特定事件类型过滤（如 'UPLOAD,DOWNLOAD'） |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 探测长轮询通道]
curl -s -X OPTIONS "https://api.box.com/2.0/events" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [GET 消费企业审计流]
curl -s -X GET "https://api.box.com/2.0/events?stream_type=admin_logs&limit=500&stream_position=now" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> now 指定による過去ログ欠損：初回連携時に stream_position=now を渡すと過去ログがすべてスキップされます。初回は 0 または明示的タイムスタンプを指定してください。

---

### <span id="02-webhooks">02. Webhooks</span>

#### 要素1：技術的本質と中核能力
リアルタイムプッシュ通知機能。特定フォルダやファイルのイベント（FILE.UPLOADED等）を検知し、指定のエンドポイントへ即座に HTTP POST を送信します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询租户下所有已注册的 Webhooks | `GET` | `/webhooks` | [Official Spec](https://developer.box.com/reference/get-webhooks) |
| 注册新的资源事件监听钩子 | `POST` | `/webhooks` | [Official Spec](https://developer.box.com/reference/post-webhooks) |
| 修改目标回调地址或监听事件列表 | `PUT` | `/webhooks/{id}` | [Official Spec](https://developer.box.com/reference/put-webhooks-id) |
| 注销并删除 Webhook | `DELETE` | `/webhooks/{id}` | [Official Spec](https://developer.box.com/reference/delete-webhooks-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `webhook_id` | `string` | **是** | Webhook 唯一 ID |
| **Body (POST)** | `target.type` | `string` | **是** | 监听资源：'file' 或 'folder' |
| **Body (POST)** | `target.id` | `string` | **是** | 目标资源唯一 ID |
| **Body (POST)** | `address` | `string(URL)` | **是** | 业务端 HTTPS 接收回调公网 URL |
| **Body (POST)** | `triggers` | `string[]` | **是** | 触发事件数组（如 ['FILE.UPLOADED', 'FILE.DELETED']） |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 注册文件上传钩子]
curl -s -X POST "https://api.box.com/2.0/webhooks" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"target": {"type": "folder", "id": "987654"}, "address": "https://api.mycorp.com/hooks/box", "triggers": ["FILE.UPLOADED"]}'
```

```bash [GET 查所有钩子]
curl -s -X GET "https://api.box.com/2.0/webhooks" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [DELETE 移除钩子]
curl -s -X DELETE "https://api.box.com/2.0/webhooks/wh_1122" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> HTTPS 必須と自己署名証明書の禁止：Webhook 通知先はパブリックCA発行の有効な HTTPS エンドポイントである必要があります。

---

## 08-5.4 実務チェックリスト

```txt
┌──────────────────────────────────────────────────────────────┐
│             Box API 08-5 工业级集成自检清单             │
├──────────────────────────────────────────────────────────────┤
│ [ ] 1. ストリーム種別: ユーザー操作は stream_type=all、企業全体監査ログは admin_logs を指定
│ [ ] 2. カーソル永続化: 再起動時の欠損防止のため next_stream_position は外部DB等に永続化必須
│ [ ] 3. Webhook 署名検証: Box-Signature-Primary ヘッダーの HMAC-SHA256 署名を必ず検証
│ [ ] 4. レスポンス即時性: Webhook エンドポイントは 3 秒以内に 2xx を返す必要があります
│ [ ] 5. 接続多重度制限: admin_logs ストリームはクライアントごとに単一スレッドで消費
└──────────────────────────────────────────────────────────────┘
```
