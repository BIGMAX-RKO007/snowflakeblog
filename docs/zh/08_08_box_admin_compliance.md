# 第 08-8 讲：Box 核心 API 实战指南 —— Administration & Compliance（安全治理与合规归档）

> **【开门见山 · 技术定位】**
>
> 企业级数据保全与法规遵循架构：数据保留期合规策略（Retention Policies）、司法举证数据冻结（Legal Hold）、Shield 信息安全屏障（Ethical Wall）与动态数字水印。无业务噪音，纯粹以安全防御模型与状态机为主线。

---

## 08-8.1 全景 CRUD 能力矩阵沙盘

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
| **01** | **Retention policies** | **内容保留期策略定义（法定存证、不可篡改与到期动作）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Define content retention policies</span> | `manage_retention` | ✅ | ✅ | ✅ | ✅ | [直达](#01-retention-policies) |
| **02** | **Retention policy assignments** | **保留策略与目录/企业全租户/元数据范围绑定分配**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply retention policies to content</span> | `manage_retention` | ✅ | ✅ | ❌ | ✅ | [直达](#02-retention-policy-assignments) |
| **03** | **File version retentions** | **受保全的历史版本清单审查与到期清除审计**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage retention policies for file versions</span> | `manage_retention` | ✅ | ❌ | ❌ | ❌ | [直达](#03-file-version-retentions) |
| **04** | **Legal hold policies** | **司法举证保全策略（诉讼冻结，优先级高于一切）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Define and manage legal hold policies</span> | `manage_legal_holds` | ✅ | ✅ | ✅ | ✅ | [直达](#04-legal-hold-policies) |
| **05** | **Legal hold policy assignments** | **诉讼冻结策略与涉案当事人/涉案目录精准绑定**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply legal hold policies to content</span> | `manage_legal_holds` | ✅ | ✅ | ❌ | ✅ | [直达](#05-legal-hold-policy-assignments) |
| **06** | **File version legal holds** | **司法保全覆盖下的受保护文件版本举证清单提取**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply legal holds to specific file versions</span> | `manage_legal_holds` | ✅ | ❌ | ❌ | ❌ | [直达](#06-file-version-legal-holds) |
| **07** | **Shield information barriers** | **Box Shield 信息安全隔离墙（跨部门合规阻断中枢）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Implement information barriers for compliance</span> | `manage_shield` | ✅ | ✅ | ❌ | ❌ | [直达](#07-shield-information-barriers) |
| **08** | **Shield information barrier segments** | **隔离分段划分（如投行业务分段、资产管理分段）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage barrier segments</span> | `manage_shield` | ✅ | ✅ | ✅ | ✅ | [直达](#08-shield-segments) |
| **09** | **Shield information barrier segment members** | **人员与隔离分段归属绑定管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage users in barrier segments</span> | `manage_shield` | ✅ | ✅ | ❌ | ✅ | [直达](#09-shield-segment-members) |
| **10** | **Shield information barrier segment restrictions** | **分段间阻断规则配置（严禁 A 与 B 之间协同）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Define restrictions between segments</span> | `manage_shield` | ✅ | ✅ | ❌ | ✅ | [直达](#10-shield-segment-restrictions) |
| **11** | **Shield information barrier reports** | **隔离屏障合规阻断审计报表生成**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Generate reports on information barriers</span> | `manage_shield` | ✅ | ✅ | ❌ | ❌ | [直达](#11-shield-reports) |
| **12** | **Watermarks (Files)** | **单文件动态数字水印应用、查询与移除**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply watermarks to files</span> | `root_readwrite` | ✅ | ❌ | ✅ | ✅ | [直达](#12-watermarks-files) |
| **13** | **Watermarks (Folders)** | **目录树级动态数字水印全局继承配置**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Apply watermarks to folders</span> | `root_readwrite` | ✅ | ❌ | ✅ | ✅ | [直达](#13-watermarks-folders) |
| **14** | **Standard and Zones Storage Policies** | **Box Zones 多区域数据主权与物理机房合规落位**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage storage location policies</span> | `manage_enterprise` | ✅ | ❌ | ❌ | ❌ | [直达](#14-storage-policies) |
| **15** | **Standard and Zones Storage Policy Assignments** | **存储区域策略与企业用户分配绑定**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Assign storage policies to users</span> | `manage_enterprise` | ✅ | ✅ | ✅ | ✅ | [直达](#15-storage-policy-assignments) |
| **16** | **Terms of service** | **企业合规服务条款定义（登录强制弹窗签署）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Define enterprise terms of service</span> | `manage_enterprise` | ✅ | ✅ | ✅ | ❌ | [直达](#16-terms-of-service) |
| **17** | **Terms of service user statuses** | **用户服务条款签署接受状态追踪与程序代签**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Track user acceptance of terms</span> | `manage_enterprise` | ✅ | ✅ | ✅ | ❌ | [直达](#17-terms-of-service-user-statuses) |
| **18** | **Integration mappings** | **企业第三方 SaaS（如 Slack、Teams）用户映射绑定**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Map Box users to external integrations</span> | `manage_enterprise` | ✅ | ✅ | ✅ | ✅ | [直达](#18-integration-mappings) |
| **19** | **Enterprise Configurations** | **企业全局安全与共享基准策略配置 (v2025.0)**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Configure enterprise-wide settings</span> | `manage_enterprise` | ✅ | ❌ | ✅ | ❌ | [直达](#19-enterprise-configurations) |
| **20** | **Shield lists** | **Box Shield 安全名单准入控制与地理围栏名单管理 (v2025.0)**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage access control lists</span> | `manage_shield` | ✅ | ✅ | ✅ | ✅ | [直达](#20-shield-lists) |

</div>

---

## 08-8.2 统一技术前置规范

在调用本分类 API 之前，所有 HTTP 客户端均需遵循以下基准通信契约：

```txt
1. Base API URL:       https://api.box.com/2.0
2. 认证凭证 Header:    Authorization: Bearer <ACCESS_TOKEN>
3. 内容交互 Header:    Content-Type: application/json (OAuth 表单或上传除外)
4. 租户企业标识:       企业管理员上下文或 As-User: <USER_ID> 代理标头
```

---

## 08-8.3 单个 API 模块五要素深度实操

### <span id="01-retention-policies">01. Retention policies</span>

#### 要素一：技术本质与核心能力
满足金融与法律监管（如 SEC 17a-4, FINRA）的强合规存证引擎。支持指定数据保留天数或永久保留（indefinite），并设定到期后动作（自动物理清除或解除保护）。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询租户下所有保留策略 | `GET` | `/retention_policies` | [Official Spec](https://developer.box.com/reference/get-retention-policies) |
| 创建新的合规保留策略 | `POST` | `/retention_policies` | [Official Spec](https://developer.box.com/reference/post-retention-policies) |
| 获取特定策略详情 | `GET` | `/retention_policies/{id}` | [Official Spec](https://developer.box.com/reference/get-retention-policies-id) |
| 更新策略（或永久锁定为不可逆状态） | `PUT` | `/retention_policies/{id}` | [Official Spec](https://developer.box.com/reference/put-retention-policies-id) |
| 删除未锁定的策略 | `DELETE` | `/retention_policies/{id}` | [Official Spec](https://developer.box.com/reference/delete-retention-policies-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `policy_name` | `string` | **是** | 保留策略名称 |
| **Body (POST)** | `policy_type` | `enum` | **是** | 类型：'finite'（有期限）或 'indefinite'（永久） |
| **Body (POST)** | `retention_length` | `int64` | **否** | 保留天数（当 finite 时必填） |
| **Body (POST)** | `disposition_action` | `enum` | **是** | 到期动作：'permanently_delete' 或 'remove_retention' |
| **Body (PUT)** | `status` | `string` | **否** | 设置为 'locked' 触发绝对不可逆锁定 |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> Locked 状态不可逆：一旦将 status 设置为 locked，该策略将无法通过任何 API 或人工后台取消或缩短保留期，连企业超级管理员也无法删除。

---

### <span id="02-retention-policy-assignments">02. Retention policy assignments</span>

#### 要素一：技术本质与核心能力
将定义好的保留策略实际挂载到目标范围。支持绑定单个目录（folder）、绑定全企业租户（enterprise），或与特定元数据字段值（metadata）联动触发。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询策略当前绑定的资源清单 | `GET` | `/retention_policies/{id}/assignments` | [Official Spec](https://developer.box.com/reference/get-retention-policies-id-assignments) |
| 将保留策略分配给目录或租户 | `POST` | `/retention_policy_assignments` | [Official Spec](https://developer.box.com/reference/post-retention-policy-assignments) |
| 解除保留策略绑定 | `DELETE` | `/retention_policy_assignments/{id}` | [Official Spec](https://developer.box.com/reference/delete-retention-policy-assignments-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `policy_id` | `string` | **是** | 保留策略 ID |
| **Body (POST)** | `assign_to.type` | `enum` | **是** | 范围类型：'folder', 'enterprise', 'metadata_template' |
| **Body (POST)** | `assign_to.id` | `string` | **否** | 目标目录 ID 或模板 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 绑定目录]
curl -s -X POST "https://api.box.com/2.0/retention_policy_assignments" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"policy_id": "rp_1122", "assign_to": {"type": "folder", "id": "987654"}}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 受保全文件不可删除：被分配了保留策略的目录中的文件在到期前禁止硬删除，试图调用 DELETE /trash 会报 403 Access Denied。

---

### <span id="03-file-version-retentions">03. File version retentions</span>

#### 要素一：技术本质与核心能力
只读查询受 Retention 保全机制锁定的特定历史文件版本，审计其预计销毁时间戳。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 分页查询处于保全状态的文件版本记录 | `GET` | `/file_version_retentions` | [Official Spec](https://developer.box.com/reference/get-file-version-retentions) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query** | `file_id` | `string` | **否** | 限定文件 ID |
| **Query** | `policy_id` | `string` | **否** | 限定策略 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查保全版本]
curl -s -X GET "https://api.box.com/2.0/file_version_retentions?limit=50" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 纯只读端点：该端点仅供审计使用，不可手动修改其到期时间戳。

---

### <span id="04-legal-hold-policies">04. Legal hold policies</span>

#### 要素一：技术本质与核心能力
法律诉讼与电子举证（e-Discovery）的最高保全指令。一旦对案件关联的个人或目录施加 Legal Hold，任何文件的修改与删除都将在底层永久保全所有历史快照，直至法务解除指令。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询所有司法保全策略 | `GET` | `/legal_hold_policies` | [Official Spec](https://developer.box.com/reference/get-legal-hold-policies) |
| 创建新的诉讼冻结保全策略 | `POST` | `/legal_hold_policies` | [Official Spec](https://developer.box.com/reference/post-legal-hold-policies) |
| 案件结案，解除冻结策略 | `DELETE` | `/legal_hold_policies/{id}` | [Official Spec](https://developer.box.com/reference/delete-legal-hold-policies-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `policy_name` | `string` | **是** | 诉讼案号或保全名称 |
| **Body (POST)** | `description` | `string` | **否** | 案情简述与法务备注 |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 优先级高于 Retention：即使文件在 Retention Policy 下已满到期清除年限，若同时挂载了 Legal Hold，底层的物理删除将被强制挂起阻断，保全证据优先。

---

### <span id="05-legal-hold-policy-assignments">05. Legal hold policy assignments</span>

#### 要素一：技术本质与核心能力
将司法保全策略精准锚定到涉案的具体用户账号、具体业务目录或文件上。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 施加冻结绑定 | `POST` | `/legal_hold_policy_assignments` | [Official Spec](https://developer.box.com/reference/post-legal-hold-policy-assignments) |
| 解除具体主体的冻结绑定 | `DELETE` | `/legal_hold_policy_assignments/{id}` | [Official Spec](https://developer.box.com/reference/delete-legal-hold-policy-assignments-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `policy_id` | `string` | **是** | 保全策略 ID |
| **Body (POST)** | `assign_to.type` | `enum` | **是** | 冻结对象类型：'user' 或 'folder' |
| **Body (POST)** | `assign_to.id` | `string` | **是** | 涉案用户 ID 或目录 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 冻结当事人]
curl -s -X POST "https://api.box.com/2.0/legal_hold_policy_assignments" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"policy_id": "lhp_123", "assign_to": {"type": "user", "id": "112233"}}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 静默后台执行：当对拥有巨量资产的用户打上保全时，系统在后台对百万级文件打标，此过程对前端用户完全无感知。

---

### <span id="06-file-version-legal-holds">06. File version legal holds</span>

#### 要素一：技术本质与核心能力
拉取由于 Legal Hold 而在后台强行留存的历史修改版本清单，支持法务导出证据链。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询处于冻结状态的文件版本 | `GET` | `/file_version_legal_holds` | [Official Spec](https://developer.box.com/reference/get-file-version-legal-holds) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query** | `policy_id` | `string` | **是** | 保全策略 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 提取保全证据版本]
curl -s -X GET "https://api.box.com/2.0/file_version_legal_holds?policy_id=lhp_123" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 证据版本不可物理修改：任何尝试覆盖或销毁该版本记录的 API 调用均会被直接拦截。

---

### <span id="07-shield-information-barriers">07. Shield information barriers</span>

#### 要素一：技术本质与核心能力
应对内幕交易防范与合规隔离（Ethical Wall）。在两个具有利益冲突的业务部门之间竖起一道不可逾越的数据隔离墙，硬性阻断一切文件分享与协同。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 获取企业信息屏障规则 | `GET` | `/shield_information_barriers` | [Official Spec](https://developer.box.com/reference/get-shield-information-barriers) |
| 变更信息屏障激活状态 | `POST` | `/shield_information_barriers/change_status` | [Official Spec](https://developer.box.com/reference/post-shield-information-barriers-change-status) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `id` | `string` | **是** | 屏障 ID |
| **Body (POST)** | `status` | `enum` | **是** | 状态：'pending' / 'disabled' |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查信息屏障]
curl -s -X GET "https://api.box.com/2.0/shield_information_barriers" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 全局单例模式：一个 Box Enterprise 租户只能拥有一个活跃的 Shield Information Barrier 顶层配置，在此之下划分多个分段（Segments）。

---

### <span id="08-shield-segments">08. Shield information barrier segments</span>

#### 要素一：技术本质与核心能力
信息隔离墙中的逻辑分段节点，代表需要被合规隔离的一方。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 列出所有隔离分段 | `GET` | `/shield_information_barrier_segments` | [Official Spec](https://developer.box.com/reference/get-shield-information-barrier-segments) |
| 创建新的隔离分段 | `POST` | `/shield_information_barrier_segments` | [Official Spec](https://developer.box.com/reference/post-shield-information-barrier-segments) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `name` | `string` | **是** | 分段名称（如 'Investment_Banking'） |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 建隔离分段]
curl -s -X POST "https://api.box.com/2.0/shield_information_barrier_segments" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"shield_information_barrier": {"id": "bar_123"}, "name": "IB_Department"}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 分段必须属于顶层 Barrier。

---

### <span id="09-shield-segment-members">09. Shield information barrier segment members</span>

#### 要素一：技术本质与核心能力
指定具体员工属于哪个隔离分段。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 添加用户至分段 | `POST` | `/shield_information_barrier_segment_members` | [Official Spec](https://developer.box.com/reference) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `user.id` | `string` | **是** | 用户 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 分配用户入分段]
curl -s -X POST "https://api.box.com/2.0/shield_information_barrier_segment_members" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"shield_information_barrier_segment": {"id": "seg_123"}, "user": {"id": "123456"}}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 一人不可跨多个冲突分段。

---

### <span id="10-shield-segment-restrictions">10. Shield information barrier segment restrictions</span>

#### 要素一：技术本质与核心能力
建立分段与分段之间的硬性阻断关系（Restricted）。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 添加阻断规则 | `POST` | `/shield_information_barrier_segment_restrictions` | [Official Spec](https://developer.box.com/reference) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `restricted_segment.id` | `string` | **是** | 被隔离的目标分段 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 配置隔离规则]
curl -s -X POST "https://api.box.com/2.0/shield_information_barrier_segment_restrictions" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"shield_information_barrier_segment": {"id": "seg_A"}, "restricted_segment": {"id": "seg_B"}, "type": "shield_information_barrier_segment_restriction"}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 阻断是双向的。

---

### <span id="11-shield-reports">11. Shield information barrier reports</span>

#### 要素一：技术本质与核心能力
生成屏障拦截事件与违规协同尝试的合规审计报告。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 请求生成审计报告 | `POST` | `/shield_information_barrier_reports` | [Official Spec](https://developer.box.com/reference) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `shield_information_barrier.id` | `string` | **是** | 屏障 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 生成审计报表]
curl -s -X POST "https://api.box.com/2.0/shield_information_barrier_reports" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"shield_information_barrier": {"id": "bar_123"}}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 报告异步生成并输出至指定目录。

---

### <span id="12-watermarks-files">12. Watermarks (Files)</span>

#### 要素一：技术本质与核心能力
在文件渲染与下载过程中动态压印包含访问者登录名、当前时间与 IP 的安全防截图水印。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询文件水印配置 | `GET` | `/files/{id}/watermark` | [Official Spec](https://developer.box.com/reference/get-files-id-watermark) |
| 为文件施加水印 | `PUT` | `/files/{id}/watermark` | [Official Spec](https://developer.box.com/reference/put-files-id-watermark) |
| 移除文件水印 | `DELETE` | `/files/{id}/watermark` | [Official Spec](https://developer.box.com/reference/delete-files-id-watermark) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `file_id` | `string` | **是** | 目标文件 ID |
| **Body (PUT)** | `watermark.imprint` | `string` | **是** | 固定为 'default' |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 对原始字节流的影响：开启水印后，通过普通下载端点获取的导出版 PDF 会被硬编码嵌入水印；但拥有编辑权限的原作者仍可获取原始未打标源文件。

---

### <span id="13-watermarks-folders">13. Watermarks (Folders)</span>

#### 要素一：技术本质与核心能力
将数字水印策略应用至整个目录树，使该目录内所有现有和后续新增的文件全量强制带水印。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 在目录上开启水印 | `PUT` | `/folders/{id}/watermark` | [Official Spec](https://developer.box.com/reference/put-folders-id-watermark) |
| 在目录上解除水印 | `DELETE` | `/folders/{id}/watermark` | [Official Spec](https://developer.box.com/reference/delete-folders-id-watermark) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `folder_id` | `string` | **是** | 目标目录 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [PUT 开启目录整树水印]
curl -s -X PUT "https://api.box.com/2.0/folders/987654/watermark" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"watermark": {"imprint": "default"}}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 级联传播性：目录水印一旦开启，子文件无需单独配置即可生效。

---

### <span id="14-storage-policies">14. Standard and Zones Storage Policies</span>

#### 要素一：技术本质与核心能力
满足跨国金融与数据本地化合规法规（如 GDPR）。允许将数据物理静态加密落位到指定地理区域（如东京、法兰克福、新加坡、美东）。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询企业租户可用存储区域列表 | `GET` | `/storage_policies` | [Official Spec](https://developer.box.com/reference/get-storage-policies) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query** | `limit` | `integer` | **否** | 返回数量限制 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查存储区域策略]
curl -s -X GET "https://api.box.com/2.0/storage_policies" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 需要 Box Zones 高级订阅授权：普通租户仅有默认 global 单一区域。

---

### <span id="15-storage-policy-assignments">15. Standard and Zones Storage Policy Assignments</span>

#### 要素一：技术本质与核心能力
指定特定用户创建的文件必须物理落在哪个 Zones 区域。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 为用户绑定存储区域 | `POST` | `/storage_policy_assignments` | [Official Spec](https://developer.box.com/reference/post-storage-policy-assignments) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `storage_policy_id` | `string` | **是** | 存储策略 ID |
| **Body (POST)** | `assigned_to.id` | `string` | **是** | 用户 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 分配区域]
curl -s -X POST "https://api.box.com/2.0/storage_policy_assignments" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"storage_policy_id": "sp_tokyo", "assigned_to": {"type": "user", "id": "123456"}}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 仅影响新增文件：修改用户的存储区域仅对其后续上传的新文件生效，旧文件需联系官方执行后端迁移。

---

### <span id="16-terms-of-service">16. Terms of service</span>

#### 要素一：技术本质与核心能力
强制用户在初次使用或条款更新时弹窗签署合规法律文本协议。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询服务条款 | `GET` | `/terms_of_services` | [Official Spec](https://developer.box.com/reference/get-terms-of-services) |
| 创建新服务条款 | `POST` | `/terms_of_services` | [Official Spec](https://developer.box.com/reference/post-terms-of-services) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `status` | `enum` | **是** | 状态：'enabled' 或 'disabled' |
| **Body (POST)** | `text` | `string` | **是** | 合规条款正文 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 发布服务条款]
curl -s -X POST "https://api.box.com/2.0/terms_of_services" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"status": "enabled", "tos_type": "managed", "text": "本环境仅用于测试合规迁移，严禁上传生产敏感脱密数据。"}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 条款不可删除：已发布的服务条款不支持物理 DELETE，仅可通过 PUT 设为 disabled 停用。

---

### <span id="17-terms-of-service-user-statuses">17. Terms of service user statuses</span>

#### 要素一：技术本质与核心能力
审查特定用户是否已点击同意服务条款，或通过 API 为特定服务账号自动化代签。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询签署状态 | `GET` | `/terms_of_service_user_statuses` | [Official Spec](https://developer.box.com/reference) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query** | `user_id` | `string` | **是** | 目标用户 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查签署状态]
curl -s -X GET "https://api.box.com/2.0/terms_of_service_user_statuses?tos_id=tos_123&user_id=123456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 未同意状态将阻断客户端登录。

---

### <span id="18-integration-mappings">18. Integration mappings</span>

#### 要素一：技术本质与核心能力
维护 Box 用户与第三方 SaaS 系统中账号之间的互信映射桥接表。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 获取 Slack 映射列表 | `GET` | `/integration_mappings/slack` | [Official Spec](https://developer.box.com/reference) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `id` | `string` | **是** | 映射记录 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查映射]
curl -s -X GET "https://api.box.com/2.0/integration_mappings/slack" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 必须在应用后台完成 OAuth 双向握手。

---

### <span id="19-enterprise-configurations">19. Enterprise Configurations</span>

#### 要素一：技术本质与核心能力
以代码化方式读取和配置企业 Admin Console 的核心全局安全开关。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 拉取企业全局配置 | `GET` | `/v2025.0/enterprise_configurations` | [Official Spec](https://developer.box.com/reference) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 版本头：'2025.0' |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查企业配置]
curl -s -X GET "https://api.box.com/2.0/enterprise_configurations" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 最高安全权限：仅企业 Primary Admin 可操作。

---

### <span id="20-shield-lists">20. Shield lists</span>

#### 要素一：技术本质与核心能力
定义 IP 白名单、国家地理围栏黑白名单等安全访问规则名单库。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询 Shield 规则名单 | `GET` | `/v2025.0/shield_lists` | [Official Spec](https://developer.box.com/reference) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 版本头：'2025.0' |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查名单列表]
curl -s -X GET "https://api.box.com/2.0/shield_lists" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> Shield 深度联动，配置立即影响外部登录准入。

---

## 08-8.4 总结与工业级实践自检清单

```txt
┌──────────────────────────────────────────────────────────────┐
│             Box API 08-8 工业级集成自检清单             │
├──────────────────────────────────────────────────────────────┤
│ [ ] 1. Retention 不可逆锁定: 处于 locked 状态的 Retention Policy 连企业超级管理员也无法删除或缩短保留期
│ [ ] 2. 司法冻结优先级高于删除: 被 Legal Hold 锁定的文件即便被用户删除，版本仍会被底层永久强行保全
│ [ ] 3. 信息屏障隔离阻断: Shield Barrier 生效后，受限部门之间的文件共享与协同将从协议层被硬性阻断
│ [ ] 4. 水印侵入性: 开启文件水印后，下载的预览图与 PDF 将被直接烧录当前访问者用户名与 IP 时间戳
│ [ ] 5. 多区域存储分区: Zones Storage Policy 可将特定部门的数据合规锚定在欧洲、亚洲或美洲物理机房
└──────────────────────────────────────────────────────────────┘
```
