# 第 08-7 讲：Box 核心 API 实战指南 —— Automation & Document Workflows（流程自动化与电子签）

> **【开门见山 · 技术定位】**
>
> 无纸化业务流程与电子合规交付：Box Relay 自动化流水线触发、Box Sign 合规电子签章请求、签章模板配置与 Doc Gen 动态文档生成。

---

## 08-7.1 全景 CRUD 能力矩阵沙盘

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
| **01** | **Box Sign requests** | **发起具有法律效力的电子签章请求与状态追踪**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage e-signature requests</span> | `manage_sign_requests` | ✅ | ✅ | ❌ | ✅ | [直达](#01-box-sign-requests) |
| **02** | **Box Sign templates** | **可复用电子签署合同模板管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage reusable e-signature templates</span> | `manage_sign_requests` | ✅ | ❌ | ❌ | ❌ | [直达](#02-box-sign-templates) |
| **03** | **Workflows** | **Box Relay 业务自动化工作流启动与流水线执行**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Trigger and manage Box Relay workflows</span> | `manage_workflows` | ✅ | ✅ | ❌ | ❌ | [直达](#03-workflows) |
| **04** | **Box Doc Gen** | **动态文档生成引擎（将 JSON 数据注入 Word 模板渲染 PDF）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Generate documents programmatically from templates</span> | `manage_docgen` | ✅ | ✅ | ❌ | ❌ | [直达](#04-box-doc-gen) |
| **05** | **Box Doc Gen templates** | **动态生成模板标签元数据管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage document generation templates</span> | `manage_docgen` | ✅ | ❌ | ❌ | ❌ | [直达](#05-box-doc-gen-templates) |
| **06** | **Convert to Box note** | **外部文本/文档内容转换为 Box Note 在线便签**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Convert content to a Box Note</span> | `root_readwrite` | ❌ | ✅ | ❌ | ❌ | [直达](#06-convert-to-box-note) |
| **07** | **Automate Workflows** | **下一代 Box Automate 自动化任务动作编排 (v2026.0 Beta)**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">List and manually start Automate workflow actions</span> | `manage_workflows` | ✅ | ✅ | ❌ | ❌ | [直达](#07-automate-workflows) |

</div>

---

## 08-7.2 统一技术前置规范

在调用本分类 API 之前，所有 HTTP 客户端均需遵循以下基准通信契约：

```txt
1. Base API URL:       https://api.box.com/2.0
2. 认证凭证 Header:    Authorization: Bearer <ACCESS_TOKEN>
3. 内容交互 Header:    Content-Type: application/json (OAuth 表单或上传除外)
4. 租户企业标识:       企业管理员上下文或 As-User: <USER_ID> 代理标头
```

---

## 08-7.3 单个 API 模块五要素深度实操

### <span id="01-box-sign-requests">01. Box Sign requests</span>

#### 要素一：技术本质与核心能力
Box 原生电子签名中枢。支持指定待签署源文件、配置签署人列表（Signer, Approver）、坐标占位符与签署到期日，并生成完整防篡改审计跟踪证书。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询租户下所有签署请求 | `GET` | `/sign_requests` | [Official Spec](https://developer.box.com/reference/get-sign-requests) |
| 发起新的电子签章流程 | `POST` | `/sign_requests` | [Official Spec](https://developer.box.com/reference/post-sign-requests) |
| 获取指定签署流程的实时状态 | `GET` | `/sign_requests/{id}` | [Official Spec](https://developer.box.com/reference/get-sign-requests-id) |
| 中途撤销未完成的签署请求 | `POST` | `/sign_requests/{id}/cancel` | [Official Spec](https://developer.box.com/reference/post-sign-requests-id-cancel) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `source_files` | `array` | **是** | 待签署的文件数组：`[{"id": "123456"}]` |
| **Body (POST)** | `parent_folder` | `object` | **是** | 签署完成后归档保存签署文件的目录 ID |
| **Body (POST)** | `signers` | `array` | **是** | 签署人列表（包含 email, role: 'signer'/'approver'） |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 归档目录必须存在且有写权限：parent_folder 必须填入真实有效的文件夹 ID，且调用主体必须具备该目录的上传写权限，否则发起签署阶段即报 404/403。

---

### <span id="02-box-sign-templates">02. Box Sign templates</span>

#### 要素一：技术本质与核心能力
管理在 Box 网页端预设好签名框、日期框的合同模板，使程序可通过 template_id 一键批量派发格式合同。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询企业所有签章模板 | `GET` | `/sign_templates` | [Official Spec](https://developer.box.com/reference/get-sign-templates) |
| 获取指定模板结构详情 | `GET` | `/sign_templates/{id}` | [Official Spec](https://developer.box.com/reference/get-sign-templates-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `template_id` | `string` | **是** | 签章模板唯一 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查签章模板]
curl -s -X GET "https://api.box.com/2.0/sign_templates" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 模板占位符参数必须匹配：基于模板发起 Sign Request 时，外部提交的预填字段键名必须与模板中配置的 tag 完全吻合。

---

### <span id="03-workflows">03. Workflows</span>

#### 要素一：技术本质与核心能力
编排内容审批与自动归档流水线。支持通过 API 显式触发预定义的无代码/低代码 Relay 流程。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询目录关联的工作流列表 | `GET` | `/workflows` | [Official Spec](https://developer.box.com/reference/get-workflows) |
| 手动触发启动指定工作流 | `POST` | `/workflows/{id}/start` | [Official Spec](https://developer.box.com/reference/post-workflows-id-start) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `workflow_id` | `string` | **是** | 工作流唯一 ID |
| **Body (POST)** | `files` | `array` | **是** | 作为流转载体的文件清单 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 触发工作流]
curl -s -X POST "https://api.box.com/2.0/workflows/wf_7788/start" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"files": [{"type": "file", "id": "123456"}]}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 工作流必须处于 Active 启用状态：被禁用或草稿态的工作流调用 start 会报错 400。

---

### <span id="04-box-doc-gen">04. Box Doc Gen</span>

#### 要素一：技术本质与核心能力
基于模板的自动化单据渲染。将外部数据 Payload（如交易账单、对账确认书）动态注入 Word 模板并导出渲染为 PDF 文件。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 创建文档生成批处理任务 | `POST` | `/v2025.0/docgen_batches` | [Official Spec](https://developer.box.com/reference/v2025.0/post-docgen-batches) |
| 轮询文档渲染进度 | `GET` | `/v2025.0/docgen_jobs/{id}` | [Official Spec](https://developer.box.com/reference/v2025.0/get-docgen-jobs-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 版本头：'2025.0' |
| **Body (POST)** | `template_file_id` | `string` | **是** | 模板文件 ID |
| **Body (POST)** | `document_generation_data` | `array` | **是** | 动态数据字典数组 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 渲染动态文档]
curl -s -X POST "https://api.box.com/2.0/docgen_batches" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0" \
     -H "Content-Type: application/json" \
     -d '{"template_file_id": "123456", "document_generation_data": [{"generated_file_name": "Bill_20261103.pdf", "user_input": {"totalAmount": "$1,000,000"}}]}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 异步批处理渲染：生成大文档需轮询 docgen_jobs 状态直至 SUCCESS。

---

### <span id="05-box-doc-gen-templates">05. Box Doc Gen templates</span>

#### 要素一：技术本质与核心能力
分析和提取 Word 模板文件内部声明的动态占位符标签清单。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询模板支持的标签字典 | `GET` | `/v2025.0/docgen_template_tags/{id}` | [Official Spec](https://developer.box.com/reference/v2025.0/get-docgen-template-tags-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `template_id` | `string` | **是** | 模板文件 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 提取模板标签]
curl -s -X GET "https://api.box.com/2.0/docgen_template_tags/123456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 模板格式严格遵循 Word OOXML 规范。

---

### <span id="06-convert-to-box-note">06. Convert to Box note</span>

#### 要素一：技术本质与核心能力
将 HTML 或纯文本结构化转换为可多人实时协同的 Box Note 云笔记格式。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 提交内容转 Note 任务 | `POST` | `/v2026.0/notes/convert` | [Official Spec](https://developer.box.com/reference) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 版本头：'2026.0' |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 转 Note]
curl -s -X POST "https://api.box.com/2.0/notes/convert" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2026.0" \
     -H "Content-Type: application/json" \
     -d '{"source_file_id": "123456"}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 前沿协议需指定 v2026.0 头。

---

### <span id="07-automate-workflows">07. Automate Workflows</span>

#### 要素一：技术本质与核心能力
集成 AI 与自动化脚本的新一代事件响应编排引擎。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 执行自动化任务 | `POST` | `/v2026.0/automate_workflows/{id}/execute` | [Official Spec](https://developer.box.com/reference) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 版本头：'2026.0' |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 执行任务]
curl -s -X POST "https://api.box.com/2.0/automate_workflows/aw_123/execute" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2026.0"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> Beta 阶段功能需关注接口兼容演进。

---

## 08-7.4 总结与工业级实践自检清单

```txt
┌──────────────────────────────────────────────────────────────┐
│             Box API 08-7 工业级集成自检清单             │
├──────────────────────────────────────────────────────────────┤
│ [ ] 1. 电子签章签署者顺序: Box Sign 支持设定 is_in_person 与顺序签署序号（order）
│ [ ] 2. 签章完成回调: Sign Request 完成后将触发 SIGN_REQUEST.COMPLETED Webhook 事件
│ [ ] 3. 模板占位符对齐: Doc Gen 渲染文档时，模板中的标签语法必须与提交的 JSON 键名严格一致
│ [ ] 4. Relay 触发身份: Relay 自动化流程由系统服务或管理员身份运行，权限独立于触发者
│ [ ] 5. 签署凭证留存: 签署完成后，Box 会自动生成不可篡改的审计签名证书 PDF 文件
└──────────────────────────────────────────────────────────────┘
```
