# 第08-4講：Box コア API 実践ガイド —— Search & Metadata（検索・メタデータ）

> **【技術ポジショニング】**
>
> コンテンツ全文検索と構造化属性グラフ：全文インデックス検索、カスタムメタデータスキーマ、フォルダカスケード継承とセキュリティ分類（Classification）。

> 📖 **Box 公式リファレンス・仕様ドキュメント**：
> - [Box API Reference - Search 検索 API 仕様](https://developer.box.com/reference/resources/search/)
> - [Box API Reference - Metadata テンプレートとインスタンス仕様](https://developer.box.com/reference/resources/metadata-template/)
> - [Box メタデータ属性設計とカスケード継承開発者ガイド](https://developer.box.com/guides/metadata/)
> - [Box 情報セキュリティ分類 (Classification) 公式ガイド](https://developer.box.com/guides/classifications/)

---

## 08-4.1 全景 CRUD 能力マトリックス

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
| **01** | **Search** | **全文検索・メタデータフィルタ・高度な属性クエリ**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Search for files and folders</span> | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [直達](#01-search) |
| **02** | **Metadata templates** | **カスタムメタデータスキーマの定義・更新・管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Define custom metadata schemas</span> | `manage_metadata` | ✅ | ✅ | ✅ | ✅ | [直達](#02-metadata-templates) |
| **03** | **Metadata instances (Files)** | **ファイルへのメタデータ付与・値更新・削除**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage metadata on files</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直達](#03-metadata-instances-files) |
| **04** | **Metadata instances (Folders)** | **フォルダへのメタデータ付与・値更新・削除**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage metadata on folders</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直達](#04-metadata-instances-folders) |
| **05** | **Metadata cascade policies** | **メタデータのフォルダ階層カスケード自動継承ポリシー**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Auto-apply metadata to folder contents</span> | `manage_metadata` | ✅ | ✅ | ❌ | ✅ | [直達](#05-metadata-cascade-policies) |
| **06** | **Classifications** | **セキュリティ分類（機密区分）スキーマの定義**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Define and manage security classifications</span> | `manage_metadata` | ✅ | ✅ | ✅ | ✅ | [直達](#06-classifications) |
| **07** | **Classifications on files** | **ファイルへのセキュリティ分類の適用・更新・解除**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply classifications to files</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直達](#07-classifications-on-files) |
| **08** | **Classifications on folders** | **フォルダへのセキュリティ分類適用と継承統制**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply classifications to folders</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直達](#08-classifications-on-folders) |
| **09** | **Metadata taxonomies** | **メタデータの階層型分類タクソノミー定義**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Organize metadata into hierarchical taxonomies</span> | `manage_metadata` | ✅ | ✅ | ✅ | ✅ | [直達](#09-metadata-taxonomies) |
| **10** | **Box query resources** | **SQLライクな構造化メタデータクエリ実行 (v2026.0)**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Query for Box items</span> | `root_readonly` | ❌ | ✅ | ❌ | ❌ | [直達](#10-box-query-resources) |
| **11** | **Box query insights** | **クエリパフォーマンスとコンテンツインサイト分析**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create insights for Box items</span> | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [直達](#11-box-query-insights) |

</div>

---

## 08-4.2 共通接続仕様と前提要件

本カテゴリの API を呼び出す際は、全クライアントで以下の通信契約を遵守します：

```txt
1. Base API URL:       https://api.box.com/2.0
2. 认证凭证 Header:    Authorization: Bearer <ACCESS_TOKEN>
3. 内容交互 Header:    Content-Type: application/json (OAuth 表单或上传除外)
4. 租户企业标识:       企业管理员上下文或 As-User: <USER_ID> 代理标头
```

---

## 08-4.3 各 API モジュール 5 要素詳細解説

### <span id="01-search">01. Search</span>

#### 要素1：技術的本質と中核能力
エンタープライズ全文検索エンジンです。キーワードによるコンテンツ検索、サイズ・更新日時・メタデータ値による複合フィルタを提供します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 执行全文与多条件复合检索 | `GET` | `/search` | [Official Spec](https://developer.box.com/reference/get-search) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query** | `query` | `string` | **否** | 搜索关键词（支持短语双引号精确匹配） |
| **Query** | `scope` | `enum` | **否** | 范围：'user_content' 或 'enterprise_content' |
| **Query** | `file_extensions` | `string` | **否** | 扩展名过滤（如 'parquet,csv'） |
| **Query** | `ancestor_folder_ids` | `string` | **否** | 限定在指定目录树下搜索 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 检索关键词]
curl -s -X GET "https://api.box.com/2.0/search?query=migration&file_extensions=parquet" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [GET 按目录范围搜]
curl -s -X GET "https://api.box.com/2.0/search?query=audit&ancestor_folder_ids=987654" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> インデックス遅延：作成直後のファイルは検索にヒットしない場合があります。即時検証には GET やイベントログを使用してください。

---

### <span id="02-metadata-templates">02. Metadata templates</span>

#### 要素1：技術的本質と中核能力
ビジネス属性を定義するスキーマ設計機能。文字列、数値、日付、単一・複数選択肢の型安全な定義を行います。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询企业定义的所有模板清单 | `GET` | `/metadata_templates/enterprise` | [Official Spec](https://developer.box.com/reference/get-metadata-templates-enterprise) |
| 创建新的元数据模板定义 | `POST` | `/metadata_templates/schema` | [Official Spec](https://developer.box.com/reference/post-metadata-templates-schema) |
| 获取特定模板的字段详情 | `GET` | `/metadata_templates/{scope}/{template_key}/schema` | [Official Spec](https://developer.box.com/reference/get-metadata-templates-id-id-schema) |
| 通过 JSON Patch 增删改字段 | `PUT` | `/metadata_templates/{scope}/{template_key}/schema` | [Official Spec](https://developer.box.com/reference/put-metadata-templates-id-id-schema) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `scope` | `string` | **是** | 命名空间（通常为 'enterprise'） |
| **Path** | `template_key` | `string` | **是** | 模板全局唯一标识键 |
| **Body (POST)** | `displayName` | `string` | **是** | 模板人类可读展示名称 |
| **Body (POST)** | `fields` | `array` | **是** | 字段数组（包含 type, key, displayName） |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 创建模板]
curl -s -X POST "https://api.box.com/2.0/metadata_templates/schema" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"scope": "enterprise", "templateKey": "lakeSyncMeta", "displayName": "数据湖同步元数据", "fields": [{"type": "string", "key": "sourceTable", "displayName": "源表名称"}, {"type": "float", "key": "batchId", "displayName": "批次号"}]}'
```

```bash [GET 查模板结构]
curl -s -X GET "https://api.box.com/2.0/metadata_templates/enterprise/lakeSyncMeta/schema" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 既存フィールドの物理削除不可：データ整合性保護のため、一度定義したフィールドを完全に消去することはできません（非表示化のみ可）。

---

### <span id="03-metadata-instances-files">03. Metadata instances (Files)</span>

#### 要素1：技術的本質と中核能力
ファイル実体にスキーマを割り当て、具体的な属性値を保存します。RFC 6902 JSON Patch による部分更新に対応します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 获取文件上挂载的元数据值 | `GET` | `/files/{file_id}/metadata/{scope}/{template_key}` | [Official Spec](https://developer.box.com/reference/get-files-id-metadata-id-id) |
| 向文件赋予初始元数据实例 | `POST` | `/files/{file_id}/metadata/{scope}/{template_key}` | [Official Spec](https://developer.box.com/reference/post-files-id-metadata-id-id) |
| 通过 JSON Patch 更新元数据属性 | `PUT` | `/files/{file_id}/metadata/{scope}/{template_key}` | [Official Spec](https://developer.box.com/reference/put-files-id-metadata-id-id) |
| 从文件上彻底移除元数据实例 | `DELETE` | `/files/{file_id}/metadata/{scope}/{template_key}` | [Official Spec](https://developer.box.com/reference/delete-files-id-metadata-id-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `file_id` | `string` | **是** | 目标文件唯一 ID |
| **Header (PUT)** | `Content-Type` | `string` | **是** | 必须指定为 'application/json-patch+json' |
| **Body (PUT)** | `op` | `string` | **是** | 操作指令：'add', 'replace', 'remove', 'test' |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 挂载元数据]
curl -s -X POST "https://api.box.com/2.0/files/123456/metadata/enterprise/lakeSyncMeta" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"sourceTable": "TRANSACTIONS", "batchId": 20261103}'
```

```bash [PUT Patch 更新属性]
curl -s -X PUT "https://api.box.com/2.0/files/123456/metadata/enterprise/lakeSyncMeta" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json-patch+json" \
     -d '[{"op": "replace", "path": "/batchId", "value": 20261104}]'
```

```bash [DELETE 解绑元数据]
curl -s -X DELETE "https://api.box.com/2.0/files/123456/metadata/enterprise/lakeSyncMeta" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> メディアタイプ指定ミス（415）：PUT 更新時はヘッダーに application/json-patch+json が必須です。

---

### <span id="04-metadata-instances-folders">04. Metadata instances (Folders)</span>

#### 要素1：技術的本質と中核能力
フォルダ自体にメタデータを保持させます。後述のカスケードポリシーの基準ノードとして機能します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 获取目录元数据 | `GET` | `/folders/{id}/metadata/{scope}/{template_key}` | [Official Spec](https://developer.box.com/reference/get-folders-id-metadata-id-id) |
| 在目录上创建元数据 | `POST` | `/folders/{id}/metadata/{scope}/{template_key}` | [Official Spec](https://developer.box.com/reference/post-folders-id-metadata-id-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `folder_id` | `string` | **是** | 目标目录 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 挂载目录元数据]
curl -s -X POST "https://api.box.com/2.0/folders/987654/metadata/enterprise/lakeSyncMeta" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"sourceTable": "CORE_LEDGER"}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 同一スキーマの重複付与不可：すでにインスタンスが存在する場合、再POSTは 409 になります。

---

### <span id="05-metadata-cascade-policies">05. Metadata cascade policies</span>

#### 要素1：技術的本質と中核能力
自動属性同期エンジン。フォルダに設定することで、配下に投入される全ファイルへメタデータを自動継承させます。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询租户下所有级联策略 | `GET` | `/metadata_cascade_policies` | [Official Spec](https://developer.box.com/reference/get-metadata-cascade-policies) |
| 创建新的元数据级联策略 | `POST` | `/metadata_cascade_policies` | [Official Spec](https://developer.box.com/reference/post-metadata-cascade-policies) |
| 解除并删除级联策略 | `DELETE` | `/metadata_cascade_policies/{id}` | [Official Spec](https://developer.box.com/reference/delete-metadata-cascade-policies-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `folder_id` | `string` | **是** | 施加级联策略的父目录 ID |
| **Body (POST)** | `scope` | `string` | **是** | 模板所属 scope（如 'enterprise'） |
| **Body (POST)** | `templateKey` | `string` | **是** | 被级联的元数据模板 Key |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 开启级联继承]
curl -s -X POST "https://api.box.com/2.0/metadata_cascade_policies" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"folder_id": "987654", "scope": "enterprise", "templateKey": "lakeSyncMeta"}'
```

```bash [GET 查级联策略]
curl -s -X GET "https://api.box.com/2.0/metadata_cascade_policies?folder_id=987654" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 前提要件：親フォルダ自体に当該メタデータが付与されていない場合、カスケードポリシーは作成できません。

---

### <span id="06-classifications">06. Classifications</span>

#### 要素1：技術的本質と中核能力
Box Shield の基本設定です。社内規定に応じたセキュリティ区分（公開、社内限定、極秘など）を定義します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询企业当前启用的密级字典 | `GET` | `/metadata_templates/enterprise/securityClassification-6VMVochwUWo/schema` | [Official Spec](https://developer.box.com/reference/get-metadata-templates-enterprise-securityclassification-6vmvochwuwo-schema) |
| 初始化企业安全密级定义 | `POST` | `/metadata_templates/enterprise/securityClassification-6VMVochwUWo/schema` | [Official Spec](https://developer.box.com/reference/post-metadata-templates-enterprise-securityclassification-6vmvochwuwo-schema) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `fields` | `array` | **是** | 密级标签选项列表 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查询密级清单]
curl -s -X GET "https://api.box.com/2.0/metadata_templates/enterprise/securityClassification-6VMVochwUWo/schema" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 固定テンプレート識別子：セキュリティ分類は Box 共通の固定識別子を使用します。

---

### <span id="07-classifications-on-files">07. Classifications on files</span>

#### 要素1：技術的本質と中核能力
ファイルに対して機密区分を刻印し、漏洩防止ポリシーやダウンロード制限を発動させます。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 获取文件当前密级 | `GET` | `/files/{id}/metadata/enterprise/securityClassification-6VMVochwUWo` | [Official Spec](https://developer.box.com/reference/get-files-id-metadata-enterprise-securityclassification-6vmvochwuwo) |
| 为文件设置密级 | `POST` | `/files/{id}/metadata/enterprise/securityClassification-6VMVochwUWo` | [Official Spec](https://developer.box.com/reference/post-files-id-metadata-enterprise-securityclassification-6vmvochwuwo) |
| 变更文件密级标签 | `PUT` | `/files/{id}/metadata/enterprise/securityClassification-6VMVochwUWo` | [Official Spec](https://developer.box.com/reference/put-files-id-metadata-enterprise-securityclassification-6vmvochwuwo) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `Box__Security__Classification__Key` | `string` | **是** | 密级名称（如 'Restricted'） |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 标记绝密]
curl -s -X POST "https://api.box.com/2.0/files/123456/metadata/enterprise/securityClassification-6VMVochwUWo" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"Box__Security__Classification__Key": "Restricted"}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 属性キーの厳密指定：キー名はアンダースコア2つの Box__Security__Classification__Key です。

---

### <span id="08-classifications-on-folders">08. Classifications on folders</span>

#### 要素1：技術的本質と中核能力
フォルダ単位で機密区分を設定し、格納されるデータの一括保護を行います。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 为目录设置安全密级 | `POST` | `/folders/{id}/metadata/enterprise/securityClassification-6VMVochwUWo` | [Official Spec](https://developer.box.com/reference/post-folders-id-metadata-enterprise-securityclassification-6vmvochwuwo) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `folder_id` | `string` | **是** | 目标目录 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 标记目录密级]
curl -s -X POST "https://api.box.com/2.0/folders/987654/metadata/enterprise/securityClassification-6VMVochwUWo" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"Box__Security__Classification__Key": "Confidential"}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> ダウングレード監視：機密度の引き下げ操作はセキュリティ監査ログに高リスクとして記録されます。

---

### <span id="09-metadata-taxonomies">09. Metadata taxonomies</span>

#### 要素1：技術的本質と中核能力
ツリー構造の多階層メタデータ定義を提供し、高度な分類とインデックス化を支援します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 获取元数据分类体系 | `GET` | `/metadata_templates/{scope}/{key}/taxonomies` | [Official Spec](https://developer.box.com/reference) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `template_key` | `string` | **是** | 关联模板 Key |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查分类树]
curl -s -X GET "https://api.box.com/2.0/metadata_templates/enterprise/lakeSyncMeta/taxonomies" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 孤立ノード防止：中間ノードを削除する際は事前に配下ノードを再配置してください。

---

### <span id="10-box-query-resources">10. Box query resources</span>

#### 要素1：技術的本質と中核能力
新世代のクエリAPI。SQLライクな構文でメタデータ属性を高速検索します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 提交元数据结构化查询 | `POST` | `/v2026.0/metadata_queries/execute_read` | [Official Spec](https://developer.box.com/reference/v2026.0/post-metadata-queries-execute-read) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 版本头：'2026.0' |
| **Body (POST)** | `from` | `string` | **是** | 查询目标模板（如 'enterprise_123.lakeSyncMeta'） |
| **Body (POST)** | `query` | `string` | **是** | 过滤表达式（如 'sourceTable = :tbl'） |
| **Body (POST)** | `query_params` | `object` | **是** | 参数值绑定映射 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 执行元数据 SQL 查]
curl -s -X POST "https://api.box.com/2.0/metadata_queries/execute_read" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2026.0" \
     -H "Content-Type: application/json" \
     -d '{"from": "enterprise_111222.lakeSyncMeta", "query": "sourceTable = :tbl", "query_params": {"tbl": "TRANSACTIONS"}}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> バインド変数必須：SQLインジェクション防止のため、必ずプレースホルダーを使用してパラメータ化してください。

---

### <span id="11-box-query-insights">11. Box query insights</span>

#### 要素1：技術的本質と中核能力
検索クエリの実行効率とメタデータ活用度をモニタリングします。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询检索洞察数据 | `GET` | `/v2026.0/query_insights` | [Official Spec](https://developer.box.com/reference) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 版本头：'2026.0' |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查洞察分析]
curl -s -X GET "https://api.box.com/2.0/query_insights" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2026.0"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 先行プレビュー：v2026.0 機能は早期アクセスプログラムでのみ利用可能です。

---

## 08-4.4 実務チェックリスト

```txt
┌──────────────────────────────────────────────────────────────┐
│             Box API 08-4 工业级集成自检清单             │
├──────────────────────────────────────────────────────────────┤
│ [ ] 1. インデックス遅延: 新規アップロード後の検索インデックス反映には 10〜60 秒の遅延があります
│ [ ] 2. メタデータスコープ: 自社テンプレートは enterprise_<id>、共通は global スコープ
│ [ ] 3. JSON Patch 準拠: メタデータ更新は RFC 6902 (add, replace, test) に準拠
│ [ ] 4. カスケード処理: 大規模フォルダへのポリシー適用は非同期ジョブで実行されます
│ [ ] 5. セキュリティ分類キー: Classification は固定テンプレートキーで管理されます
└──────────────────────────────────────────────────────────────┘
```
