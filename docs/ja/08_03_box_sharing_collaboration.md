# 第08-3講：Box コア API 実践ガイド —— Sharing & Collaboration（共有・コラボレーション）

> **【技術ポジショニング】**
>
> コラボレーション権限マトリックスと共有リンク：8段階のアクセスロール、パスワード保護付き共有リンク、ファイルコメントとタスク管理フローを完全網羅します。

---

## 08-3.1 全景 CRUD 能力マトリックス

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
| **01** | **Collaborations** | **コラボレーションの新規追加・ロール変更・共有解除**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage file/folder collaborations</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直達](#01-collaborations) |
| **02** | **Collaborations (List)** | **リソース・ユーザー・グループ単位のコラボレーション一覧照会**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">List collaborations for users, files, folders, and groups</span> | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [直達](#02-collaborations-list) |
| **03** | **Shared links (Files)** | **ファイル共有リンクの作成・パスワード設定・期限管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage shared links for files</span> | `root_readwrite` | ✅ | ❌ | ✅ | ✅ | [直達](#03-shared-links-files) |
| **04** | **Shared links (Folders)** | **フォルダ共有リンクの作成とアクセス制御**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage shared links for folders</span> | `root_readwrite` | ✅ | ❌ | ✅ | ✅ | [直達](#04-shared-links-folders) |
| **05** | **Shared links (Web Links)** | **外部リンク（Web Link）の共有リンク管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Access web links via shared links</span> | `root_readwrite` | ✅ | ❌ | ✅ | ✅ | [直達](#05-shared-links-web-links) |
| **06** | **Shared links (App Items)** | **アプリ連携アイテムの共有リンク解決**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Access app items via shared links</span> | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [直達](#06-shared-links-app-items) |
| **07** | **Comments** | **ファイルコメントの投稿・メンション・スレッド返信**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Add and manage comments on files</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直達](#07-comments) |
| **08** | **Tasks** | **ファイル承認タスクの作成・期限設定・進捗管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage file-based tasks</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直達](#08-tasks) |
| **09** | **Task assignments** | **タスクのユーザー割り当て・承認・却下アクション**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Assign tasks to users</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直達](#09-task-assignments) |
| **10** | **Domain restrictions for collaborations** | **外部共有の許可ドメインホワイトリスト統制**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Restrict collaborations to specific domains</span> | `manage_enterprise` | ✅ | ✅ | ❌ | ✅ | [直達](#10-domain-restrictions-collab) |
| **11** | **Domain restrictions (User exemptions)** | **ドメイン制限の特定ユーザー例外ポリシー**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Exempt users from domain restrictions</span> | `manage_enterprise` | ✅ | ✅ | ❌ | ✅ | [直達](#11-domain-restrictions-exemptions) |
| **12** | **Box Hubs** | **Box Hubs ナレッジポータルの作成・管理 (v2025.0)**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage Box Hubs</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直達](#12-box-hubs) |
| **13** | **Box Hub Items** | **Hubs ポータル内アイテムの配置・更新**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage items within Box Hubs</span> | `root_readwrite` | ✅ | ✅ | ❌ | ✅ | [直達](#13-box-hub-items) |
| **14** | **Box Hub Collaborations** | **Hubs ポータルの閲覧・編集権限コラボレーション**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage collaborations for Box Hubs</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直達](#14-box-hub-collaborations) |

</div>

---

## 08-3.2 共通接続仕様と前提要件

本カテゴリの API を呼び出す際は、全クライアントで以下の通信契約を遵守します：

```txt
1. Base API URL:       https://api.box.com/2.0
2. 认证凭证 Header:    Authorization: Bearer <ACCESS_TOKEN>
3. 内容交互 Header:    Content-Type: application/json (OAuth 表单或上传除外)
4. 租户企业标识:       企业管理员上下文或 As-User: <USER_ID> 代理标头
```

---

## 08-3.3 各 API モジュール 5 要素詳細解説

### <span id="01-collaborations">01. Collaborations</span>

#### 要素1：技術的本質と中核能力
Box のアクセス制御の根幹です。フォルダまたはファイルに対し、ユーザーやグループへ8段階のアクセスロールを割り当てます。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 在指定资源上新增协作者 | `POST` | `/collaborations` | [Official Spec](https://developer.box.com/reference/post-collaborations) |
| 查询单条协作记录详情 | `GET` | `/collaborations/{id}` | [Official Spec](https://developer.box.com/reference/get-collaborations-id) |
| 提升/降级协作者权限角色 | `PUT` | `/collaborations/{id}` | [Official Spec](https://developer.box.com/reference/put-collaborations-id) |
| 移除协作者访问权限 | `DELETE` | `/collaborations/{id}` | [Official Spec](https://developer.box.com/reference/delete-collaborations-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `collaboration_id` | `string` | **是** | 协作映射关系 ID |
| **Body (POST)** | `item.type` | `string` | **是** | 被共享资源类型：'folder' 或 'file' |
| **Body (POST)** | `item.id` | `string` | **是** | 目标目录或文件的唯一 ID |
| **Body (POST)** | `accessible_by.type` | `string` | **是** | 被赋权主体：'user' 或 'group' |
| **Body (POST)** | `accessible_by.id` | `string` | **否** | 主体 ID（或用 login 传递外部邮箱） |
| **Body (POST/PUT)** | `role` | `enum` | **是** | 角色：'editor', 'viewer', 'previewer', 'co-owner' 等 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 新增协作者]
curl -s -X POST "https://api.box.com/2.0/collaborations" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"item": {"type": "folder", "id": "987654"}, "accessible_by": {"type": "user", "id": "123456"}, "role": "editor"}'
```

```bash [PUT 角色降级]
curl -s -X PUT "https://api.box.com/2.0/collaborations/collab_8899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"role": "viewer"}'
```

```bash [DELETE 移除协作]
curl -s -X DELETE "https://api.box.com/2.0/collaborations/collab_8899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> ウォーターフォール型権限継承：親フォルダで付与された権限は全配下アイテムへ自動継承され、子フォルダ側で権限を縮小することは不可能です。機密データは別階層へ分離してください。

---

### <span id="02-collaborations-list">02. Collaborations (List)</span>

#### 要素1：技術的本質と中核能力
コラボレーション関係の横断検索。ファイル、フォルダ、特定ユーザー、グループ視点から権限付与状況を一覧抽出します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询指定目录上的全部协作者 | `GET` | `/folders/{id}/collaborations` | [Official Spec](https://developer.box.com/reference/get-folders-id-collaborations) |
| 查询指定文件上的全部协作者 | `GET` | `/files/{id}/collaborations` | [Official Spec](https://developer.box.com/reference/get-files-id-collaborations) |
| 查询指定用户组获赠的所有外部协同 | `GET` | `/groups/{id}/collaborations` | [Official Spec](https://developer.box.com/reference/get-groups-id-collaborations) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `id` | `string` | **是** | 目标资源对象的 ID |
| **Query** | `limit` | `integer` | **否** | 单页返回数量（默认 100） |
| **Query** | `marker` | `string` | **否** | 游标标记 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查目录协作者]
curl -s -X GET "https://api.box.com/2.0/folders/987654/collaborations?limit=100" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [GET 查文件协作者]
curl -s -X GET "https://api.box.com/2.0/files/123456/collaborations" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 明示的権限のみ取得：本エンドポイントは直接付与されたコラボレーションのみを返します。親から継承した権限は含まれません。

---

### <span id="03-shared-links-files">03. Shared links (Files)</span>

#### 要素1：技術的本質と中核能力
ファイル単位の共有リンクを管理します。オープン公開、社内限定、パスワード設定、ダウンロード制限、有効期限を柔軟に構成できます。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 通过更新 shared_link 属性创建/修改外链 | `PUT` | `/files/{file_id}` | [Official Spec](https://developer.box.com/reference/put-files-id) |
| 通过外链 URL 逆向检索对应文件对象 | `GET` | `/shared_items` | [Official Spec](https://developer.box.com/reference/get-shared-items) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `file_id` | `string` | **是** | 目标文件 ID |
| **Body (PUT)** | `shared_link.access` | `enum` | **否** | 权限：'open', 'company', 'collaborators' |
| **Body (PUT)** | `shared_link.password` | `string` | **否** | 访问密码 |
| **Body (PUT)** | `shared_link.unshared_at` | `string` | **否** | 失效时间戳（ISO 8601） |
| **Body (PUT)** | `shared_link.permissions.can_download` | `boolean` | **否** | 是否允许外链下载 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [PUT 生成公开下载外链]
curl -s -X PUT "https://api.box.com/2.0/files/123456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"shared_link": {"access": "open", "permissions": {"can_download": true}}}'
```

```bash [PUT 移除外链]
curl -s -X PUT "https://api.box.com/2.0/files/123456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"shared_link": null}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> リンク無効化時の null 指定：共有リンクを解除する際は、shared_link に null を明示的に渡す必要があります。{} では解除されません。

---

### <span id="04-shared-links-folders">04. Shared links (Folders)</span>

#### 要素1：技術的本質と中核能力
フォルダツリー全体に対する共有リンクを生成します。外部ユーザーによるディレクトリブラウジングと一括ダウンロードを制御します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 通过更新 shared_link 字段启用/更新目录外链 | `PUT` | `/folders/{folder_id}` | [Official Spec](https://developer.box.com/reference/put-folders-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `folder_id` | `string` | **是** | 目标目录 ID |
| **Body (PUT)** | `shared_link.access` | `enum` | **否** | 访问范围：'open' / 'company' |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [PUT 开启目录外链]
curl -s -X PUT "https://api.box.com/2.0/folders/987654" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"shared_link": {"access": "company"}}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 企業ポリシーの制限：テナントで外部共有が禁止されている場合、open を指定すると 403 エラーになります。

---

### <span id="05-shared-links-web-links">05. Shared links (Web Links)</span>

#### 要素1：技術的本質と中核能力
フォルダ内の Web リンクオブジェクトに対する外部共有を管理します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 配置 Web Link 节点的 shared_link 属性 | `PUT` | `/web_links/{id}` | [Official Spec](https://developer.box.com/reference/put-web-links-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `web_link_id` | `string` | **是** | Web Link 唯一 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [PUT 开启链接共享]
curl -s -X PUT "https://api.box.com/2.0/web_links/778899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"shared_link": {"access": "open"}}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> メタデータの転送：Webリンクの外れアクセス時は対象URLへリダイレクトされます。

---

### <span id="06-shared-links-app-items">06. Shared links (App Items)</span>

#### 要素1：技術的本質と中核能力
共有リンク経由でサードパーティアプリ連携アイテムを参照します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 提取外链关联的 App Item | `GET` | `/shared_items#app_items` | [Official Spec](https://developer.box.com/reference/get-shared-items) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `BoxApi` | `string` | **是** | 格式为 'shared_link=https://...' |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 逆向解析]
curl -s -X GET "https://api.box.com/2.0/shared_items" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "BoxApi: shared_link=https://app.box.com/s/xyz123"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 完全なURL指定：BoxApi ヘッダーには完全な共有リンクURLを指定してください。

---

### <span id="07-comments">07. Comments</span>

#### 要素1：技術的本質と中核能力
ファイルに紐付くディスカッション機能です。スレッド形式の返信や @ メンションによる通知をサポートします。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 拉取文件上的所有评论列表 | `GET` | `/files/{file_id}/comments` | [Official Spec](https://developer.box.com/reference/get-files-id-comments) |
| 在文件上发布新评论或回复 | `POST` | `/comments` | [Official Spec](https://developer.box.com/reference/post-comments) |
| 编辑已发布的评论正文 | `PUT` | `/comments/{id}` | [Official Spec](https://developer.box.com/reference/put-comments-id) |
| 删除指定评论 | `DELETE` | `/comments/{id}` | [Official Spec](https://developer.box.com/reference/delete-comments-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `comment_id` | `string` | **是** | 评论唯一 ID |
| **Body (POST)** | `item.type` | `string` | **是** | 固定为 'file' |
| **Body (POST)** | `item.id` | `string` | **是** | 被评论的文件 ID |
| **Body (POST)** | `message` | `string` | **是** | 评论内容（支持 @提及） |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 发送评论]
curl -s -X POST "https://api.box.com/2.0/comments" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"item": {"type": "file", "id": "123456"}, "message": "对账完成，校验无误！"}'
```

```bash [GET 查文件评论]
curl -s -X GET "https://api.box.com/2.0/files/123456/comments" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [DELETE 删评论]
curl -s -X DELETE "https://api.box.com/2.0/comments/cm_7788" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> フォルダへのコメント不可：コメントはファイルにのみ紐付け可能です。フォルダに対して実行すると 400 エラーになります。

---

### <span id="08-tasks">08. Tasks</span>

#### 要素1：技術的本質と中核能力
ファイルベースの承認ワークフローです。レビュー要求や完了確認タスクを定義し、期限を設定します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询文件绑定的所有任务 | `GET` | `/files/{file_id}/tasks` | [Official Spec](https://developer.box.com/reference/get-files-id-tasks) |
| 在文件上创建新任务 | `POST` | `/tasks` | [Official Spec](https://developer.box.com/reference/post-tasks) |
| 更新任务说明或到期时间 | `PUT` | `/tasks/{task_id}` | [Official Spec](https://developer.box.com/reference/put-tasks-id) |
| 删除指定任务 | `DELETE` | `/tasks/{task_id}` | [Official Spec](https://developer.box.com/reference/delete-tasks-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `task_id` | `string` | **是** | 任务唯一 ID |
| **Body (POST)** | `item.id` | `string` | **是** | 文件 ID |
| **Body (POST)** | `action` | `enum` | **否** | 动作类型：'review'（审核）或 'complete'（完成） |
| **Body (POST)** | `message` | `string` | **否** | 任务说明 |
| **Body (POST)** | `due_at` | `string` | **否** | 截止到期时间（ISO 8601） |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 创建审核任务]
curl -s -X POST "https://api.box.com/2.0/tasks" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"item": {"type": "file", "id": "123456"}, "action": "review", "message": "请复核本批次同步日志"}'
```

```bash [GET 查任务]
curl -s -X GET "https://api.box.com/2.0/files/123456/tasks" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> タスク作成と割り当ての分離：Task を作成しただけでは担当者に通知されません。Task assignments で担当者を割り当ててください。

---

### <span id="09-task-assignments">09. Task assignments</span>

#### 要素1：技術的本質と中核能力
タスクの実行者を管理します。担当者は承認（approved）または却下（rejected）を提出します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 将任务指派给指定用户 | `POST` | `/task_assignments` | [Official Spec](https://developer.box.com/reference/post-task-assignments) |
| 查询任务执行分配状态 | `GET` | `/task_assignments/{id}` | [Official Spec](https://developer.box.com/reference/get-task-assignments-id) |
| 更新审批结论（通过/驳回） | `PUT` | `/task_assignments/{id}` | [Official Spec](https://developer.box.com/reference/put-task-assignments-id) |
| 撤销任务指派 | `DELETE` | `/task_assignments/{id}` | [Official Spec](https://developer.box.com/reference/delete-task-assignments-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `task_assignment_id` | `string` | **是** | 分配记录 ID |
| **Body (POST)** | `task.id` | `string` | **是** | 关联的任务 ID |
| **Body (POST)** | `assign_to.id` | `string` | **是** | 被指派人用户 ID |
| **Body (PUT)** | `resolution_state` | `enum` | **否** | 结论：'approved', 'rejected', 'completed' |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 指派任务]
curl -s -X POST "https://api.box.com/2.0/task_assignments" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"task": {"type": "task", "id": "t_1122"}, "assign_to": {"id": "123456"}}'
```

```bash [PUT 提交审批通过]
curl -s -X PUT "https://api.box.com/2.0/task_assignments/ta_5566" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"resolution_state": "approved", "message": "校验一致，准予发布"}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> ステータス変更の不可逆性：一度 approved または rejected に完了したタスクは再変更できません。

---

### <span id="10-domain-restrictions-collab">10. Domain restrictions for collaborations</span>

#### 要素1：技術的本質と中核能力
情報漏洩防止のためのドメイン制限機能。信頼されたドメインのメールアドレスにのみコラボレーションを許可します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 列出所有受信任域名白名单 | `GET` | `/collaboration_whitelist_entries` | [Official Spec](https://developer.box.com/reference/get-collaboration-whitelist-entries) |
| 添加新的协同受信任域名 | `POST` | `/collaboration_whitelist_entries` | [Official Spec](https://developer.box.com/reference/post-collaboration-whitelist-entries) |
| 移除域名白名单 | `DELETE` | `/collaboration_whitelist_entries/{id}` | [Official Spec](https://developer.box.com/reference/delete-collaboration-whitelist-entries-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `id` | `string` | **是** | 白名单记录 ID |
| **Body (POST)** | `domain` | `string` | **是** | 域名（如 'partner-corp.com'） |
| **Body (POST)** | `direction` | `enum` | **是** | 方向：'inbound'（只进）, 'outbound'（只出）, 'both'（双向） |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 增白名单]
curl -s -X POST "https://api.box.com/2.0/collaboration_whitelist_entries" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"domain": "trusted-partner.com", "direction": "both"}'
```

```bash [GET 查白名单]
curl -s -X GET "https://api.box.com/2.0/collaboration_whitelist_entries" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 既存共有の非自動解除：新規にドメイン制限を適用しても、過去に共有済みのアイテムは自動解除されません。

---

### <span id="11-domain-restrictions-exemptions">11. Domain restrictions (User exemptions)</span>

#### 要素1：技術的本質と中核能力
特定の管理者やシステムアカウントに対して、ドメイン制限の例外を認可します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 列出所有豁免用户清单 | `GET` | `/collaboration_whitelist_exempt_targets` | [Official Spec](https://developer.box.com/reference/get-collaboration-whitelist-exempt-targets) |
| 增加豁免例外用户 | `POST` | `/collaboration_whitelist_exempt_targets` | [Official Spec](https://developer.box.com/reference/post-collaboration-whitelist-exempt-targets) |
| 撤销用户豁免权 | `DELETE` | `/collaboration_whitelist_exempt_targets/{id}` | [Official Spec](https://developer.box.com/reference/delete-collaboration-whitelist-exempt-targets-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `user.id` | `string` | **是** | 获得豁免权的用户 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 添加豁免]
curl -s -X POST "https://api.box.com/2.0/collaboration_whitelist_exempt_targets" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"user": {"id": "123456"}}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 監査対象：例外ユーザーは任意の外部アドレスと共有可能となるため、セキュリティ監視を強化してください。

---

### <span id="12-box-hubs">12. Box Hubs</span>

#### 要素1：技術的本質と中核能力
散在するコンテンツを集約するポータル機能です。Box AI と統合された社内ナレッジハブを構築します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询企业租户下的 Hubs 列表 | `GET` | `/v2025.0/hubs` | [Official Spec](https://developer.box.com/reference/v2025.0/get-hubs) |
| 创建新的知识门户 Hub | `POST` | `/v2025.0/hubs` | [Official Spec](https://developer.box.com/reference/v2025.0/post-hubs) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 必须指定版本头：'2025.0' |
| **Body (POST)** | `title` | `string` | **是** | Hub 门户大标题 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 创建 Hub]
curl -s -X POST "https://api.box.com/2.0/hubs" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0" \
     -H "Content-Type: application/json" \
     -d '{"title": "Engineering Knowledge Hub"}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> ライセンス前提：Hubs 機能が有効化されたテナントでのみ呼び出し可能です。

---

### <span id="13-box-hub-items">13. Box Hub Items</span>

#### 要素1：技術的本質と中核能力
Hubs にマウントするファイルやフォルダの関連付けを管理します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 获取 Hub 内挂载的内容条目 | `GET` | `/v2025.0/hubs/{id}/items` | [Official Spec](https://developer.box.com/reference/v2025.0/get-hubs-id-items) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `id` | `string` | **是** | Hub ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查 Hub 条目]
curl -s -X GET "https://api.box.com/2.0/hubs/hub_123/items" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 仮想参照：Hub からアイテムを解除しても、本体ファイルは削除されません。

---

### <span id="14-box-hub-collaborations">14. Box Hub Collaborations</span>

#### 要素1：技術的本質と中核能力
Hubs ポータル単位のアクセス制御リストを管理します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询 Hub 的协作者 | `GET` | `/v2025.0/hubs/{id}/collaborations` | [Official Spec](https://developer.box.com/reference/v2025.0/get-hubs-id-collaborations) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `id` | `string` | **是** | Hub 唯一 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查 Hub 协同]
curl -s -X GET "https://api.box.com/2.0/hubs/hub_123/collaborations" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> セキュリティ継承：ユーザーは元々アクセス権のあるコンテンツのみ Hub 上で閲覧可能です。

---

## 08-3.4 実務チェックリスト

```txt
┌──────────────────────────────────────────────────────────────┐
│             Box API 08-3 工业级集成自检清单             │
├──────────────────────────────────────────────────────────────┤
│ [ ] 1. コラボレーションロール: Editor、Viewer、Previewer 等のダウンロード・編集権限境界を区別
│ [ ] 2. 共有リンクの付与: リンク作成は別端点ではなく対象ファイルへの PUT リクエストで実行
│ [ ] 3. 重複コラボレーション: 同一リソースに対する同一ユーザーの重複登録は 409 Conflict
│ [ ] 4. ドメイン制限ポリシー: ドメインホワイトリスト設定下での未承認ドメイン招待は 403 エラー
│ [ ] 5. タスク完了ステータス: incomplete、approved、rejected の状態遷移を厳密に管理
│ [ ] 6. パスワード保護リンク: 参照時は BoxApi: shared_link_password ヘッダーを適切に透過
└──────────────────────────────────────────────────────────────┘
```
