# 第 08-6 讲：Box 核心 API 实战指南 —— AI & Intelligence（大模型检索与智能代理）

> **【开门见山 · 技术定位】**
>
> 下一代内容智能底座：基于大语言模型的单/多文档 RAG 问答（Box AI）、智能结构化元数据提取与 AI Studio 自定义 Agent。无业务噪音，纯粹以提示词交互与 LLM 管道为主线。

> 📖 **Box 官方权威规范与文档**：
> - [Box API Reference - Box AI 资源手册](https://developer.box.com/reference/resources/ai/)
> - [Box AI 开发者官方开发指南 (Box AI Overview)](https://developer.box.com/guides/box-ai/)
> - [Box AI 针对文档 RAG 问答官方规范 (Ask Questions)](https://developer.box.com/guides/box-ai/ask-questions/)
> - [Box AI 结构化元数据智能提取规范 (Extract Metadata)](https://developer.box.com/guides/box-ai/extract-metadata/)

---

## 08-6.1 全景 CRUD 能力矩阵沙盘

下表为该分类下全部核心模块的能力全景矩阵。通过 HTTP 动词直观呈现各模块的技术特征与操作权限边界。

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

| 序号 | 模块 (Module) | 官方定位与中文功能说明 | 核心作用域 (Scope) | GET | POST | PUT | DEL | 快速跳转 |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **01** | **Box AI** | **单/多文档 RAG 智能问答、文本摘要与结构化信息提取**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">AI-powered features for asking questions and extracting data</span> | `root_readonly` | ❌ | ✅ | ❌ | ❌ | [直达](#01-box-ai) |
| **02** | **Box AI Studio** | **企业定制化 AI Agent 创建、系统提示词配置与模型选型**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Build and manage custom AI agents</span> | `manage_ai` | ✅ | ✅ | ✅ | ✅ | [直达](#02-box-ai-studio) |
| **03** | **Box Skills** | **文件自动化智能管道集成（音视频转写、OCR、标签生成）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply AI-powered skills to files</span> | `manage_skills` | ✅ | ✅ | ✅ | ✅ | [直达](#03-box-skills) |

</div>

---

## 08-6.2 统一技术前置规范

在调用本分类 API 之前，所有 HTTP 客户端均需遵循以下基准通信契约：

```txt
1. Base API URL:       https://api.box.com/2.0
2. 认证凭证 Header:    Authorization: Bearer <ACCESS_TOKEN>
3. 内容交互 Header:    Content-Type: application/json (OAuth 表单或上传除外)
4. 租户企业标识:       企业管理员上下文或 As-User: <USER_ID> 代理标头
```

---

## 08-6.3 单个 API 模块五要素深度实操

### <span id="01-box-ai">01. Box AI</span>

#### 要素一：技术本质与核心能力
Box 原生集成的 LLM 内容智能引擎。提供 /ai/ask 端点进行跨文档问答、/ai/text_gen 端点生成衍生内容，以及从非结构化文本中精准抽取符合 JSON Schema 的元数据。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 针对一个或多个文件提出自然语言问题 | `POST` | `/ai/ask` | [Official Spec](https://developer.box.com/reference/post-ai-ask) |
| 基于已有文件内容生成新文本 | `POST` | `/ai/text_gen` | [Official Spec](https://developer.box.com/reference/post-ai-text-gen) |
| 从非结构化文件中结构化抽取字段 | `POST` | `/ai/extract` | [Official Spec](https://developer.box.com/reference/post-ai-extract) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `mode` | `enum` | **是** | 模式：'single_item_qa'（单文档）或 'multiple_item_qa'（多文档） |
| **Body (POST)** | `prompt` | `string` | **是** | 发给大模型的自然语言提问内容 |
| **Body (POST)** | `items` | `array` | **是** | 参考文档清单：`[{"type": "file", "id": "123456"}]` |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 多文档上限限制：在 multiple_item_qa 模式下，一次请求传入的 items 数组不能超过 10,000 个字符或指定文档数量限制，否则会报错 400。

---

### <span id="02-box-ai-studio">02. Box AI Studio</span>

#### 要素一：技术本质与核心能力
Box AI Agent 治理控制台。允许企业配置专属的系统提示词（System Prompt）、选择底层基础模型（OpenAI GPT-4o, Anthropic Claude 3.5 等），并将 Agent 部署到特定目录。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询租户下所有已配置的 AI Agent | `GET` | `/ai_agent_configs` | [Official Spec](https://developer.box.com/reference/get-ai-agent-configs) |
| 创建新的企业级 AI Agent 配置 | `POST` | `/ai_agent_configs` | [Official Spec](https://developer.box.com/reference/post-ai-agent-configs) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `agent_type` | `string` | **是** | Agent 类型（如 'ask', 'text_gen'） |
| **Body (POST)** | `system_prompt` | `string` | **否** | 系统级先验角色定义指令 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 创建专属 Agent]
curl -s -X POST "https://api.box.com/2.0/ai_agent_configs" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"agent_type": "ask", "system_prompt": "你是一名资深数据库迁移架构师，仅回答与数据一致性对账相关问题。"}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 企业级 AI 订阅授权：AI Studio 需要企业启用 Box AI Enterprise Plus 高级套件，否则接口将返回 403 Forbidden。

---

### <span id="03-box-skills">03. Box Skills</span>

#### 要素一：技术本质与核心能力
事件驱动的媒体深度处理管道。当新文件上传时，自动触发第三方机器学习模型（如语音转文字、图像分类），并将识别出的结构化数据写入文件的 Skills 卡片。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 向 Box 回写技能识别结果卡片 | `POST` | `/skill_invocations/{id}` | [Official Spec](https://developer.box.com/reference/post-skill-invocations-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `skill_invocation_id` | `string` | **是** | 技能调用实例唯一 ID |
| **Body (POST)** | `status` | `enum` | **是** | 状态：'success', 'transient_failure', 'permanent_failure' |
| **Body (POST)** | `metadata` | `object` | **是** | 卡片结构化识别数据（cards 数组） |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 回写技能结果]
curl -s -X POST "https://api.box.com/2.0/skill_invocations/sk_112233" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"status": "success", "metadata": {"cards": [{"type": "skill_card", "skill_card_type": "transcript", "text": "OCR识别结果"}]}}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 超时失效机制：Skill 触发后，Box 为该次调用颁发的临时 Token 有效期较短，外部处理引擎必须在握手超时内完成结果回写。

---

## 08-6.4 总结与工业级实践自检清单

```txt
┌──────────────────────────────────────────────────────────────┐
│             Box API 08-6 工业级集成自检清单             │
├──────────────────────────────────────────────────────────────┤
│ [ ] 1. 文档切片格式支持: Box AI 问答原生支持 PDF, Word, Excel, PPT, TXT 等主流格式
│ [ ] 2. RAG 引用源提取: 响应体中返回 citations 包含段落引用源信息
│ [ ] 3. Agent 权限继承: 调用 Box AI 提问时严格遵循调用者当前文件权限边界，不可越权获悉内容
│ [ ] 4. Token 配额消耗: 企业租户具备 Box AI 调用配额上限，超标将响应 429 Too Many Requests
│ [ ] 5. Skills 流式管道: Box Skills 处理完成后需将提取的元数据实例回写至目标文件
└──────────────────────────────────────────────────────────────┘
```
