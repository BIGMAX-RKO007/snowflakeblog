# 第08-8講：Box コア API 実践ガイド —— Administration & Compliance（管理・ガバナンス・コンプライアンス）

> **【技術ポジショニング】**
>
> エンタープライズ資産保全と統制：リテンション保持ポリシー、リーガルホールド、Shield 情報障壁（チャイニーズウォール）および動的電子透かしを徹底解説します。

> 📖 **Box 公式リファレンス・仕様ドキュメント**：
> - [Box API Reference - Retention Policies データ保持ポリシー仕様](https://developer.box.com/reference/resources/retention-policy/)
> - [Box API Reference - Legal Hold 法的証拠保全仕様](https://developer.box.com/reference/resources/legal-hold-policy/)
> - [Box データライフサイクル保持期間管理ガイド (Retention Policies Guide)](https://developer.box.com/guides/retention-policies/)
> - [Box 訴訟ホールド保全開発者ガイド (Legal Holds Guide)](https://developer.box.com/guides/legal-holds/)
> - [Box Shield 脅威保護・情報障壁開発者ガイド](https://developer.box.com/guides/shield/)

---

## 08-8.1 全景 CRUD 能力マトリックス

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
| **01** | **Retention policies** | **データ保持（リテンション）ポリシーの作成・ロック管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Define content retention policies</span> | `manage_retention` | ✅ | ✅ | ✅ | ✅ | [直達](#01-retention-policies) |
| **02** | **Retention policy assignments** | **リテンションポリシーのフォルダ・メタデータ・全社適用**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply retention policies to content</span> | `manage_retention` | ✅ | ✅ | ❌ | ✅ | [直達](#02-retention-policy-assignments) |
| **03** | **File version retentions** | **保持期間適用中のファイル世代一覧照会と監査**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage retention policies for file versions</span> | `manage_retention` | ✅ | ❌ | ❌ | ❌ | [直達](#03-file-version-retentions) |
| **04** | **Legal hold policies** | **訴訟ホールド（リーガルホールド）ポリシーの作成・凍結統制**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Define and manage legal hold policies</span> | `manage_legal_holds` | ✅ | ✅ | ✅ | ✅ | [直達](#04-legal-hold-policies) |
| **05** | **Legal hold policy assignments** | **リーガルホールドの対象ユーザー・フォルダ割り当て**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply legal hold policies to content</span> | `manage_legal_holds` | ✅ | ✅ | ❌ | ✅ | [直達](#05-legal-hold-policy-assignments) |
| **06** | **File version legal holds** | **法的保護下にある特定バージョン証拠の照会**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply legal holds to specific file versions</span> | `manage_legal_holds` | ✅ | ❌ | ❌ | ❌ | [直達](#06-file-version-legal-holds) |
| **07** | **Shield information barriers** | **Box Shield 情報障壁（チャイニーズウォール）全体の統制**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Implement information barriers for compliance</span> | `manage_shield` | ✅ | ✅ | ❌ | ❌ | [直達](#07-shield-information-barriers) |
| **08** | **Shield information barrier segments** | **情報障壁セグメント（部門グループ）の作成と管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage barrier segments</span> | `manage_shield` | ✅ | ✅ | ✅ | ✅ | [直達](#08-shield-segments) |
| **09** | **Shield information barrier segment members** | **セグメントへのユーザー割り当て統制**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage users in barrier segments</span> | `manage_shield` | ✅ | ✅ | ❌ | ✅ | [直達](#09-shield-segment-members) |
| **10** | **Shield information barrier segment restrictions** | **セグメント間の通信・共有制限ルールの定義**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Define restrictions between segments</span> | `manage_shield` | ✅ | ✅ | ❌ | ✅ | [直達](#10-shield-segment-restrictions) |
| **11** | **Shield information barrier reports** | **情報障壁の監査レポート自動生成**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Generate reports on information barriers</span> | `manage_shield` | ✅ | ✅ | ❌ | ❌ | [直達](#11-shield-reports) |
| **12** | **Watermarks (Files)** | **ファイルへの動的電子透かし付与・照会・解除**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply watermarks to files</span> | `root_readwrite` | ✅ | ❌ | ✅ | ✅ | [直達](#12-watermarks-files) |
| **13** | **Watermarks (Folders)** | **フォルダ階層への電子透かし一括適用**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply watermarks to folders</span> | `root_readwrite` | ✅ | ❌ | ✅ | ✅ | [直達](#13-watermarks-folders) |
| **14** | **Standard and Zones Storage Policies** | **Box Zones データ主権・保管リージョンポリシー管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage storage location policies</span> | `manage_enterprise` | ✅ | ❌ | ❌ | ❌ | [直達](#14-storage-policies) |
| **15** | **Standard and Zones Storage Policy Assignments** | **ユーザーへの保管リージョン割り当て**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Assign storage policies to users</span> | `manage_enterprise` | ✅ | ✅ | ✅ | ✅ | [直達](#15-storage-policy-assignments) |
| **16** | **Terms of service** | **利用規約（Terms of Service）の策定・有効化**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Define enterprise terms of service</span> | `manage_enterprise` | ✅ | ✅ | ✅ | ❌ | [直達](#16-terms-of-service) |
| **17** | **Terms of service user statuses** | **ユーザーの利用規約同意ステータス追跡・代行同意**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Track user acceptance of terms</span> | `manage_enterprise` | ✅ | ✅ | ✅ | ❌ | [直達](#17-terms-of-service-user-statuses) |
| **18** | **Integration mappings** | **外部 SaaS（Slack 等）とのユーザーIDマッピング**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Map Box users to external integrations</span> | `manage_enterprise` | ✅ | ✅ | ✅ | ✅ | [直達](#18-integration-mappings) |
| **19** | **Enterprise Configurations** | **全社セキュリティ・共有ポリシーの構成設定**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Configure enterprise-wide settings</span> | `manage_enterprise` | ✅ | ❌ | ✅ | ❌ | [直達](#19-enterprise-configurations) |
| **20** | **Shield lists** | **Box Shield アクセス制御リスト・地理フェンス管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage access control lists</span> | `manage_shield` | ✅ | ✅ | ✅ | ✅ | [直達](#20-shield-lists) |

</div>

---

## 08-8.2 共通接続仕様と前提要件

本カテゴリの API を呼び出す際は、全クライアントで以下の通信契約を遵守します：

```txt
1. Base API URL:       https://api.box.com/2.0
2. 认证凭证 Header:    Authorization: Bearer <ACCESS_TOKEN>
3. 内容交互 Header:    Content-Type: application/json (OAuth 表单或上传除外)
4. 租户企业标识:       企业管理员上下文或 As-User: <USER_ID> 代理标头
```

---

## 08-8.3 各 API モジュール 5 要素詳細解説

### <span id="01-retention-policies">01. Retention policies</span>

#### 要素1：技術的本質と中核能力
法令遵守（リテンション）のためのデータ保持ポリシー管理です。保持期間（日数または無期限）および満了時アクション（完全消去または解除）を設定します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询租户下所有保留策略 | `GET` | `/retention_policies` | [Official Spec](https://developer.box.com/reference/get-retention-policies) |
| 创建新的合规保留策略 | `POST` | `/retention_policies` | [Official Spec](https://developer.box.com/reference/post-retention-policies) |
| 获取特定策略详情 | `GET` | `/retention_policies/{id}` | [Official Spec](https://developer.box.com/reference/get-retention-policies-id) |
| 更新策略（或永久锁定为不可逆状态） | `PUT` | `/retention_policies/{id}` | [Official Spec](https://developer.box.com/reference/put-retention-policies-id) |
| 删除未锁定的策略 | `DELETE` | `/retention_policies/{id}` | [Official Spec](https://developer.box.com/reference/delete-retention-policies-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `policy_name` | `string` | **是** | 保留策略名称 |
| **Body (POST)** | `policy_type` | `enum` | **是** | 类型：'finite'（有期限）或 'indefinite'（永久） |
| **Body (POST)** | `retention_length` | `int64` | **否** | 保留天数（当 finite 时必填） |
| **Body (POST)** | `disposition_action` | `enum` | **是** | 到期动作：'permanently_delete' 或 'remove_retention' |
| **Body (PUT)** | `status` | `string` | **否** | 设置为 'locked' 触发绝对不可逆锁定 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 创建 7 年保留策略]
curl -s -X POST "https://api.box.com/2.0/retention_policies" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"policy_name": "Financial_7Year_Retention", "policy_type": "finite", "retention_length": 2555, "disposition_action": "permanently_delete"}'
```

```bash [GET 查保留策略]
curl -s -X GET "https://api.box.com/2.0/retention_policies" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> ロック状態の不可逆性：status を locked に設定したポリシーは、いかなる管理者権限でも変更・削除できなくなります。

---

### <span id="02-retention-policy-assignments">02. Retention policy assignments</span>

#### 要素1：技術的本質と中核能力
作成したリテンションポリシーを特定のフォルダ、全社、またはメタデータ条件に対してバインドします。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询策略当前绑定的资源清单 | `GET` | `/retention_policies/{id}/assignments` | [Official Spec](https://developer.box.com/reference/get-retention-policies-id-assignments) |
| 将保留策略分配给目录或租户 | `POST` | `/retention_policy_assignments` | [Official Spec](https://developer.box.com/reference/post-retention-policy-assignments) |
| 解除保留策略绑定 | `DELETE` | `/retention_policy_assignments/{id}` | [Official Spec](https://developer.box.com/reference/delete-retention-policy-assignments-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `policy_id` | `string` | **是** | 保留策略 ID |
| **Body (POST)** | `assign_to.type` | `enum` | **是** | 范围类型：'folder', 'enterprise', 'metadata_template' |
| **Body (POST)** | `assign_to.id` | `string` | **否** | 目标目录 ID 或模板 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 绑定目录]
curl -s -X POST "https://api.box.com/2.0/retention_policy_assignments" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"policy_id": "rp_1122", "assign_to": {"type": "folder", "id": "987654"}}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 完全削除の拒絶：リテンション対象ファイルは期間満了まで物理削除できず、403 エラーとなります。

---

### <span id="03-file-version-retentions">03. File version retentions</span>

#### 要素1：技術的本質と中核能力
リテンションポリシーによって保護されている個別バージョンレコードを照会します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 分页查询处于保全状态的文件版本记录 | `GET` | `/file_version_retentions` | [Official Spec](https://developer.box.com/reference/get-file-version-retentions) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query** | `file_id` | `string` | **否** | 限定文件 ID |
| **Query** | `policy_id` | `string` | **否** | 限定策略 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查保全版本]
curl -s -X GET "https://api.box.com/2.0/file_version_retentions?limit=50" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 読み取り専用：満了日時の直接改ざんは不可能です。

---

### <span id="04-legal-hold-policies">04. Legal hold policies</span>

#### 要素1：技術的本質と中核能力
司法手続き・訴訟対応のための証拠保全機能。対象ユーザーやフォルダの全データは変更・削除操作に関わらず不変状態で凍結されます。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询所有司法保全策略 | `GET` | `/legal_hold_policies` | [Official Spec](https://developer.box.com/reference/get-legal-hold-policies) |
| 创建新的诉讼冻结保全策略 | `POST` | `/legal_hold_policies` | [Official Spec](https://developer.box.com/reference/post-legal-hold-policies) |
| 案件结案，解除冻结策略 | `DELETE` | `/legal_hold_policies/{id}` | [Official Spec](https://developer.box.com/reference/delete-legal-hold-policies-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `policy_name` | `string` | **是** | 诉讼案号或保全名称 |
| **Body (POST)** | `description` | `string` | **否** | 案情简述与法务备注 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 开启司法保全]
curl -s -X POST "https://api.box.com/2.0/legal_hold_policies" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"policy_name": "Case_2026_Audit_Hold", "description": "监管专项检查保全"}'
```

```bash [GET 查保全列表]
curl -s -X GET "https://api.box.com/2.0/legal_hold_policies" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> リテンションへの優先性：リテンション満了日を迎えたファイルであっても、リーガルホールド適用中は物理削除が強制保留されます。

---

### <span id="05-legal-hold-policy-assignments">05. Legal hold policy assignments</span>

#### 要素1：技術的本質と中核能力
特定の調査対象者（ユーザー）や機密フォルダに対して司法凍結を適用します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 施加冻结绑定 | `POST` | `/legal_hold_policy_assignments` | [Official Spec](https://developer.box.com/reference/post-legal-hold-policy-assignments) |
| 解除具体主体的冻结绑定 | `DELETE` | `/legal_hold_policy_assignments/{id}` | [Official Spec](https://developer.box.com/reference/delete-legal-hold-policy-assignments-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `policy_id` | `string` | **是** | 保全策略 ID |
| **Body (POST)** | `assign_to.type` | `enum` | **是** | 冻结对象类型：'user' 或 'folder' |
| **Body (POST)** | `assign_to.id` | `string` | **是** | 涉案用户 ID 或目录 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 冻结当事人]
curl -s -X POST "https://api.box.com/2.0/legal_hold_policy_assignments" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"policy_id": "lhp_123", "assign_to": {"type": "user", "id": "112233"}}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> サイレントバックグラウンド処理：大量データを抱えるユーザーへの適用は非同期で実行されます。

---

### <span id="06-file-version-legal-holds">06. File version legal holds</span>

#### 要素1：技術的本質と中核能力
司法ホールドにより保全された履歴バージョンをリスト化し、証拠保全監査に利用します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询处于冻结状态的文件版本 | `GET` | `/file_version_legal_holds` | [Official Spec](https://developer.box.com/reference/get-file-version-legal-holds) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query** | `policy_id` | `string` | **是** | 保全策略 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 提取保全证据版本]
curl -s -X GET "https://api.box.com/2.0/file_version_legal_holds?policy_id=lhp_123" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 証拠改ざん防止：対象バージョンの上書き・削除は不可です。

---

### <span id="07-shield-information-barriers">07. Shield information barriers</span>

#### 要素1：技術的本質と中核能力
利益相反防止のための情報障壁（チャイニーズウォール）を構築します。指定グループ間のデータ共有をシステム的に完全遮断します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 获取企业信息屏障规则 | `GET` | `/shield_information_barriers` | [Official Spec](https://developer.box.com/reference/get-shield-information-barriers) |
| 变更信息屏障激活状态 | `POST` | `/shield_information_barriers/change_status` | [Official Spec](https://developer.box.com/reference/post-shield-information-barriers-change-status) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `id` | `string` | **是** | 屏障 ID |
| **Body (POST)** | `status` | `enum` | **是** | 状态：'pending' / 'disabled' |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查信息屏障]
curl -s -X GET "https://api.box.com/2.0/shield_information_barriers" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> テナント単一インスタンス：Information Barrier は企業全体で1つのみ定義され、配下の Segment で詳細を制御します。

---

### <span id="08-shield-segments">08. Shield information barrier segments</span>

#### 要素1：技術的本質と中核能力
隔離対象となる部門やプロジェクトを定義するセグメントを作成します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 列出所有隔离分段 | `GET` | `/shield_information_barrier_segments` | [Official Spec](https://developer.box.com/reference/get-shield-information-barrier-segments) |
| 创建新的隔离分段 | `POST` | `/shield_information_barrier_segments` | [Official Spec](https://developer.box.com/reference/post-shield-information-barrier-segments) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `name` | `string` | **是** | 分段名称（如 'Investment_Banking'） |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 建隔离分段]
curl -s -X POST "https://api.box.com/2.0/shield_information_barrier_segments" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"shield_information_barrier": {"id": "bar_123"}, "name": "IB_Department"}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 親バリアへの紐付けが必須です。

---

### <span id="09-shield-segment-members">09. Shield information barrier segment members</span>

#### 要素1：技術的本質と中核能力
ユーザーを特定のセグメントへ配属します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 添加用户至分段 | `POST` | `/shield_information_barrier_segment_members` | [Official Spec](https://developer.box.com/reference) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `user.id` | `string` | **是** | 用户 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 分配用户入分段]
curl -s -X POST "https://api.box.com/2.0/shield_information_barrier_segment_members" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"shield_information_barrier_segment": {"id": "seg_123"}, "user": {"id": "123456"}}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 競合セグメントの重複所属は不可です。

---

### <span id="10-shield-segment-restrictions">10. Shield information barrier segment restrictions</span>

#### 要素1：技術的本質と中核能力
セグメント間のアクセス遮断ルールを有効化します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 添加阻断规则 | `POST` | `/shield_information_barrier_segment_restrictions` | [Official Spec](https://developer.box.com/reference) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `restricted_segment.id` | `string` | **是** | 被隔离的目标分段 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 配置隔离规则]
curl -s -X POST "https://api.box.com/2.0/shield_information_barrier_segment_restrictions" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"shield_information_barrier_segment": {"id": "seg_A"}, "restricted_segment": {"id": "seg_B"}, "type": "shield_information_barrier_segment_restriction"}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 制限は双方向に機能します。

---

### <span id="11-shield-reports">11. Shield information barrier reports</span>

#### 要素1：技術的本質と中核能力
障壁によって阻止された共有試行の監査ログレポートを出力します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 请求生成审计报告 | `POST` | `/shield_information_barrier_reports` | [Official Spec](https://developer.box.com/reference) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `shield_information_barrier.id` | `string` | **是** | 屏障 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 生成审计报表]
curl -s -X POST "https://api.box.com/2.0/shield_information_barrier_reports" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"shield_information_barrier": {"id": "bar_123"}}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> レポートは非同期でフォルダに出力されます。

---

### <span id="12-watermarks-files">12. Watermarks (Files)</span>

#### 要素1：技術的本質と中核能力
閲覧者のユーザー名と日時をファイルプレビューおよびPDFダウンロードに直接透かしとして焼き付けます。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询文件水印配置 | `GET` | `/files/{id}/watermark` | [Official Spec](https://developer.box.com/reference/get-files-id-watermark) |
| 为文件施加水印 | `PUT` | `/files/{id}/watermark` | [Official Spec](https://developer.box.com/reference/put-files-id-watermark) |
| 移除文件水印 | `DELETE` | `/files/{id}/watermark` | [Official Spec](https://developer.box.com/reference/delete-files-id-watermark) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `file_id` | `string` | **是** | 目标文件 ID |
| **Body (PUT)** | `watermark.imprint` | `string` | **是** | 固定为 'default' |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [PUT 开启文件水印]
curl -s -X PUT "https://api.box.com/2.0/files/123456/watermark" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"watermark": {"imprint": "default"}}'
```

```bash [DELETE 移除水印]
curl -s -X DELETE "https://api.box.com/2.0/files/123456/watermark" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> ダウンロードファイルへの影響：透かし設定時は変換後PDF等に印字されます。

---

### <span id="13-watermarks-folders">13. Watermarks (Folders)</span>

#### 要素1：技術的本質と中核能力
フォルダ全体に透かしを設定し、配下の全ドキュメントへ強制適用します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 在目录上开启水印 | `PUT` | `/folders/{id}/watermark` | [Official Spec](https://developer.box.com/reference/put-folders-id-watermark) |
| 在目录上解除水印 | `DELETE` | `/folders/{id}/watermark` | [Official Spec](https://developer.box.com/reference/delete-folders-id-watermark) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `folder_id` | `string` | **是** | 目标目录 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [PUT 开启目录整树水印]
curl -s -X PUT "https://api.box.com/2.0/folders/987654/watermark" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"watermark": {"imprint": "default"}}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 自動継承：配下ファイルへ一括自動適用されます。

---

### <span id="14-storage-policies">14. Standard and Zones Storage Policies</span>

#### 要素1：技術的本質と中核能力
GDPR 等のデータレジデンシー要件に適合。データを指定の物理リージョン（東京、欧州、米国等）に保管固定します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询企业租户可用存储区域列表 | `GET` | `/storage_policies` | [Official Spec](https://developer.box.com/reference/get-storage-policies) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query** | `limit` | `integer` | **否** | 返回数量限制 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查存储区域策略]
curl -s -X GET "https://api.box.com/2.0/storage_policies" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> Zones ライセンス必須：マルチゾーン構成は専用アドオンが必要です。

---

### <span id="15-storage-policy-assignments">15. Standard and Zones Storage Policy Assignments</span>

#### 要素1：技術的本質と中核能力
特定ユーザーが所有するデータの保管先リージョンを決定します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 为用户绑定存储区域 | `POST` | `/storage_policy_assignments` | [Official Spec](https://developer.box.com/reference/post-storage-policy-assignments) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `storage_policy_id` | `string` | **是** | 存储策略 ID |
| **Body (POST)** | `assigned_to.id` | `string` | **是** | 用户 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 分配区域]
curl -s -X POST "https://api.box.com/2.0/storage_policy_assignments" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"storage_policy_id": "sp_tokyo", "assigned_to": {"type": "user", "id": "123456"}}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 新規ファイルのみ適用：ポリシー変更後の新規データにのみ有効です。

---

### <span id="16-terms-of-service">16. Terms of service</span>

#### 要素1：技術的本質と中核能力
ログイン時にユーザーへ同意を求める社内利用規約を設定します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询服务条款 | `GET` | `/terms_of_services` | [Official Spec](https://developer.box.com/reference/get-terms-of-services) |
| 创建新服务条款 | `POST` | `/terms_of_services` | [Official Spec](https://developer.box.com/reference/post-terms-of-services) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `status` | `enum` | **是** | 状态：'enabled' 或 'disabled' |
| **Body (POST)** | `text` | `string` | **是** | 合规条款正文 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 发布服务条款]
curl -s -X POST "https://api.box.com/2.0/terms_of_services" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"status": "enabled", "tos_type": "managed", "text": "本环境仅用于测试合规迁移，严禁上传生产敏感脱密数据。"}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 削除不可：利用規約は履歴保護のため disabled へのステータス変更のみ可能です。

---

### <span id="17-terms-of-service-user-statuses">17. Terms of service user statuses</span>

#### 要素1：技術的本質と中核能力
ユーザーの規約同意状況を確認し、必要に応じて同意状態を更新します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询签署状态 | `GET` | `/terms_of_service_user_statuses` | [Official Spec](https://developer.box.com/reference) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query** | `user_id` | `string` | **是** | 目标用户 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查签署状态]
curl -s -X GET "https://api.box.com/2.0/terms_of_service_user_statuses?tos_id=tos_123&user_id=123456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 未同意時はログインが制限されます。

---

### <span id="18-integration-mappings">18. Integration mappings</span>

#### 要素1：技術的本質と中核能力
Slack や Teams などの外部サービスアカウントと Box ユーザーをマッピングします。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 获取 Slack 映射列表 | `GET` | `/integration_mappings/slack` | [Official Spec](https://developer.box.com/reference) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `id` | `string` | **是** | 映射记录 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查映射]
curl -s -X GET "https://api.box.com/2.0/integration_mappings/slack" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 双方のOAuth連携が必要です。

---

### <span id="19-enterprise-configurations">19. Enterprise Configurations</span>

#### 要素1：技術的本質と中核能力
企業全体のセキュリティ設定や外部共有制限をプログラムから構成します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 拉取企业全局配置 | `GET` | `/v2025.0/enterprise_configurations` | [Official Spec](https://developer.box.com/reference) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 版本头：'2025.0' |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查企业配置]
curl -s -X GET "https://api.box.com/2.0/enterprise_configurations" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 最高管理者権限が必要です。

---

### <span id="20-shield-lists">20. Shield lists</span>

#### 要素1：技術的本質と中核能力
IPアドレスリストや許可国リスト（ジオフェンス）を管理します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询 Shield 规则名单 | `GET` | `/v2025.0/shield_lists` | [Official Spec](https://developer.box.com/reference) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 版本头：'2025.0' |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查名单列表]
curl -s -X GET "https://api.box.com/2.0/shield_lists" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 即時反映されるため慎重に更新してください。

---

## 08-8.4 実務チェックリスト

```txt
┌──────────────────────────────────────────────────────────────┐
│             Box API 08-8 工业级集成自检清单             │
├──────────────────────────────────────────────────────────────┤
│ [ ] 1. ロック済みリテンションの不可逆性: locked 状態のポリシーは管理者でも削除・短縮できません
│ [ ] 2. リーガルホールドの優先順位: 司法凍結されたファイルはユーザーが削除しても永久保全されます
│ [ ] 3. Shield 情報障壁による遮断: バリア適用部門間ではあらゆる共有・コラボレーションが拒絶されます
│ [ ] 4. 電子透かしの強制焼き付け: Watermark はダウンロードファイルに閲覧者名と日時を直接印字します
│ [ ] 5. リージョンデータ主権: Zones により日本や欧州など特定地域にデータを物理固定します
└──────────────────────────────────────────────────────────────┘
```
