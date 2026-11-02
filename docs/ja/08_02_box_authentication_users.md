# 第08-2講：Box コア API 実践ガイド —— Authentication & Users（認証・ユーザー管理）

> **【技術ポジショニング】**
>
> エンタープライズアイデンティティ統制：OAuth 2.0、JWT認証、ユーザー・グループ構成とセッション強制切断。業務前提を排除し、純粋な技術仕様と状態機を中心に解説します。

---

## 08-2.1 全景 CRUD 能力マトリックス

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
| **01** | **Authorization** | **OAuth 2.0 認証・トークン発行と失効処理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">OAuth 2.0 authorization and token management</span> | `root_readwrite` | ✅ | ✅ | ❌ | ❌ | [直達](#01-authorization) |
| **02** | **Users** | **エンタープライズユーザーのライフサイクル管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage users</span> | `manage_users` | ✅ | ✅ | ✅ | ✅ | [直達](#02-users) |
| **03** | **User avatars** | **ユーザーアバター画像の取得・アップロード・消去**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage user profile images</span> | `manage_users` | ✅ | ✅ | ❌ | ✅ | [直達](#03-user-avatars) |
| **04** | **Groups** | **ユーザーグループの作成・属性管理・組織分離**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage user groups</span> | `manage_groups` | ✅ | ✅ | ✅ | ✅ | [直達](#04-groups) |
| **05** | **Group memberships** | **グループメンバーシップの追加・役職変更・脱退**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage user membership in groups</span> | `manage_groups` | ✅ | ✅ | ✅ | ✅ | [直達](#05-group-memberships) |
| **06** | **Invites** | **エンタープライズへの新規ユーザー招待・進捗確認**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Invite users to join Box</span> | `manage_users` | ✅ | ✅ | ❌ | ❌ | [直達](#06-invites) |
| **07** | **Email aliases** | **ユーザーエイリアスメールの登録・確認・削除**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage user email aliases</span> | `manage_users` | ✅ | ✅ | ❌ | ✅ | [直達](#07-email-aliases) |
| **08** | **Session termination** | **緊急時のユーザー・グループセッション強制一括破棄**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Terminate user or group sessions</span> | `manage_users` | ❌ | ✅ | ❌ | ❌ | [直達](#08-session-termination) |
| **09** | **Device pinners** | **端末固定化（デバイスピニング）の照会と解除**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage device pinning for offline access</span> | `manage_enterprise` | ✅ | ❌ | ❌ | ✅ | [直達](#09-device-pinners) |
| **10** | **External Users** | **外部非管理ユーザーのアクセス統制と一括消去ジョブ**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage external user access</span> | `manage_users` | ✅ | ✅ | ❌ | ❌ | [直達](#10-external-users) |

</div>

---

## 08-2.2 共通接続仕様と前提要件

本カテゴリの API を呼び出す際は、全クライアントで以下の通信契約を遵守します：

```txt
1. Base API URL:       https://api.box.com/2.0
2. 认证凭证 Header:    Authorization: Bearer <ACCESS_TOKEN>
3. 内容交互 Header:    Content-Type: application/json (OAuth 表单或上传除外)
4. 租户企业标识:       企业管理员上下文或 As-User: <USER_ID> 代理标头
```

---

## 08-2.3 各 API モジュール 5 要素詳細解説

### <span id="01-authorization">01. Authorization</span>

#### 要素1：技術的本質と中核能力
Box プラットフォームの認証・認可プロトコルチェーンを管理します。標準 OAuth 2.0 認可コードフロー、JWT サービスアカウント認証、トークンのローテーションと明示的失効をサポートします。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 获取用户授权重定向 URL | `GET` | `/authorize` | [Official Spec](https://developer.box.com/reference/get-authorize) |
| 换取或刷新 Access / Refresh Token | `POST` | `/oauth2/token` | [Official Spec](https://developer.box.com/reference/post-oauth2-token) |
| 主动废弃指定 Token | `POST` | `/oauth2/revoke` | [Official Spec](https://developer.box.com/reference/post-oauth2-revoke) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query (Auth)** | `response_type` | `string` | **是** | 固定为 'code' |
| **Query (Auth)** | `client_id` | `string` | **是** | 应用唯一客户端标识 |
| **Body (Token)** | `grant_type` | `string` | **是** | 授权模式：'authorization_code' / 'refresh_token' / 'client_credentials' |
| **Body (Token)** | `code` | `string` | **否** | OAuth 重定向获取的一次性 Code |
| **Body (Token)** | `client_secret` | `string` | **是** | 客户端应用通信密钥 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 获取 Token]
curl -s -X POST "https://api.box.com/oauth2/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=authorization_code" \
     -d "code=AUTH_CODE_HERE" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET"
```

```bash [POST 刷新 Token]
curl -s -X POST "https://api.box.com/oauth2/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=refresh_token" \
     -d "refresh_token=YOUR_REFRESH_TOKEN" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET"
```

```bash [POST 吊销 Token]
curl -s -X POST "https://api.box.com/oauth2/revoke" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET" \
     -d "token=TOKEN_TO_REVOKE"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> リフレッシュトークン失効の競合：Refresh Token は1回使用すると即座に無効化され新しいトークンが発行されます。分散環境で並行リフレッシュが走ると 400 invalid_grant が返されます。必ず分散ロックを用いて直列化してください。

---

### <span id="02-users">02. Users</span>

#### 要素1：技術的本質と中核能力
テナント内の全アカウント実体の状態機を管理します。管理対象ユーザー（Managed User）や API 連携用の App User の作成、容量制限、凍結、完全削除を行います。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 分页查询企业租户用户列表 | `GET` | `/users` | [Official Spec](https://developer.box.com/reference/get-users) |
| 获取当前认证主体上下文详情 | `GET` | `/users/me` | [Official Spec](https://developer.box.com/reference/get-users-me) |
| 新建受管用户或 App User | `POST` | `/users` | [Official Spec](https://developer.box.com/reference/post-users) |
| 更新用户信息、角色、配额或状态 | `PUT` | `/users/{user_id}` | [Official Spec](https://developer.box.com/reference/put-users-id) |
| 删除或注销指定用户 | `DELETE` | `/users/{user_id}` | [Official Spec](https://developer.box.com/reference/delete-users-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `user_id` | `string` | **是** | 目标用户 ID（'me' 表示当前调用上下文） |
| **Body (POST)** | `name` | `string` | **是** | 用户姓名 |
| **Body (POST)** | `login` | `string` | **否** | 用户主登录邮箱（App User 可免填） |
| **Body (POST)** | `is_platform_access_only` | `boolean` | **否** | 是否创建纯 API App User |
| **Body (PUT)** | `status` | `enum` | **否** | 状态：'active', 'inactive', 'cannot_delete_edit' |
| **Body (PUT)** | `space_amount` | `int64` | **否** | 存储空间字节数配额上限 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查当前用户]
curl -s -X GET "https://api.box.com/2.0/users/me" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [POST 建新用户]
curl -s -X POST "https://api.box.com/2.0/users" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"name": "Dev_Engineer_01", "login": "dev01@example.com", "role": "coadmin"}'
```

```bash [PUT 封禁用户]
curl -s -X PUT "https://api.box.com/2.0/users/123456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"status": "inactive"}'
```

```bash [DELETE 彻底注销]
curl -s -X DELETE "https://api.box.com/2.0/users/123456?notify=false" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> ファイル残存時の削除不可：削除対象ユーザーの配下にデータが存在する場合、直接削除は 400 エラーになります。事前に資産を移行するか、URL に ?force=true を付加してください。

---

### <span id="03-user-avatars">03. User avatars</span>

#### 要素1：技術的本質と中核能力
ユーザーのプロフィール画像を管理します。バイナリストリームの取得、新規アップロードによる上書き、デフォルトへのリセットを行います。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 获取用户头像图片二进制流 | `GET` | `/users/{user_id}/avatar` | [Official Spec](https://developer.box.com/reference/get-users-id-avatar) |
| 上传或更新用户自定义头像 | `POST` | `/users/{user_id}/avatar` | [Official Spec](https://developer.box.com/reference/post-users-id-avatar) |
| 删除用户头像并恢复默认 | `DELETE` | `/users/{user_id}/avatar` | [Official Spec](https://developer.box.com/reference/delete-users-id-avatar) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `user_id` | `string` | **是** | 目标用户唯一标识符 |
| **FormData** | `pic` | `binary` | **是** | 上传的头像二进制图片流（jpg/png/gif） |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 提取头像]
curl -s -X GET "https://api.box.com/2.0/users/123456/avatar" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" -o avatar.png
```

```bash [POST 上传头像]
curl -s -X POST "https://api.box.com/2.0/users/123456/avatar" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -F pic=@./profile.png
```

```bash [DELETE 恢复默认]
curl -s -X DELETE "https://api.box.com/2.0/users/123456/avatar" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 画像サイズ制限：最大 1MB 以下の JPEG/PNG/GIF 形式のみ有効です。

---

### <span id="04-groups">04. Groups</span>

#### 要素1：技術的本質と中核能力
組織構造の論理マッピングを提供します。プロジェクトや部門ごとにグループを定義し、アクセス権限の一括付与・剥奪を可能にします。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 分页查询企业内所有用户组 | `GET` | `/groups` | [Official Spec](https://developer.box.com/reference/get-groups) |
| 创建新的企业用户组 | `POST` | `/groups` | [Official Spec](https://developer.box.com/reference/post-groups) |
| 获取指定用户组详情 | `GET` | `/groups/{group_id}` | [Official Spec](https://developer.box.com/reference/get-groups-id) |
| 修改用户组名称或邀请权限 | `PUT` | `/groups/{group_id}` | [Official Spec](https://developer.box.com/reference/put-groups-id) |
| 解散并删除用户组 | `DELETE` | `/groups/{group_id}` | [Official Spec](https://developer.box.com/reference/delete-groups-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `group_id` | `string` | **是** | 用户组唯一 ID |
| **Body (POST)** | `name` | `string` | **是** | 用户组名称（企业内唯一） |
| **Body (POST)** | `invitability_level` | `enum` | **否** | 邀请权限级别：'admins_only', 'admins_and_members', 'all_managed_users' |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 创建组]
curl -s -X POST "https://api.box.com/2.0/groups" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"name": "Data_Lake_Operators", "invitability_level": "admins_only"}'
```

```bash [GET 查所有组]
curl -s -X GET "https://api.box.com/2.0/groups?limit=50" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [PUT 修改组名]
curl -s -X PUT "https://api.box.com/2.0/groups/778899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"name": "Core_ETL_Engineers"}'
```

```bash [DELETE 删除组]
curl -s -X DELETE "https://api.box.com/2.0/groups/778899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> グループ名の重複：同一テナント内での名称重複は 409 Conflict を引き起こします。事前存在チェックが必須です。

---

### <span id="05-group-memberships">05. Group memberships</span>

#### 要素1：技術的本質と中核能力
ユーザーとグループ間の多対多リレーションを管理します。一般メンバーまたはグループ管理者の役職割り当てを行います。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询指定组下的所有组员 | `GET` | `/groups/{group_id}/memberships` | [Official Spec](https://developer.box.com/reference/get-groups-id-memberships) |
| 查询指定用户所属的所有组 | `GET` | `/users/{user_id}/memberships` | [Official Spec](https://developer.box.com/reference/get-users-id-memberships) |
| 将用户加入指定组 | `POST` | `/group_memberships` | [Official Spec](https://developer.box.com/reference/post-group-memberships) |
| 修改成员在组内的角色 | `PUT` | `/group_memberships/{id}` | [Official Spec](https://developer.box.com/reference/put-group-memberships-id) |
| 将用户从指定组中剔除 | `DELETE` | `/group_memberships/{id}` | [Official Spec](https://developer.box.com/reference/delete-group-memberships-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `group_membership_id` | `string` | **是** | 成员绑定记录唯一 ID |
| **Body (POST)** | `user.id` | `string` | **是** | 用户 ID |
| **Body (POST)** | `group.id` | `string` | **是** | 用户组 ID |
| **Body (POST/PUT)** | `role` | `enum` | **否** | 组内角色：'member' 或 'admin' |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 加入组]
curl -s -X POST "https://api.box.com/2.0/group_memberships" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"user": {"id": "123456"}, "group": {"id": "778899"}, "role": "member"}'
```

```bash [PUT 提拔为组管理]
curl -s -X PUT "https://api.box.com/2.0/group_memberships/gm_9988" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"role": "admin"}'
```

```bash [DELETE 移出组]
curl -s -X DELETE "https://api.box.com/2.0/group_memberships/gm_9988" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 重複登録時の 409 Conflict：登録済みユーザーの再追加は 409 になります。

---

### <span id="06-invites">06. Invites</span>

#### 要素1：技術的本質と中核能力
新規ユーザーの招致フローを管理します。メール招待を送信し、受諾ステータスを追跡します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 向指定邮箱发送企业入驻邀请函 | `POST` | `/invites` | [Official Spec](https://developer.box.com/reference/post-invites) |
| 查询指定邀请的审批与接受状态 | `GET` | `/invites/{invite_id}` | [Official Spec](https://developer.box.com/reference/get-invites-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `invite_id` | `string` | **是** | 邀请记录 ID |
| **Body (POST)** | `enterprise.id` | `string` | **是** | 目标企业租户 ID |
| **Body (POST)** | `actionable_by.login` | `string` | **是** | 被邀请者的登录邮箱 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 发出邀请]
curl -s -X POST "https://api.box.com/2.0/invites" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"enterprise": {"id": "111222"}, "actionable_by": {"login": "partner@vendor.com"}}'
```

```bash [GET 查邀请进度]
curl -s -X GET "https://api.box.com/2.0/invites/inv_456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 他社管理下アカウントの制約：他社エンタープライズに属するユーザーは直接受諾できません。

---

### <span id="07-email-aliases">07. Email aliases</span>

#### 要素1：技術的本質と中核能力
ユーザーのエイリアス（別名）メールアドレスを管理します。複数のアドレスでコラボレーション通知を受信可能にします。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询用户绑定的所有别名邮箱 | `GET` | `/users/{user_id}/email_aliases` | [Official Spec](https://developer.box.com/reference/get-users-id-email-aliases) |
| 为用户增加辅助别名邮箱 | `POST` | `/users/{user_id}/email_aliases` | [Official Spec](https://developer.box.com/reference/post-users-id-email-aliases) |
| 删除已绑定的指定别名邮箱 | `DELETE` | `/users/{user_id}/email_aliases/{alias_id}` | [Official Spec](https://developer.box.com/reference/delete-users-id-email-aliases-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `user_id` | `string` | **是** | 用户 ID |
| **Path** | `email_alias_id` | `string` | **是** | 别名记录唯一 ID |
| **Body (POST)** | `email` | `string` | **是** | 待绑定的新邮箱地址 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 列出别名]
curl -s -X GET "https://api.box.com/2.0/users/123456/email_aliases" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [POST 绑定别名]
curl -s -X POST "https://api.box.com/2.0/users/123456/email_aliases" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"email": "dev.backup@example.com"}'
```

```bash [DELETE 解绑别名]
curl -s -X DELETE "https://api.box.com/2.0/users/123456/email_aliases/ea_8899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> プライマリメールの削除不可：プライマリログインアドレスは直接削除できません。

---

### <span id="08-session-termination">08. Session termination</span>

#### 要素1：技術的本質と中核能力
資格情報漏洩や緊急退職時の即時セキュリティ対策。対象アカウントの全ブラウザ、Box Drive、モバイルのセッションを一括強制失効させます。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 批量强制终结指定用户的全部在线活跃会话 | `POST` | `/users/terminate_sessions` | [Official Spec](https://developer.box.com/reference/post-users-terminate-sessions) |
| 批量强制终结指定用户组下所有成员的会话 | `POST` | `/groups/terminate_sessions` | [Official Spec](https://developer.box.com/reference/post-groups-terminate-sessions) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `user_ids` | `string[]` | **是** | 强制注销的用户 ID 数组 |
| **Body (POST)** | `user_logins` | `string[]` | **否** | 强制注销的用户登录邮箱数组 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 强退用户会话]
curl -s -X POST "https://api.box.com/2.0/users/terminate_sessions" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"user_ids": ["123456", "987654"]}'
```

```bash [POST 强退整组会话]
curl -s -X POST "https://api.box.com/2.0/groups/terminate_sessions" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"group_ids": ["778899"]}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 非同期ステータス（202）：即時 202 が返りバックグラウンドで処理されます。完了確認は Events ストリームを監査してください。

---

### <span id="09-device-pinners">09. Device pinners</span>

#### 要素1：技術的本質と中核能力
端末アクセスの境界防御を提供します。端末の紛失・盗難・除籍時に、ピン留めされたデバイスを強制解除してアクセスを遮断します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 分页查询企业内所有被 Pin 绑定的设备清单 | `GET` | `/enterprises/{enterprise_id}/device_pinners` | [Official Spec](https://developer.box.com/reference/get-enterprises-id-device-pinners) |
| 查询单个设备的硬件标识与绑定详情 | `GET` | `/device_pinners/{id}` | [Official Spec](https://developer.box.com/reference/get-device-pinners-id) |
| 解除并删除指定设备的 Pin 信任关系 | `DELETE` | `/device_pinners/{id}` | [Official Spec](https://developer.box.com/reference/delete-device-pinners-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `enterprise_id` | `string` | **是** | 企业租户唯一标识符 |
| **Path** | `device_pinner_id` | `string` | **是** | 设备 Pin 记录唯一 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查企业绑定设备]
curl -s -X GET "https://api.box.com/2.0/enterprises/111222/device_pinners?direction=desc" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [DELETE 强制解绑设备]
curl -s -X DELETE "https://api.box.com/2.0/device_pinners/dp_5566" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> ポリシー前提：テナント設定でデバイスピニングが有効でない場合 403 になります。

---

### <span id="10-external-users">10. External Users</span>

#### 要素1：技術的本質と中核能力
v2025.0 仕様に基づく外部コラボレーターの統制機能です。外部ユーザーの共有アクセス権を一括剥奪するジョブを管理します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 提交批量删除外部协作者访问权的后台作业 | `POST` | `/v2025.0/external_users/delete_jobs` | [Official Spec](https://developer.box.com/reference/v2025.0/post-external-users-delete-jobs) |
| 轮询外部用户清理任务的执行状态 | `GET` | `/v2025.0/external_users/delete_jobs/{id}` | [Official Spec](https://developer.box.com/reference/v2025.0/get-external-users-delete-jobs-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 必须指定版本头：'2025.0' |
| **Body (POST)** | `user_ids` | `string[]` | **是** | 待清除访问权限的外部用户 ID 列表 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 提交清理作业]
curl -s -X POST "https://api.box.com/2.0/external_users/delete_jobs" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0" \
     -H "Content-Type: application/json" \
     -d '{"user_ids": ["ext_1122", "ext_3344"]}'
```

```bash [GET 查作业进度]
curl -s -X GET "https://api.box.com/2.0/external_users/delete_jobs/job_9988" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> アカウントの非物理消去：本機能は自社コンテンツへの紐付け解除であり、外部アカウント本体の削除ではありません。

---

## 08-2.4 実務チェックリスト

```txt
┌──────────────────────────────────────────────────────────────┐
│             Box API 08-2 工业级集成自检清单             │
├──────────────────────────────────────────────────────────────┤
│ [ ] 1. トークン排他制御: refresh_token はローテーションされるため分散ロックで直列化
│ [ ] 2. プライマリメール保護: ログイン用メールは直接削除不可。PUT で切り替え後に削除
│ [ ] 3. 資産残存時の削除: フォルダ所有ユーザーの削除は Transfer 移譲または force=true 必須
│ [ ] 4. グループ名一意性: 同一テナント内でグループ名はユニーク。事前存在チェック推奨
│ [ ] 5. 非同期セッション破棄: terminate_sessions は 202 応答後バックグラウンドで即時失効
│ [ ] 6. 外部ユーザー境界: 外部ユーザーのクリーンアップは共有権限の剥奪であり物理消去ではない
└──────────────────────────────────────────────────────────────┘
```
