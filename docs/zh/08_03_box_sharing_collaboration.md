# 第 08-3 讲：Box 核心 API 实战指南 —— Sharing & Collaboration（协同与共享管理）

> **【开门见山 · 技术定位】**
>
> 网状协作关系树与外链生命周期：跨企业协作者权限矩阵（8 大角色）、只读外链与密码保护、评论批注与任务流驱动。无业务噪音，纯粹以协作图模型与 HTTP 契约为主线。

---

## 08-3.1 全景 CRUD 能力矩阵沙盘

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
| **01** | **Collaborations** | **协同关系创建、角色调整（8 级权限）与协作解绑**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage file/folder collaborations</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#01-collaborations) |
| **02** | **Collaborations (List)** | **全维度协同拓扑遍历（按文件、目录、用户、组检索）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">List collaborations for users, files, folders, and groups</span> | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [直达](#02-collaborations-list) |
| **03** | **Shared links (Files)** | **文件对外公开外链创建、密码保护与到期失效**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage shared links for files</span> | `root_readwrite` | ✅ | ❌ | ✅ | ✅ | [直达](#03-shared-links-files) |
| **04** | **Shared links (Folders)** | **目录树只读外链公开与层级访问控制**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage shared links for folders</span> | `root_readwrite` | ✅ | ❌ | ✅ | ✅ | [直达](#04-shared-links-folders) |
| **05** | **Shared links (Web Links)** | **目录内外部书签节点的共享外链配置**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Access web links via shared links</span> | `root_readwrite` | ✅ | ❌ | ✅ | ✅ | [直达](#05-shared-links-web-links) |
| **06** | **Shared links (App Items)** | **第三方集成应用关联条目的共享凭证提取**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Access app items via shared links</span> | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [直达](#06-shared-links-app-items) |
| **07** | **Comments** | **文件批注系统（讨论流、@提及与富文本回复）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Add and manage comments on files</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#07-comments) |
| **08** | **Tasks** | **基于文件的审核/审批任务定义与截止时间设定**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage file-based tasks</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#08-tasks) |
| **09** | **Task assignments** | **审核任务指派、执行审批流与提交驳回/通过状态**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Assign tasks to users</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#09-task-assignments) |
| **10** | **Domain restrictions for collaborations** | **协同防泄漏域名白名单（仅允许受信任域名外部共享）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Restrict collaborations to specific domains</span> | `manage_enterprise` | ✅ | ✅ | ❌ | ✅ | [直达](#10-domain-restrictions-collab) |
| **11** | **Domain restrictions (User exemptions)** | **域名防泄漏白名单的特定用户豁免例外配置**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Exempt users from domain restrictions</span> | `manage_enterprise` | ✅ | ✅ | ❌ | ✅ | [直达](#11-domain-restrictions-exemptions) |
| **12** | **Box Hubs** | **企业主题门户与智能知识中心创建与治理 (v2025.0)**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage Box Hubs</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#12-box-hubs) |
| **13** | **Box Hub Items** | **知识门户内关联文件与结构化条目挂载**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage items within Box Hubs</span> | `root_readwrite` | ✅ | ✅ | ❌ | ✅ | [直达](#13-box-hub-items) |
| **14** | **Box Hub Collaborations** | **知识门户的协作者赋权与阅读范围控制**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage collaborations for Box Hubs</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#14-box-hub-collaborations) |

</div>

---

## 08-3.2 统一技术前置规范

在调用本分类 API 之前，所有 HTTP 客户端均需遵循以下基准通信契约：

```txt
1. Base API URL:       https://api.box.com/2.0
2. 认证凭证 Header:    Authorization: Bearer <ACCESS_TOKEN>
3. 内容交互 Header:    Content-Type: application/json (OAuth 表单或上传除外)
4. 租户企业标识:       企业管理员上下文或 As-User: <USER_ID> 代理标头
```

---

## 08-3.3 单个 API 模块五要素深度实操

### <span id="01-collaborations">01. Collaborations</span>

#### 要素一：技术本质与核心能力
Box 网状权限系统的核心支柱。用于在任意文件或目录上，向指定受管用户、组或外部邮箱赋予精确的协同角色（如 editor, viewer, previewer, uploader 等）。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 在指定资源上新增协作者 | `POST` | `/collaborations` | [Official Spec](https://developer.box.com/reference/post-collaborations) |
| 查询单条协作记录详情 | `GET` | `/collaborations/{id}` | [Official Spec](https://developer.box.com/reference/get-collaborations-id) |
| 提升/降级协作者权限角色 | `PUT` | `/collaborations/{id}` | [Official Spec](https://developer.box.com/reference/put-collaborations-id) |
| 移除协作者访问权限 | `DELETE` | `/collaborations/{id}` | [Official Spec](https://developer.box.com/reference/delete-collaborations-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `collaboration_id` | `string` | **是** | 协作映射关系 ID |
| **Body (POST)** | `item.type` | `string` | **是** | 被共享资源类型：'folder' 或 'file' |
| **Body (POST)** | `item.id` | `string` | **是** | 目标目录或文件的唯一 ID |
| **Body (POST)** | `accessible_by.type` | `string` | **是** | 被赋权主体：'user' 或 'group' |
| **Body (POST)** | `accessible_by.id` | `string` | **否** | 主体 ID（或用 login 传递外部邮箱） |
| **Body (POST/PUT)** | `role` | `enum` | **是** | 角色：'editor', 'viewer', 'previewer', 'co-owner' 等 |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 权限向下继承性（Waterfall Permissions）：在父目录赋予的协同权限会自动递归继承至所有子目录及文件，且无法在子目录单独降权或剔除。若需隔离敏感数据，必须将其移出父树或采用平级目录架构。

---

### <span id="02-collaborations-list">02. Collaborations (List)</span>

#### 要素一：技术本质与核心能力
多维透视协同关系图。允许开发者分别从文件自身、目录、特定用户或指定组为起点，逆向或正向拉取完整的权限授予清单。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询指定目录上的全部协作者 | `GET` | `/folders/{id}/collaborations` | [Official Spec](https://developer.box.com/reference/get-folders-id-collaborations) |
| 查询指定文件上的全部协作者 | `GET` | `/files/{id}/collaborations` | [Official Spec](https://developer.box.com/reference/get-files-id-collaborations) |
| 查询指定用户组获赠的所有外部协同 | `GET` | `/groups/{id}/collaborations` | [Official Spec](https://developer.box.com/reference/get-groups-id-collaborations) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `id` | `string` | **是** | 目标资源对象的 ID |
| **Query** | `limit` | `integer` | **否** | 单页返回数量（默认 100） |
| **Query** | `marker` | `string` | **否** | 游标标记 |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 仅反映直接协同：该端点返回的是直接挂载在该对象上的显式协同，通过父级继承下来的隐式协同需递归向上遍历父目录链获取。

---

### <span id="03-shared-links-files">03. Shared links (Files)</span>

#### 要素一：技术本质与核心能力
生成免登录或凭密码访问的文件公开直链。支持配置访问等级（open 公开、company 公司内、collaborators 仅协作者）及下载禁止（vanity URL）。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 通过更新 shared_link 属性创建/修改外链 | `PUT` | `/files/{file_id}` | [Official Spec](https://developer.box.com/reference/put-files-id) |
| 通过外链 URL 逆向检索对应文件对象 | `GET` | `/shared_items` | [Official Spec](https://developer.box.com/reference/get-shared-items) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `file_id` | `string` | **是** | 目标文件 ID |
| **Body (PUT)** | `shared_link.access` | `enum` | **否** | 权限：'open', 'company', 'collaborators' |
| **Body (PUT)** | `shared_link.password` | `string` | **否** | 访问密码 |
| **Body (PUT)** | `shared_link.unshared_at` | `string` | **否** | 失效时间戳（ISO 8601） |
| **Body (PUT)** | `shared_link.permissions.can_download` | `boolean` | **否** | 是否允许外链下载 |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 关闭外链传 null：销毁或关闭已有外链时，必须将 shared_link 字段明确赋值为 JSON null，不能传空对象 {}，否则外链仍处于激活状态。

---

### <span id="04-shared-links-folders">04. Shared links (Folders)</span>

#### 要素一：技术本质与核心能力
针对整棵目录树生成外部只读访问链接。外部访客可通过该外链浏览目录层级，或打包 Zip 批量下载配准资产。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 通过更新 shared_link 字段启用/更新目录外链 | `PUT` | `/folders/{folder_id}` | [Official Spec](https://developer.box.com/reference/put-folders-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `folder_id` | `string` | **是** | 目标目录 ID |
| **Body (PUT)** | `shared_link.access` | `enum` | **否** | 访问范围：'open' / 'company' |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [PUT 开启目录外链]
curl -s -X PUT "https://api.box.com/2.0/folders/987654" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"shared_link": {"access": "company"}}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 租户安全策略约束：若企业管理员在 Admin Console 开启了“禁止对外部公开共享”，试图设置 access: open 将直接抛出 403 Forbidden 错误。

---

### <span id="05-shared-links-web-links">05. Shared links (Web Links)</span>

#### 要素一：技术本质与核心能力
为挂载在目录树中的 Web Link 快捷方式生成对外公开链接。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 配置 Web Link 节点的 shared_link 属性 | `PUT` | `/web_links/{id}` | [Official Spec](https://developer.box.com/reference/put-web-links-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `web_link_id` | `string` | **是** | Web Link 唯一 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [PUT 开启链接共享]
curl -s -X PUT "https://api.box.com/2.0/web_links/778899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"shared_link": {"access": "open"}}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 纯元数据转发：访问 Web Link 外链时，客户端将收到目标 URL 引导跳转。

---

### <span id="06-shared-links-app-items">06. Shared links (App Items)</span>

#### 要素一：技术本质与核心能力
解析通过共享外链访问集成应用关联实体的安全凭据映射。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 提取外链关联的 App Item | `GET` | `/shared_items#app_items` | [Official Spec](https://developer.box.com/reference/get-shared-items) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `BoxApi` | `string` | **是** | 格式为 'shared_link=https://...' |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 逆向解析]
curl -s -X GET "https://api.box.com/2.0/shared_items" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "BoxApi: shared_link=https://app.box.com/s/xyz123"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 必须带完整 URL：BoxApi 请求头中填入的必须是完整的外链 URL 地址。

---

### <span id="07-comments">07. Comments</span>

#### 要素一：技术本质与核心能力
挂载在特定文件时间线上的评论系统。支持普通文本批注、回复嵌套（Reply）以及使用 @[user_id:name] 触发站内通知与邮件提醒。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 拉取文件上的所有评论列表 | `GET` | `/files/{file_id}/comments` | [Official Spec](https://developer.box.com/reference/get-files-id-comments) |
| 在文件上发布新评论或回复 | `POST` | `/comments` | [Official Spec](https://developer.box.com/reference/post-comments) |
| 编辑已发布的评论正文 | `PUT` | `/comments/{id}` | [Official Spec](https://developer.box.com/reference/put-comments-id) |
| 删除指定评论 | `DELETE` | `/comments/{id}` | [Official Spec](https://developer.box.com/reference/delete-comments-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `comment_id` | `string` | **是** | 评论唯一 ID |
| **Body (POST)** | `item.type` | `string` | **是** | 固定为 'file' |
| **Body (POST)** | `item.id` | `string` | **是** | 被评论的文件 ID |
| **Body (POST)** | `message` | `string` | **是** | 评论内容（支持 @提及） |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 评论仅支持挂载在文件上：目录（Folder）不支持调用 POST /comments，若向 folder 添加评论会返回 400 Bad Request。

---

### <span id="08-tasks">08. Tasks</span>

#### 要素一：技术本质与核心能力
轻量级工作流任务模型。允许在重要文件上创建审阅任务（review）或完成任务（complete），设定到期截止时间与多重审批规则。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询文件绑定的所有任务 | `GET` | `/files/{file_id}/tasks` | [Official Spec](https://developer.box.com/reference/get-files-id-tasks) |
| 在文件上创建新任务 | `POST` | `/tasks` | [Official Spec](https://developer.box.com/reference/post-tasks) |
| 更新任务说明或到期时间 | `PUT` | `/tasks/{task_id}` | [Official Spec](https://developer.box.com/reference/put-tasks-id) |
| 删除指定任务 | `DELETE` | `/tasks/{task_id}` | [Official Spec](https://developer.box.com/reference/delete-tasks-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `task_id` | `string` | **是** | 任务唯一 ID |
| **Body (POST)** | `item.id` | `string` | **是** | 文件 ID |
| **Body (POST)** | `action` | `enum` | **否** | 动作类型：'review'（审核）或 'complete'（完成） |
| **Body (POST)** | `message` | `string` | **否** | 任务说明 |
| **Body (POST)** | `due_at` | `string` | **否** | 截止到期时间（ISO 8601） |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> Task 与 Assignment 的解耦：创建 Task 本身并不代表分派给具体的人，必须紧接着调用 Task assignments 模块指派给具体处理人。

---

### <span id="09-task-assignments">09. Task assignments</span>

#### 要素一：技术本质与核心能力
管理任务的具体承办人与审批结果。处理人可提交 approval 决策状态（approved 通过，rejected 驳回）。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 将任务指派给指定用户 | `POST` | `/task_assignments` | [Official Spec](https://developer.box.com/reference/post-task-assignments) |
| 查询任务执行分配状态 | `GET` | `/task_assignments/{id}` | [Official Spec](https://developer.box.com/reference/get-task-assignments-id) |
| 更新审批结论（通过/驳回） | `PUT` | `/task_assignments/{id}` | [Official Spec](https://developer.box.com/reference/put-task-assignments-id) |
| 撤销任务指派 | `DELETE` | `/task_assignments/{id}` | [Official Spec](https://developer.box.com/reference/delete-task-assignments-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `task_assignment_id` | `string` | **是** | 分配记录 ID |
| **Body (POST)** | `task.id` | `string` | **是** | 关联的任务 ID |
| **Body (POST)** | `assign_to.id` | `string` | **是** | 被指派人用户 ID |
| **Body (PUT)** | `resolution_state` | `enum` | **否** | 结论：'approved', 'rejected', 'completed' |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 状态终态不可逆：一旦将 resolution_state 设置为 approved 或 rejected，任务将进入终态，无法再次修改结论。

---

### <span id="10-domain-restrictions-collab">10. Domain restrictions for collaborations</span>

#### 要素一：技术本质与核心能力
企业数据防泄漏（DLP）的核心防线。通过建立企业间信任域名白名单，阻断向未合规域名的邮箱外发共享。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 列出所有受信任域名白名单 | `GET` | `/collaboration_whitelist_entries` | [Official Spec](https://developer.box.com/reference/get-collaboration-whitelist-entries) |
| 添加新的协同受信任域名 | `POST` | `/collaboration_whitelist_entries` | [Official Spec](https://developer.box.com/reference/post-collaboration-whitelist-entries) |
| 移除域名白名单 | `DELETE` | `/collaboration_whitelist_entries/{id}` | [Official Spec](https://developer.box.com/reference/delete-collaboration-whitelist-entries-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `id` | `string` | **是** | 白名单记录 ID |
| **Body (POST)** | `domain` | `string` | **是** | 域名（如 'partner-corp.com'） |
| **Body (POST)** | `direction` | `enum` | **是** | 方向：'inbound'（只进）, 'outbound'（只出）, 'both'（双向） |

#### 要素四：尚硅谷三板斧实操 (cURL)
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

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 已有协作不自动回滚：添加新的域名白名单限制并不会主动切断在此之前已经建立的违规协同，需结合审计日志进行历史清理。

---

### <span id="11-domain-restrictions-exemptions">11. Domain restrictions (User exemptions)</span>

#### 要素一：技术本质与核心能力
为特定管理人员或业务接口账号开放跨越域名限制的特权豁免清单。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 列出所有豁免用户清单 | `GET` | `/collaboration_whitelist_exempt_targets` | [Official Spec](https://developer.box.com/reference/get-collaboration-whitelist-exempt-targets) |
| 增加豁免例外用户 | `POST` | `/collaboration_whitelist_exempt_targets` | [Official Spec](https://developer.box.com/reference/post-collaboration-whitelist-exempt-targets) |
| 撤销用户豁免权 | `DELETE` | `/collaboration_whitelist_exempt_targets/{id}` | [Official Spec](https://developer.box.com/reference/delete-collaboration-whitelist-exempt-targets-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `user.id` | `string` | **是** | 获得豁免权的用户 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 添加豁免]
curl -s -X POST "https://api.box.com/2.0/collaboration_whitelist_exempt_targets" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"user": {"id": "123456"}}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 审计追踪风险：被豁免的用户能够向任何外部未授信邮箱发起协作，建议结合企业 SIEM 系统重点审计。

---

### <span id="12-box-hubs">12. Box Hubs</span>

#### 要素一：技术本质与核心能力
Box 官方最新知识聚合门户。支持将散落在不同目录的文件聚合为一个统一的内容门户，并内嵌 Box AI 提供门户级问答。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询企业租户下的 Hubs 列表 | `GET` | `/v2025.0/hubs` | [Official Spec](https://developer.box.com/reference/v2025.0/get-hubs) |
| 创建新的知识门户 Hub | `POST` | `/v2025.0/hubs` | [Official Spec](https://developer.box.com/reference/v2025.0/post-hubs) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 必须指定版本头：'2025.0' |
| **Body (POST)** | `title` | `string` | **是** | Hub 门户大标题 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 创建 Hub]
curl -s -X POST "https://api.box.com/2.0/hubs" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0" \
     -H "Content-Type: application/json" \
     -d '{"title": "Engineering Knowledge Hub"}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 依赖 Hubs 企业许可：未开通 Hubs 特性的企业调用将返回 403 Feature Not Enabled。

---

### <span id="13-box-hub-items">13. Box Hub Items</span>

#### 要素一：技术本质与核心能力
管理挂载在特定 Hub 门户中的文件、目录或外部引文条目映射。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 获取 Hub 内挂载的内容条目 | `GET` | `/v2025.0/hubs/{id}/items` | [Official Spec](https://developer.box.com/reference/v2025.0/get-hubs-id-items) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `id` | `string` | **是** | Hub ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查 Hub 条目]
curl -s -X GET "https://api.box.com/2.0/hubs/hub_123/items" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 虚引用机制：从 Hub 中删除条目仅解除门户聚合关系，不会物理删除原文件。

---

### <span id="14-box-hub-collaborations">14. Box Hub Collaborations</span>

#### 要素一：技术本质与核心能力
针对整个 Hub 知识门户配置访问控制列表（Viewer, Editor）。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询 Hub 的协作者 | `GET` | `/v2025.0/hubs/{id}/collaborations` | [Official Spec](https://developer.box.com/reference/v2025.0/get-hubs-id-collaborations) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `id` | `string` | **是** | Hub 唯一 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查 Hub 协同]
curl -s -X GET "https://api.box.com/2.0/hubs/hub_123/collaborations" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 访问安全继承：用户在 Hub 中只能搜索和预览其在底层原文件本就拥有访问权的内容。

---

## 08-3.4 总结与工业级实践自检清单

```txt
┌──────────────────────────────────────────────────────────────┐
│             Box API 08-3 工业级集成自检清单             │
├──────────────────────────────────────────────────────────────┤
│ [ ] 1. 协作者角色限定: 清楚区分 Editor(可读写)、Viewer(只读)、Previewer(不可下载) 权限边界
│ [ ] 2. 外链权限生效: 为文件添加 shared_link 必须对文件本身发起 PUT 请求，而非独立端点
│ [ ] 3. 协作者去重: 重复邀请同一用户对同一目录协作将报 409 Conflict
│ [ ] 4. 域名白名单拦截: 若企业开启域名限制，向非白名单域名的外部邮箱授权将触发 403 异常
│ [ ] 5. 任务流完成状态: Task Assignment 状态包含 'incomplete', 'approved', 'rejected'
│ [ ] 6. 临时密码外链: 携带密码的外链在请求时必须通过 Header 'BoxApi: shared_link_password=...' 透传
└──────────────────────────────────────────────────────────────┘
```
