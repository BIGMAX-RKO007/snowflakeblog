# 第08-7講：Box コア API 実践ガイド —— Automation & Document Workflows（自動化・署名ワークフロー）

> **【技術ポジショニング】**
>
> ペーパーレス業務自動化と電子署名統制：Box Relay ワークフロー実行、Box Sign 法的電子署名リクエスト、署名テンプレートおよび Doc Gen 帳票自動生成エンジン。

---

## 08-7.1 全景 CRUD 能力マトリックス

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
| **01** | **Box Sign requests** | **法的効力を持つ電子署名リクエストの作成・追跡**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage e-signature requests</span> | `manage_sign_requests` | ✅ | ✅ | ❌ | ✅ | [直達](#01-box-sign-requests) |
| **02** | **Box Sign templates** | **再利用可能な電子署名テンプレートの管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage reusable e-signature templates</span> | `manage_sign_requests` | ✅ | ❌ | ❌ | ❌ | [直達](#02-box-sign-templates) |
| **03** | **Workflows** | **Box Relay ワークフローの手動起動と実行管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Trigger and manage Box Relay workflows</span> | `manage_workflows` | ✅ | ✅ | ❌ | ❌ | [直達](#03-workflows) |
| **04** | **Box Doc Gen** | **動的ドキュメント生成エンジン（WordテンプレートへのJSON流し込み）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Generate documents programmatically from templates</span> | `manage_docgen` | ✅ | ✅ | ❌ | ❌ | [直達](#04-box-doc-gen) |
| **05** | **Box Doc Gen templates** | **帳票テンプレートのタグ定義と管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage document generation templates</span> | `manage_docgen` | ✅ | ❌ | ❌ | ❌ | [直達](#05-box-doc-gen-templates) |
| **06** | **Convert to Box note** | **外部テキスト・ドキュメントの Box Note 変換**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Convert content to a Box Note</span> | `root_readwrite` | ❌ | ✅ | ❌ | ❌ | [直達](#06-convert-to-box-note) |
| **07** | **Automate Workflows** | **次世代 Automate 自動化アクションの制御 (Beta)**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">List and manually start Automate workflow actions</span> | `manage_workflows` | ✅ | ✅ | ❌ | ❌ | [直達](#07-automate-workflows) |

</div>

---

## 08-7.2 共通接続仕様と前提要件

本カテゴリの API を呼び出す際は、全クライアントで以下の通信契約を遵守します：

```txt
1. Base API URL:       https://api.box.com/2.0
2. 认证凭证 Header:    Authorization: Bearer <ACCESS_TOKEN>
3. 内容交互 Header:    Content-Type: application/json (OAuth 表单或上传除外)
4. 租户企业标识:       企业管理员上下文或 As-User: <USER_ID> 代理标头
```

---

## 08-7.3 各 API モジュール 5 要素詳細解説

### <span id="01-box-sign-requests">01. Box Sign requests</span>

#### 要素1：技術的本質と中核能力
電子署名プラットフォームです。契約書や同意書に対して複数署名者の順序指定、入力必須項目配置、法的監査ログ生成を行います。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询租户下所有签署请求 | `GET` | `/sign_requests` | [Official Spec](https://developer.box.com/reference/get-sign-requests) |
| 发起新的电子签章流程 | `POST` | `/sign_requests` | [Official Spec](https://developer.box.com/reference/post-sign-requests) |
| 获取指定签署流程的实时状态 | `GET` | `/sign_requests/{id}` | [Official Spec](https://developer.box.com/reference/get-sign-requests-id) |
| 中途撤销未完成的签署请求 | `POST` | `/sign_requests/{id}/cancel` | [Official Spec](https://developer.box.com/reference/post-sign-requests-id-cancel) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `source_files` | `array` | **是** | 待签署的文件数组：`[{"id": "123456"}]` |
| **Body (POST)** | `parent_folder` | `object` | **是** | 签署完成后归档保存签署文件的目录 ID |
| **Body (POST)** | `signers` | `array` | **是** | 签署人列表（包含 email, role: 'signer'/'approver'） |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 发起签署]
curl -s -X POST "https://api.box.com/2.0/sign_requests" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"source_files": [{"id": "123456"}], "parent_folder": {"id": "987654"}, "signers": [{"email": "client@partner.com", "role": "signer"}]}'
```

```bash [GET 查签署进度]
curl -s -X GET "https://api.box.com/2.0/sign_requests/sr_112233" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 保存先フォルダの権限要件：parent_folder は書き込み権限のある実在フォルダを指定してください。

---

### <span id="02-box-sign-templates">02. Box Sign templates</span>

#### 要素1：技術的本質と中核能力
署名枠やテキストフィールドが配置済みの定型契約テンプレートを管理・再利用します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询企业所有签章模板 | `GET` | `/sign_templates` | [Official Spec](https://developer.box.com/reference/get-sign-templates) |
| 获取指定模板结构详情 | `GET` | `/sign_templates/{id}` | [Official Spec](https://developer.box.com/reference/get-sign-templates-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `template_id` | `string` | **是** | 签章模板唯一 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 查签章模板]
curl -s -X GET "https://api.box.com/2.0/sign_templates" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> プレースホルダーの一致：テンプレートからリクエストを作成する際は定義済みタグと完全一致させる必要があります。

---

### <span id="03-workflows">03. Workflows</span>

#### 要素1：技術的本質と中核能力
コンテンツ承認や自動アーカイブの流れをオーケストレーションします。定義済み Relay フローを API からキックします。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询目录关联的工作流列表 | `GET` | `/workflows` | [Official Spec](https://developer.box.com/reference/get-workflows) |
| 手动触发启动指定工作流 | `POST` | `/workflows/{id}/start` | [Official Spec](https://developer.box.com/reference/post-workflows-id-start) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `workflow_id` | `string` | **是** | 工作流唯一 ID |
| **Body (POST)** | `files` | `array` | **是** | 作为流转载体的文件清单 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 触发工作流]
curl -s -X POST "https://api.box.com/2.0/workflows/wf_7788/start" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"files": [{"type": "file", "id": "123456"}]}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> ステータス検証：無効化されたフローや下書き状態のワークフローは起動できません。

---

### <span id="04-box-doc-gen">04. Box Doc Gen</span>

#### 要素1：技術的本質と中核能力
帳票自動出力エンジン。Word テンプレートに動的 JSON データを流し込み、PDF や DOCX を自動生成します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 创建文档生成批处理任务 | `POST` | `/v2025.0/docgen_batches` | [Official Spec](https://developer.box.com/reference/v2025.0/post-docgen-batches) |
| 轮询文档渲染进度 | `GET` | `/v2025.0/docgen_jobs/{id}` | [Official Spec](https://developer.box.com/reference/v2025.0/get-docgen-jobs-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 版本头：'2025.0' |
| **Body (POST)** | `template_file_id` | `string` | **是** | 模板文件 ID |
| **Body (POST)** | `document_generation_data` | `array` | **是** | 动态数据字典数组 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 渲染动态文档]
curl -s -X POST "https://api.box.com/2.0/docgen_batches" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0" \
     -H "Content-Type: application/json" \
     -d '{"template_file_id": "123456", "document_generation_data": [{"generated_file_name": "Bill_20261103.pdf", "user_input": {"totalAmount": "$1,000,000"}}]}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 非同期生成：大容量ファイルの生成はステータスをポーリングして完了を確認してください。

---

### <span id="05-box-doc-gen-templates">05. Box Doc Gen templates</span>

#### 要素1：技術的本質と中核能力
テンプレートファイル内に含まれるプレースホルダー定義を解析・管理します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询模板支持的标签字典 | `GET` | `/v2025.0/docgen_template_tags/{id}` | [Official Spec](https://developer.box.com/reference/v2025.0/get-docgen-template-tags-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `template_id` | `string` | **是** | 模板文件 ID |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [GET 提取模板标签]
curl -s -X GET "https://api.box.com/2.0/docgen_template_tags/123456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> DOCX 形式準拠が必要です。

---

### <span id="06-convert-to-box-note">06. Convert to Box note</span>

#### 要素1：技術的本質と中核能力
HTML やテキストコンテンツをリアルタイム共同編集可能な Box Note 形式へ変換します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 提交内容转 Note 任务 | `POST` | `/v2026.0/notes/convert` | [Official Spec](https://developer.box.com/reference) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 版本头：'2026.0' |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 转 Note]
curl -s -X POST "https://api.box.com/2.0/notes/convert" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2026.0" \
     -H "Content-Type: application/json" \
     -d '{"source_file_id": "123456"}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> v2026.0 バージョンヘッダーが必要です。

---

### <span id="07-automate-workflows">07. Automate Workflows</span>

#### 要素1：技術的本質と中核能力
AI 連携とイベントトリガーを統合した新世代自動化機能です。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 执行自动化任务 | `POST` | `/v2026.0/automate_workflows/{id}/execute` | [Official Spec](https://developer.box.com/reference) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 版本头：'2026.0' |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 执行任务]
curl -s -X POST "https://api.box.com/2.0/automate_workflows/aw_123/execute" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2026.0"
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> Beta 仕様のため変更に留意してください。

---

## 08-7.4 実務チェックリスト

```txt
┌──────────────────────────────────────────────────────────────┐
│             Box API 08-7 工业级集成自检清单             │
├──────────────────────────────────────────────────────────────┤
│ [ ] 1. 署名順序制御: Box Sign では各署名者の order（順序）と対面署名フラグを制御可能
│ [ ] 2. 署名完了通知: 完了時は SIGN_REQUEST.COMPLETED イベントが Webhook へ通知されます
│ [ ] 3. 帳票プレースホルダー: Doc Gen ではテンプレート内のタグと送信 JSON のキーを完全一致させます
│ [ ] 4. ワークフロー実行権限: Relay 自動化はシステム権限で実行され、コンテンツ操作を完遂します
│ [ ] 5. 監査証跡PDF: 署名完了後、法的効力を持つ改ざん防止監査ログPDFが自動生成されます
└──────────────────────────────────────────────────────────────┘
```
