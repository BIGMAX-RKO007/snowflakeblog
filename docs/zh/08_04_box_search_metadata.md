# 第 08-4 讲：Box 核心 API 实战指南 —— Search & Metadata（全文检索与结构化元数据）

> **【开门见山 · 技术定位】**
>
> 企业内容索引与结构化属性图谱：全文倒排检索、自定义元数据模板（Metadata Templates）、属性级联继承（Cascade Policy）与数据安全密级（Classification）。

> 📖 **Box 官方权威规范与文档**：
> - [Box API Reference - Search 检索手册](https://developer.box.com/reference/resources/search/)
> - [Box API Reference - Metadata 模版与实例资源](https://developer.box.com/reference/resources/metadata-template/)
> - [Box Metadata 结构化属性与级联继承官方指南](https://developer.box.com/guides/metadata/)
> - [Box Information Security Classification 官方开发指南](https://developer.box.com/guides/classifications/)

---

## 08-4.1 全景 CRUD 能力矩阵沙盘

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
| **01** | **Search** | **全文字符串检索、元数据过滤器与高级范围搜索**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Search for files and folders</span> | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [直达](#01-search) |
| **02** | **Metadata templates** | **结构化元数据模板定义（字段名、数据类型与校验规则）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Define custom metadata schemas</span> | `manage_metadata` | ✅ | ✅ | ✅ | ✅ | [直达](#02-metadata-templates) |
| **03** | **Metadata instances (Files)** | **文件实例元数据附加、属性读写与 JSON Patch 修改**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage metadata on files</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#03-metadata-instances-files) |
| **04** | **Metadata instances (Folders)** | **目录级元数据属性挂载与读写治理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage metadata on folders</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#04-metadata-instances-folders) |
| **05** | **Metadata cascade policies** | **元数据级联继承策略（自动向下广播至所有子文件）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Auto-apply metadata to folder contents</span> | `manage_metadata` | ✅ | ✅ | ❌ | ✅ | [直达](#05-metadata-cascade-policies) |
| **06** | **Classifications** | **企业数据安全密级定义（公开、内部、绝密标签）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Define and manage security classifications</span> | `manage_metadata` | ✅ | ✅ | ✅ | ✅ | [直达](#06-classifications) |
| **07** | **Classifications on files** | **文件实体安全密级标记附加、更新与清除**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply classifications to files</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#07-classifications-on-files) |
| **08** | **Classifications on folders** | **目录实体安全密级标记与整树继承联动**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply classifications to folders</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#08-classifications-on-folders) |
| **09** | **Metadata taxonomies** | **层级化元数据分类树定义与标准化字典维护**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Organize metadata into hierarchical taxonomies</span> | `manage_metadata` | ✅ | ✅ | ✅ | ✅ | [直达](#09-metadata-taxonomies) |
| **10** | **Box query resources** | **结构化类似 SQL 的精准元数据条件过滤查询 (v2026.0)**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Query for Box items</span> | `root_readonly` | ❌ | ✅ | ❌ | ❌ | [直达](#10-box-query-resources) |
| **11** | **Box query insights** | **内容检索质量透视与查询洞察分析 (v2026.0)**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create insights for Box items</span> | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [直达](#11-box-query-insights) |

</div>

---

## 08-4.2 统一技术前置规范

在调用本分类 API 之前，所有 HTTP 客户端均需遵循以下基准通信契约：

```txt
1. Base API URL:       https://api.box.com/2.0
2. 认证凭证 Header:    Authorization: Bearer <ACCESS_TOKEN>
3. 内容交互 Header:    Content-Type: application/json (OAuth 表单或上传除外)
4. 租户企业标识:       企业管理员上下文或 As-User: <USER_ID> 代理标头
```

---

## 08-4.3 单个 API 模块五要素深度实操

### <span id="01-search">01. Search</span>

#### 要素一：技术本质与核心能力
提供企业级倒排全文检索能力。支持通过关键字匹配文件名、文件正文，并支持联合按文件大小、时间区间、所有者与元数据值多维度复合过滤。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 执行全文与多条件复合检索 | `GET` | `/search` | [Official Spec](https://developer.box.com/reference/get-search) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query** | `query` | `string` | **否** | 搜索关键词（支持短语双引号精确匹配） |
| **Query** | `scope` | `enum` | **否** | 范围：'user_content' 或 'enterprise_content' |
| **Query** | `file_extensions` | `string` | **否** | 扩展名过滤（如 'parquet,csv'） |
| **Query** | `ancestor_folder_ids` | `string` | **否** | 限定在指定目录树下搜索 |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 倒排索引延迟：新创建或刚修改的文件无法立即被 /search 端点搜出，索引构建通常有数十秒准实时延迟。即时查验请用直接 GET 或 Events API。

---

### <span id="02-metadata-templates">02. Metadata templates</span>

#### 要素一：技术本质与核心能力
设计与定义强类型的业务元数据表结构。支持定义 string, float, date, enum, multiSelect 字段类型与枚举选项。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询企业定义的所有模板清单 | `GET` | `/metadata_templates/enterprise` | [Official Spec](https://developer.box.com/reference/get-metadata-templates-enterprise) |
| 创建新的元数据模板定义 | `POST` | `/metadata_templates/schema` | [Official Spec](https://developer.box.com/reference/post-metadata-templates-schema) |
| 获取特定模板的字段详情 | `GET` | `/metadata_templates/{scope}/{template_key}/schema` | [Official Spec](https://developer.box.com/reference/get-metadata-templates-id-id-schema) |
| 通过 JSON Patch 增删改字段 | `PUT` | `/metadata_templates/{scope}/{template_key}/schema` | [Official Spec](https://developer.box.com/reference/put-metadata-templates-id-id-schema) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `scope` | `string` | **是** | 命名空间（通常为 'enterprise'） |
| **Path** | `template_key` | `string` | **是** | 模板全局唯一标识键 |
| **Body (POST)** | `displayName` | `string` | **是** | 模板人类可读展示名称 |
| **Body (POST)** | `fields` | `array` | **是** | 字段数组（包含 type, key, displayName） |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 已存在字段不可直接删除物理定义：为了保证既有文件历史元数据完整性，Box 不允许直接物理删减已有模板的字段，仅能将字段设为隐藏或添加新字段。

---

### <span id="03-metadata-instances-files">03. Metadata instances (Files)</span>

#### 要素一：技术本质与核心能力
将定义好的元数据模板实例实际绑定在特定文件上，赋予键值对属性，并支持使用 RFC 6902 标准局部增量修改字段值。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 获取文件上挂载的元数据值 | `GET` | `/files/{file_id}/metadata/{scope}/{template_key}` | [Official Spec](https://developer.box.com/reference/get-files-id-metadata-id-id) |
| 向文件赋予初始元数据实例 | `POST` | `/files/{file_id}/metadata/{scope}/{template_key}` | [Official Spec](https://developer.box.com/reference/post-files-id-metadata-id-id) |
| 通过 JSON Patch 更新元数据属性 | `PUT` | `/files/{file_id}/metadata/{scope}/{template_key}` | [Official Spec](https://developer.box.com/reference/put-files-id-metadata-id-id) |
| 从文件上彻底移除元数据实例 | `DELETE` | `/files/{file_id}/metadata/{scope}/{template_key}` | [Official Spec](https://developer.box.com/reference/delete-files-id-metadata-id-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `file_id` | `string` | **是** | 目标文件唯一 ID |
| **Header (PUT)** | `Content-Type` | `string` | **是** | 必须指定为 'application/json-patch+json' |
| **Body (PUT)** | `op` | `string` | **是** | 操作指令：'add', 'replace', 'remove', 'test' |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> Content-Type 必须指定为 application/json-patch+json：在调用 PUT 更新元数据时，若误传 application/json 会直接报 415 Unsupported Media Type 错误。

---

### <span id="04-metadata-instances-folders">04. Metadata instances (Folders)</span>

#### 要素一：技术本质与核心能力
在目录节点上附加业务属性元数据，常与级联策略（Cascade Policy）结合使用，充当整个目录树默认属性的发源地。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 获取目录元数据 | `GET` | `/folders/{id}/metadata/{scope}/{template_key}` | [Official Spec](https://developer.box.com/reference/get-folders-id-metadata-id-id) |
| 在目录上创建元数据 | `POST` | `/folders/{id}/metadata/{scope}/{template_key}` | [Official Spec](https://developer.box.com/reference/post-folders-id-metadata-id-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `folder_id` | `string` | **是** | 目标目录 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 挂载目录元数据]
curl -s -X POST "https://api.box.com/2.0/folders/987654/metadata/enterprise/lakeSyncMeta" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"sourceTable": "CORE_LEDGER"}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 重复挂载报 409：一个目录上同一模板只能有一个实例，重复 POST 会报 409 Conflict，修改应走 PUT。

---

### <span id="05-metadata-cascade-policies">05. Metadata cascade policies</span>

#### 要素一：技术本质与核心能力
自动化属性广播引擎。在指定父目录上配置级联策略后，该目录及未来落入该目录的所有子文件将自动继承并同步父级元数据。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询租户下所有级联策略 | `GET` | `/metadata_cascade_policies` | [Official Spec](https://developer.box.com/reference/get-metadata-cascade-policies) |
| 创建新的元数据级联策略 | `POST` | `/metadata_cascade_policies` | [Official Spec](https://developer.box.com/reference/post-metadata-cascade-policies) |
| 解除并删除级联策略 | `DELETE` | `/metadata_cascade_policies/{id}` | [Official Spec](https://developer.box.com/reference/delete-metadata-cascade-policies-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `folder_id` | `string` | **是** | 施加级联策略的父目录 ID |
| **Body (POST)** | `scope` | `string` | **是** | 模板所属 scope（如 'enterprise'） |
| **Body (POST)** | `templateKey` | `string` | **是** | 被级联的元数据模板 Key |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 父目录必须先拥有该元数据实例：在为一个目录创建级联策略前，该目录本身必须已经挂载了该模板的 Metadata Instance，否则报错 400。

---

### <span id="06-classifications">06. Classifications</span>

#### 要素一：技术本质与核心能力
Box Shield 安全底座。允许企业管理员定义合规密级字典（如 Public, Internal, Confidential, Restricted），并设定安全说明及颜色标识。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询企业当前启用的密级字典 | `GET` | `/metadata_templates/enterprise/securityClassification-6VMVochwUWo/schema` | [Official Spec](https://developer.box.com/reference/get-metadata-templates-enterprise-securityclassification-6vmvochwuwo-schema) |
| 初始化企业安全密级定义 | `POST` | `/metadata_templates/enterprise/securityClassification-6VMVochwUWo/schema` | [Official Spec](https://developer.box.com/reference/post-metadata-templates-enterprise-securityclassification-6vmvochwuwo-schema) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `fields` | `array` | **是** | 密级标签选项列表 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查询密级清单]
curl -s -X GET "https://api.box.com/2.0/metadata_templates/enterprise/securityClassification-6VMVochwUWo/schema" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 固定唯一模板 Key：Box 全局内置安全密级模板 Key 严格固定为 securityClassification-6VMVochwUWo，不可随意自定义模板名。

---

### <span id="07-classifications-on-files">07. Classifications on files</span>

#### 要素一：技术本质与核心能力
为单个文件打上安全标签，触发 Shield 访问屏障、防泄漏外发拦截及只读保护联动。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 获取文件当前密级 | `GET` | `/files/{id}/metadata/enterprise/securityClassification-6VMVochwUWo` | [Official Spec](https://developer.box.com/reference/get-files-id-metadata-enterprise-securityclassification-6vmvochwuwo) |
| 为文件设置密级 | `POST` | `/files/{id}/metadata/enterprise/securityClassification-6VMVochwUWo` | [Official Spec](https://developer.box.com/reference/post-files-id-metadata-enterprise-securityclassification-6vmvochwuwo) |
| 变更文件密级标签 | `PUT` | `/files/{id}/metadata/enterprise/securityClassification-6VMVochwUWo` | [Official Spec](https://developer.box.com/reference/put-files-id-metadata-enterprise-securityclassification-6vmvochwuwo) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `Box__Security__Classification__Key` | `string` | **是** | 密级名称（如 'Restricted'） |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 标记绝密]
curl -s -X POST "https://api.box.com/2.0/files/123456/metadata/enterprise/securityClassification-6VMVochwUWo" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"Box__Security__Classification__Key": "Restricted"}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 字段名双下划线格式：请求体中的键名严格为 Box__Security__Classification__Key（大小写敏感且为双下划线）。

---

### <span id="08-classifications-on-folders">08. Classifications on folders</span>

#### 要素一：技术本质与核心能力
在目录维度指定基线安全密级，实现进入该目录的资产默认继承安全防护规则。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 为目录设置安全密级 | `POST` | `/folders/{id}/metadata/enterprise/securityClassification-6VMVochwUWo` | [Official Spec](https://developer.box.com/reference/post-folders-id-metadata-enterprise-securityclassification-6vmvochwuwo) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `folder_id` | `string` | **是** | 目标目录 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 标记目录密级]
curl -s -X POST "https://api.box.com/2.0/folders/987654/metadata/enterprise/securityClassification-6VMVochwUWo" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"Box__Security__Classification__Key": "Confidential"}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 降密受控审计：从高密级（Restricted）降至低密级（Public）会被 Box Shield 记录为高风险审计事件。

---

### <span id="09-metadata-taxonomies">09. Metadata taxonomies</span>

#### 要素一：技术本质与核心能力
支持多级树状元数据分类标准（Taxonomy），用于复杂企业资产树的分类标签归档。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 获取元数据分类体系 | `GET` | `/metadata_templates/{scope}/{key}/taxonomies` | [Official Spec](https://developer.box.com/reference) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `template_key` | `string` | **是** | 关联模板 Key |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查分类树]
curl -s -X GET "https://api.box.com/2.0/metadata_templates/enterprise/lakeSyncMeta/taxonomies" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 树节点孤儿风险：在删除分类树中间节点前，必须先迁移子节点。

---

### <span id="10-box-query-resources">10. Box query resources</span>

#### 要素一：技术本质与核心能力
面向新一代企业数据湖的精准元数据查询 API。支持使用类似 SQL 的语法对海量资产进行毫秒级精准条件检索。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 提交元数据结构化查询 | `POST` | `/v2026.0/metadata_queries/execute_read` | [Official Spec](https://developer.box.com/reference/v2026.0/post-metadata-queries-execute-read) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 版本头：'2026.0' |
| **Body (POST)** | `from` | `string` | **是** | 查询目标模板（如 'enterprise_123.lakeSyncMeta'） |
| **Body (POST)** | `query` | `string` | **是** | 过滤表达式（如 'sourceTable = :tbl'） |
| **Body (POST)** | `query_params` | `object` | **是** | 参数值绑定映射 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 执行元数据 SQL 查]
curl -s -X POST "https://api.box.com/2.0/metadata_queries/execute_read" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2026.0" \
     -H "Content-Type: application/json" \
     -d '{"from": "enterprise_111222.lakeSyncMeta", "query": "sourceTable = :tbl", "query_params": {"tbl": "TRANSACTIONS"}}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 防 SQL 注入与参数化绑定：严禁直接拼接 query 字符串，必须使用 :param 占位符并通过 query_params 进行安全绑定。

---

### <span id="11-box-query-insights">11. Box query insights</span>

#### 要素一：技术本质与核心能力
分析检索性能与聚合指标，提供元数据索引利用效率评估。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询检索洞察数据 | `GET` | `/v2026.0/query_insights` | [Official Spec](https://developer.box.com/reference) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 版本头：'2026.0' |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查洞察分析]
curl -s -X GET "https://api.box.com/2.0/query_insights" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2026.0"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 前沿预览特性：v2026.0 特性需租户加入先锋试用计划。

---

## 08-4.4 总结与工业级实践自检清单

```txt
┌──────────────────────────────────────────────────────────────┐
│             Box API 08-4 工业级集成自检清单             │
├──────────────────────────────────────────────────────────────┤
│ [ ] 1. 索引准实时延迟: 新上传文件的全文检索通常有 10-60 秒的倒排索引构建窗口
│ [ ] 2. 元数据作用域: 自定义模板属于 enterprise_<id> 域，全局公共模板属于 global 域
│ [ ] 3. 元数据更新补丁格式: 更新元数据必须遵循 RFC 6902 JSON Patch 规范（op, path, value）
│ [ ] 4. 级联策略防风暴: Cascade Policy 向下递归数十万文件时在后台异步队列执行
│ [ ] 5. 密级模板固定 Key: 安全密级在底层固定挂载于 securityClassification-6VMVochwUWo 模板
└──────────────────────────────────────────────────────────────┘
```
