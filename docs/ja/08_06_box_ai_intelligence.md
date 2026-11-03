# 第08-6講：Box コア API 実践ガイド —— AI & Intelligence（AI・インテリジェンス）

> **【技術ポジショニング】**
>
> 次世代コンテンツインテリジェンス：大規模言語モデル（LLM）による単一・複数ドキュメント RAG 質問応答（Box AI）、構造化抽出、AI Studio カスタムエージェントを解説します。

> 📖 **Box 公式リファレンス・仕様ドキュメント**：
> - [Box API Reference - Box AI リソース仕様](https://developer.box.com/reference/resources/ai/)
> - [Box AI 開発者公式ガイド (Box AI Overview)](https://developer.box.com/guides/box-ai/)
> - [Box AI ドキュメント RAG 質問応答仕様 (Ask Questions)](https://developer.box.com/guides/box-ai/ask-questions/)
> - [Box AI 構造化メタデータ自動抽出仕様 (Extract Metadata)](https://developer.box.com/guides/box-ai/extract-metadata/)

---

## 08-6.1 全景 CRUD 能力マトリックス

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
| **01** | **Box AI** | **ドキュメント RAG 質問応答・要約・構造化データ抽出**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">AI-powered features for asking questions and extracting data</span> | `root_readonly` | ❌ | ✅ | ❌ | ❌ | [直達](#01-box-ai) |
| **02** | **Box AI Studio** | **カスタム AI エージェントの設計・プロンプト調整・モデル選択**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Build and manage custom AI agents</span> | `manage_ai` | ✅ | ✅ | ✅ | ✅ | [直達](#02-box-ai-studio) |
| **03** | **Box Skills** | **メディア自動処理パイプライン（OCR・音声認識・顔認識）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply AI-powered skills to files</span> | `manage_skills` | ✅ | ✅ | ✅ | ✅ | [直達](#03-box-skills) |

</div>

---

## 08-6.2 共通接続仕様と前提要件

本カテゴリの API を呼び出す際は、全クライアントで以下の通信契約を遵守します：

```txt
1. Base API URL:       https://api.box.com/2.0
2. 认证凭证 Header:    Authorization: Bearer <ACCESS_TOKEN>
3. 内容交互 Header:    Content-Type: application/json (OAuth 表单或上传除外)
4. 租户企业标识:       企业管理员上下文或 As-User: <USER_ID> 代理标头
```

---

## 08-6.3 各 API モジュール 5 要素詳細解説

### <span id="01-box-ai">01. Box AI</span>

#### 要素1：技術的本質と中核能力
Box 統合型生成AIエンジンです。ファイルに対する自然言語質問（RAG）、要約生成、スキーマに基づく自動抽出を実行します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 针对一个或多个文件提出自然语言问题 | `POST` | `/ai/ask` | [Official Spec](https://developer.box.com/reference/post-ai-ask) |
| 基于已有文件内容生成新文本 | `POST` | `/ai/text_gen` | [Official Spec](https://developer.box.com/reference/post-ai-text-gen) |
| 从非结构化文件中结构化抽取字段 | `POST` | `/ai/extract` | [Official Spec](https://developer.box.com/reference/post-ai-extract) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `mode` | `enum` | **是** | 模式：'single_item_qa'（单文档）或 'multiple_item_qa'（多文档） |
| **Body (POST)** | `prompt` | `string` | **是** | 发给大模型的自然语言提问内容 |
| **Body (POST)** | `items` | `array` | **是** | 参考文档清单：`[{"type": "file", "id": "123456"}]` |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 单文档提问]
curl -s -X POST "https://api.box.com/2.0/ai/ask" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"mode": "single_item_qa", "prompt": "请总结这份技术方案的核心迁移风险", "items": [{"type": "file", "id": "123456"}]}'
```

```bash [POST 跨文档对比]
curl -s -X POST "https://api.box.com/2.0/ai/ask" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"mode": "multiple_item_qa", "prompt": "对比两份对账单的总金额差异", "items": [{"type": "file", "id": "111"}, {"type": "file", "id": "222"}]}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 参照アイテム数制限：複数ドキュメント照会時は一度に指定できるアイテム上限に注意してください。

---

### <span id="02-box-ai-studio">02. Box AI Studio</span>

#### 要素1：技術的本質と中核能力
カスタム AI エージェントの管理機能です。専用システムプロンプトの定義やモデル選択を行い、業務特化型エージェントを構築します。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 查询租户下所有已配置的 AI Agent | `GET` | `/ai_agent_configs` | [Official Spec](https://developer.box.com/reference/get-ai-agent-configs) |
| 创建新的企业级 AI Agent 配置 | `POST` | `/ai_agent_configs` | [Official Spec](https://developer.box.com/reference/post-ai-agent-configs) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `agent_type` | `string` | **是** | Agent 类型（如 'ask', 'text_gen'） |
| **Body (POST)** | `system_prompt` | `string` | **否** | 系统级先验角色定义指令 |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 创建专属 Agent]
curl -s -X POST "https://api.box.com/2.0/ai_agent_configs" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"agent_type": "ask", "system_prompt": "你是一名资深数据库迁移架构师，仅回答与数据一致性对账相关问题。"}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> 上位プラン必須：AI Studio の利用には Enterprise Plus などの上位ライセンスが必要です。

---

### <span id="03-box-skills">03. Box Skills</span>

#### 要素1：技術的本質と中核能力
メディア処理パイプライン。ファイルアップロード時に外部 ML サービスと連携し、認識結果をファイルカードへ書き込みます。

#### 要素2：エンドポイント定義辞書
| アクション | HTTP メソッド | URI パス | 公式仕様書 |
| :--- | :---: | :--- | :--- |
| 向 Box 回写技能识别结果卡片 | `POST` | `/skill_invocations/{id}` | [Official Spec](https://developer.box.com/reference/post-skill-invocations-id) |

#### 要素3：主要リクエストパラメータ・ペイロード構成
| パラメータ位置 | 項目名 (Field) | 型 (Type) | 必須 | 定義・仕様説明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `skill_invocation_id` | `string` | **是** | 技能调用实例唯一 ID |
| **Body (POST)** | `status` | `enum` | **是** | 状态：'success', 'transient_failure', 'permanent_failure' |
| **Body (POST)** | `metadata` | `object` | **是** | 卡片结构化识别数据（cards 数组） |

#### 要素4：ハンズオン実行例 (cURL)
::: code-group
```bash [POST 回写技能结果]
curl -s -X POST "https://api.box.com/2.0/skill_invocations/sk_112233" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"status": "success", "metadata": {"cards": [{"type": "skill_card", "skill_card_type": "transcript", "text": "OCR识别结果"}]}}'
```

:::

#### 要素5：アンチパターンと回避策
> [!CAUTION] **生产避险要点**
> トークン有効期限：Skill 呼び出し時に渡される一時トークンは短命です。処理完了後速やかにコールバックしてください。

---

## 08-6.4 実務チェックリスト

```txt
┌──────────────────────────────────────────────────────────────┐
│             Box API 08-6 工业级集成自检清单             │
├──────────────────────────────────────────────────────────────┤
│ [ ] 1. 対応ファイル形式: Box AI は PDF、Office文書、テキスト等にネイティブ対応
│ [ ] 2. 出典引用（Citations）: レスポンスに回答根拠となったドキュメント箇所が含まれます
│ [ ] 3. 権限境界の厳守: 呼び出しユーザーに閲覧権限のないデータはプロンプト回答に反映されません
│ [ ] 4. レート制限とクォータ: AI 呼び出しはテナント枠を消費し、上限時は 429 エラーとなります
│ [ ] 5. Skills コールバック: 処理完了後はメタデータインスタンスとして結果を書き戻します
└──────────────────────────────────────────────────────────────┘
```
