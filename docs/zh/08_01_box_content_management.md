# 第 08-1 讲：Box 核心 API 实战指南 —— Content Management 19 大模块全景

> **【开门见山 · 技术定位】**
>
> 任何云存储与企业级内容协作系统的底层本质，都是一组通过 HTTP 协议暴露的**受控状态机与资源模型**。
>
> 在 Box 开放平台体系中，**Content Management（内容管理）** 是绝对的核心枢纽。无论上层对接的是自动化流转引擎、数据同步中间件，还是自定义客户端应用，所有关于文件创建、切片断点续传、目录遍历、版本追溯、加锁防并发冲突以及软硬删除生命周期的操作，全部归口于该类目。
>
> 本章节抛开任何业务虚词与场景假设，**纯技术视角**拆解 Content Management 下全部 **19 个官方模块**。通过「CRUD 全景沙盘矩阵」与「API 要素拓扑卡片」，帮助开发者建立全景心智模型，掌握最严谨的生产级 API 交互规范。

> 📖 **Box 官方权威规范与文档**：
> - [Box API Reference - 官方完整参考手册](https://developer.box.com/reference/)
> - [Content Management 核心开发者指南](https://developer.box.com/guides/content/)
> - [Chunked Uploads 大文件分片上传指南](https://developer.box.com/guides/uploads/chunked/)

---

## 8.1 官方 Content Management 架构图景

通过浏览器自动化实地探测 Box 官方开发者平台（`developer.box.com/reference`），Content Management 手风琴组件下严格收录了 19 个独立资源模块，涵盖从基础文件 CRUD 到千万级切片流式上传、跨节点归档冷备的完整技术闭环：

![Box Content Management 官方 19 大模块全景图](/images/08_step_01_content_management_cards_full.png)
*图 8.1：Box 开发者官方控制台 Content Management 资源面板（上区）*

![Box Content Management 官方 19 大模块下半区](/images/08_step_02_content_management_cards_lower.png)
*图 8.2：Box 开发者官方控制台 Content Management 资源面板（下区）*

---

## 8.2 Content Management 19 大模块 CRUD 矩阵沙盘

下表为 Content Management 全部 19 个模块的能力全景矩阵。通过 HTTP 动词（GET / POST / PUT / DEL）直观呈现各模块的技术特征与操作权限边界。

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
| **01** | **Files** | **文件元数据 CRUD、复制与移动**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Core file operations and management</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#_01-files) |
| **02** | **Folders** | **目录树创建、遍历、移动与管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Organizing and structuring content</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#_02-folders) |
| **03** | **File versions** | **文件历史版本追溯、提升与永久销毁**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Version history and recovery</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#_03-file-versions) |
| **04** | **File requests** | **免登录文件投递箱/收集链接配置**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Secure file collection workflows</span> | `manage_file_requests` | ✅ | ✅ | ✅ | ✅ | [直达](#_04-file-requests) |
| **05** | **Uploads** | **小文件标准直传 (< 50MB) 与预检**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Direct standard file ingestion</span> | `root_readwrite` | ❌ | ✅ | ❌ | ❌ | [直达](#_05-uploads) |
| **06** | **Uploads (Chunked)** | **大文件切片并行断点续传 (≥ 50MB)**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Large file multipart sessions</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#_06-uploads-chunked) |
| **07** | **Downloads** | **二进制文件流获取与 302 临时重定向**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Binary content streaming</span> | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [直达](#_07-downloads) |
| **08** | **Zip Downloads** | **多文件/多目录异步压缩包一键下载**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Multi-item batch packaging</span> | `root_readonly` | ✅ | ✅ | ❌ | ❌ | [直达](#_08-zip-downloads) |
| **09** | **Folder Locks** | **目录并发变更锁（防删除与防移动）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Concurrency and mutation freeze</span> | `root_readwrite` | ✅ | ✅ | ❌ | ✅ | [直达](#_09-folder-locks) |
| **10** | **Collections** | **收藏夹与跨目录虚拟资源聚合列表**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Tagging and virtual grouping</span> | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [直达](#_10-collections) |
| **11** | **Recent items** | **最近访问与交互时间线查询**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Audit and access recency stream</span> | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [直达](#_11-recent-items) |
| **12** | **Transfer folders** | **组织成员根目录资产全量所有权过户**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Content ownership migration</span> | `manage_users` | ❌ | ❌ | ✅ | ❌ | [直达](#_12-transfer-folders) |
| **13** | **Web links** | **目录内外部网址快捷方式挂载**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">External URL pointers in directory</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#_13-web-links) |
| **14** | **App item associations** | **第三方扩展应用与文件/目录双向关联**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Third-party app binding relations</span> | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [直达](#_14-app-item-associations) |
| **15** | **Trashed files** | **已移入回收站文件的查阅、恢复与硬删除**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Soft-deleted file lifecycle</span> | `root_readwrite` | ✅ | ✅ | ❌ | ✅ | [直达](#_15-trashed-files) |
| **16** | **Trashed folders** | **已移入回收站目录的查阅、恢复与硬删除**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Soft-deleted directory lifecycle</span> | `root_readwrite` | ✅ | ✅ | ❌ | ✅ | [直达](#_16-trashed-folders) |
| **17** | **Trashed items** | **全局回收站混合清单分页遍历**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Global recycle bin indexing</span> | `root_readonly` | ✅ | ❌ | ❌ | ❌ | [直达](#_17-trashed-items) |
| **18** | **Trashed web links** | **已移入回收站 Web Link 的恢复与粉碎**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Soft-deleted pointer recovery</span> | `root_readwrite` | ✅ | ✅ | ❌ | ✅ | [直达](#_18-trashed-web-links) |
| **19** | **Archives** | **冷数据自动化归档策略与归档包管理**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Long-term cold data lifecycle</span> | `root_readwrite` | ✅ | ✅ | ✅ | ✅ | [直达](#_19-archives) |

</div>

---

## 8.3 统一技术前置规范

在调用 Box 任何 API 之前，所有 HTTP 客户端均需遵循以下基准通信契约：

```txt
1. Base API URL:       https://api.box.com/2.0
2. Base Upload URL:    https://upload.box.com/api/2.0  (仅用于 Uploads 相关模块)
3. 身份凭证 Header:    Authorization: Bearer <ACCESS_TOKEN>
4. 内容交互 Header:    Content-Type: application/json (文件二进制直传除外)
5. 根目录标识:         "0" (Box 中根目录 ID 严格为字符串 "0"，非 "/" 亦非 "root")
```

---

## 8.4 单个 API 模块五要素深度实操

---

### 01. Files

#### 要素一：技术本质与核心能力
Files 模块管理 Box 存储体系中所有文件的**元数据对象**（非二进制字节流本身）。核心能力包括读取文件属性、提取缩略图渲染流、跨目录复制、元数据更新（重命名/移动父目录）以及软删除至回收站。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 获取文件元数据 | `GET` | `/files/{file_id}` | [Official Spec](https://developer.box.com/reference/get-files-id) |
| 获取文件缩略图 | `GET` | `/files/{file_id}/thumbnail.{extension}` | [Official Spec](https://developer.box.com/reference/get-files-id-thumbnail-id) |
| 跨目录复制文件 | `POST` | `/files/{file_id}/copy` | [Official Spec](https://developer.box.com/reference/post-files-id-copy) |
| 更新文件元数据 / 移动 | `PUT` | `/files/{file_id}` | [Official Spec](https://developer.box.com/reference/put-files-id) |
| 删除文件 (进回收站) | `DELETE` | `/files/{file_id}` | [Official Spec](https://developer.box.com/reference/delete-files-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `file_id` | `string` | **是** | 文件的唯一标识符（如 `"123456789"`） |
| **Header** | `If-Match` | `string` | 否 | 用于并发防冲突的 ETag 校验串（如 `"3"`） |
| **Query** | `fields` | `string[]` | 否 | 响应字段过滤器（逗号分隔，如 `name,size,sha1,path_collection`） |
| **Body (PUT)** | `name` | `string` | 否 | 新文件名（包含扩展名，如 `"renamed.parquet"`） |
| **Body (PUT)** | `parent.id` | `string` | 否 | 移动目标父目录 ID（根目录填 `"0"`） |
| **Body (PUT)** | `description` | `string` | 否 | 文件说明描述（最大长度 255 字符） |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查询元数据]
curl -s -X GET "https://api.box.com/2.0/files/123456789?fields=name,size,sha1,path_collection" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [POST 复制文件]
curl -s -X POST "https://api.box.com/2.0/files/123456789/copy" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "backup_2026.parquet",
       "parent": { "id": "987654321" }
     }'
```

```bash [PUT 重命名/移动]
curl -s -X PUT "https://api.box.com/2.0/files/123456789" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "If-Match: \"3\"" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "renamed_data.parquet",
       "parent": { "id": "0" }
     }'
```

```bash [DELETE 软删除]
curl -s -X DELETE "https://api.box.com/2.0/files/123456789" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!CAUTION] **并发修改冲突 (412 Precondition Failed)**
> 更新文件元数据（PUT）时，多线程或分布式调度程序容易发生更新覆盖。
> **解法**：在 GET 获取元数据时提取响应头中的 `ETag`，并在发起 PUT 请求时附加请求头 `If-Match: "3"`。若 ETag 已被其他进程递增，Box 会直接响应 `412 Precondition Failed`，阻止脏写。

---

### 02. Folders

#### 要素一：技术本质与核心能力
Folders 模块承载 Box 的**虚拟树状目录层级系统**。它负责物理分层结构的组织，支持递归创建子目录、遍历目录内直接子项清单（分页游标控制）、跨目录整体克隆以及目录树整体迁移。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 获取目录信息 | `GET` | `/folders/{folder_id}` | [Official Spec](https://developer.box.com/reference/get-folders-id) |
| 分页列出目录项 | `GET` | `/folders/{folder_id}/items` | [Official Spec](https://developer.box.com/reference/get-folders-id-items) |
| 创建新目录 | `POST` | `/folders` | [Official Spec](https://developer.box.com/reference/post-folders) |
| 克隆/复制整个目录 | `POST` | `/folders/{folder_id}/copy` | [Official Spec](https://developer.box.com/reference/post-folders-id-copy) |
| 更新/重命名/移动目录 | `PUT` | `/folders/{folder_id}` | [Official Spec](https://developer.box.com/reference/put-folders-id) |
| 删除目录树 | `DELETE` | `/folders/{folder_id}?recursive=true` | [Official Spec](https://developer.box.com/reference/delete-folders-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `folder_id` | `string` | **是** | 目标目录 ID（根目录严格为 `"0"`） |
| **Query** | `usemarker` | `boolean` | 否 | 是否启用游标分页（大数据量必须传 `true`） |
| **Query** | `marker` | `string` | 否 | 上一页返回的 `next_marker` 游标定位串 |
| **Query** | `limit` | `integer` | 否 | 每次拉取的条目数上限（默认 100，最大 1000） |
| **Query (DEL)** | `recursive` | `boolean` | 否 | 非空目录删除时必须指定为 `true`，否则返回 400 |
| **Body (POST)** | `name` | `string` | **是** | 新建目录名称（不得包含斜杠 `/` 或首尾空格） |
| **Body (POST)** | `parent.id` | `string` | **是** | 父目录 ID（在根目录下建文件夹填 `"0"`） |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 创建目录]
curl -s -X POST "https://api.box.com/2.0/folders" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Raw_Lake_Data",
       "parent": { "id": "0" }
     }'
```

```bash [GET 游标遍历目录]
curl -s -X GET "https://api.box.com/2.0/folders/987654321/items?limit=100&usemarker=true" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [PUT 移动目录]
curl -s -X PUT "https://api.box.com/2.0/folders/987654321" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Archive_2026",
       "parent": { "id": "0" }
     }'
```

```bash [DELETE 递归删除]
curl -s -X DELETE "https://api.box.com/2.0/folders/987654321?recursive=true" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!WARNING] **分页遍历陷阱：Offset 模式在大数据量下的深度退化**
> Box 默认的 `offset` 分页在目录项超过 10,000 时性能急剧劣化且容易丢项。
> **解法**：生产环境必须强制附加 URL 参数 `usemarker=true`，启用游标分页机制。通过响应体中的 `next_marker` 循环迭代，直至 `next_marker` 为空。

---

### 03. File versions

#### 要素一：技术本质与核心能力
Box 对同一文件路径采取**单文件多版本指针链**管理机制。当重复上传同名文件时，旧文件并不被物理覆写，而是形成版本记录链表。File versions 模块允许开发者拉取历史版本快照、将特定旧版本重新提升（Promote）为主版本，或者永久销毁特定过时版本。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 列出文件所有历史版本 | `GET` | `/files/{file_id}/versions` | [Official Spec](https://developer.box.com/reference/get-files-id-versions) |
| 获取特定版本详情 | `GET` | `/files/{file_id}/versions/{version_id}` | [Official Spec](https://developer.box.com/reference/get-files-id-versions-id) |
| 提升旧版本为主版本 | `POST` | `/files/{file_id}/versions/current` | [Official Spec](https://developer.box.com/reference/post-files-id-versions-current) |
| 还原特定版本 | `PUT` | `/files/{file_id}/versions/{version_id}` | [Official Spec](https://developer.box.com/reference/put-files-id-versions-id) |
| 物理删除特定版本 | `DELETE` | `/files/{file_id}/versions/{version_id}` | [Official Spec](https://developer.box.com/reference/delete-files-id-versions-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `file_id` | `string` | **是** | 文件唯一 ID |
| **Path** | `version_id` | `string` | **是** | 历史版本 ID（通过 GET versions 获取） |
| **Body (POST)** | `type` | `string` | **是** | 固定枚举值 `"file_version"` |
| **Body (POST)** | `id` | `string` | **是** | 需要提升为当前版本的历史版本 ID |
| **Body (PUT)** | `trashed_at` | `null` | 否 | 传 `null` 表示将已回收的版本恢复为可用状态 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 版本链查询]
curl -s -X GET "https://api.box.com/2.0/files/123456789/versions" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [POST 提升指定版本]
curl -s -X POST "https://api.box.com/2.0/files/123456789/versions/current" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "type": "file_version",
       "id": "5566778899"
     }'
```

```bash [DELETE 销毁历史版本]
curl -s -X DELETE "https://api.box.com/2.0/files/123456789/versions/5566778899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!NOTE] **Current 版本不可通过 DELETE 端点移除**
> DELETE 端点只能删除次级历史版本。若试图删除当前正在生效的 Active 版本，Box 会直接响应 `400 Bad Request`。必须先执行 `POST /versions/current` 将另一版本置顶，才能安全剔除目标版本。

---

### 04. File requests

#### 要素一：技术本质与核心能力
File requests（文件收集请求）是一种**受限反向写入通道**。它允许外部不可信实体或未登录用户向指定的 Box 目录投递上传文件，而无法查看该目录内已存在的任何其它资产，具备极高的隔离安全性。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 获取文件请求配置 | `GET` | `/file_requests/{file_request_id}` | [Official Spec](https://developer.box.com/reference/get-file-requests-id) |
| 克隆文件收集链接 | `POST` | `/file_requests/{file_request_id}/copy` | [Official Spec](https://developer.box.com/reference/post-file-requests-id-copy) |
| 更新收集标题/状态 | `PUT` | `/file_requests/{file_request_id}` | [Official Spec](https://developer.box.com/reference/put-file-requests-id) |
| 删除文件收集通道 | `DELETE` | `/file_requests/{file_request_id}` | [Official Spec](https://developer.box.com/reference/delete-file-requests-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `file_request_id` | `string` | **是** | 文件收集请求 ID |
| **Body (PUT)** | `title` | `string` | 否 | 上传页面展示的大标题（如 `"数据采集专用通道"`） |
| **Body (PUT)** | `status` | `string` | 否 | 状态枚举：`"active"`（启用）或 `"inactive"`（禁用） |
| **Body (PUT)** | `is_email_required` | `boolean` | 否 | 投递者是否必须填写其邮箱地址 |
| **Body (PUT)** | `is_description_required` | `boolean` | 否 | 投递者是否必须填写文件用途说明 |
| **Body (PUT)** | `expires_at` | `string` | 否 | 收集页面失效时间（ISO 8601 时间戳） |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 详情检查]
curl -s -X GET "https://api.box.com/2.0/file_requests/123456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [PUT 开启/更新配置]
curl -s -X PUT "https://api.box.com/2.0/file_requests/123456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Daily Data Ingestion Dropzone",
       "status": "active",
       "is_description_required": true
     }'
```

```bash [DELETE 关闭收集]
curl -s -X DELETE "https://api.box.com/2.0/file_requests/123456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!WARNING] **目标目录必须存在且处于未锁定状态**
> 文件收集通道必须绑定一个真实有效的 `folder_id`。若目标目录被删除至回收站或被 Folder Lock 锁定，外部上传动作将直接失败。

---

### 05. Uploads

#### 要素一：技术本质与核心能力
Uploads 模块为标准的**小文件单连接直接上传**协议。采用 `multipart/form-data` MIME 编码方式，专用于传输小于 50MB 的单一文件或为现有文件提交新版本。支持 OPTIONS 预检（Preflight Check）探测配额与重名冲突。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 预检上传可用性 | `OPTIONS` | `https://upload.box.com/api/2.0/files/content` | [Official Spec](https://developer.box.com/reference/options-files-content) |
| 直接上传新文件 | `POST` | `https://upload.box.com/api/2.0/files/content` | [Official Spec](https://developer.box.com/reference/post-files-content) |
| 上传已有文件新版本 | `POST` | `https://upload.box.com/api/2.0/files/{file_id}/content` | [Official Spec](https://developer.box.com/reference/post-files-id-content) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **URL** | `upload.box.com` | `host` | **是** | 必须发往 upload 专用网关，不能是 `api.box.com` |
| **Form-Data** | `attributes` | `string(JSON)` | **是** | 元数据 JSON：`{"name":"...", "parent":{"id":"0"}}` |
| **Form-Data** | `file` | `binary` | **是** | 文件二进制字节流内容 |
| **Header** | `Content-MD5` | `string` | 否 | 上传内容的 MD5 散列（Box 校验防网络乱序坏包） |
| **Path (新版)** | `file_id` | `string` | **是** | 更新版本时，指定目标文件的 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 单文件直传]
curl -s -X POST "https://upload.box.com/api/2.0/files/content" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -F attributes='{"name":"node_config.json", "parent":{"id":"0"}}' \
     -F file=@./node_config.json
```

```bash [POST 提交新版本]
curl -s -X POST "https://upload.box.com/api/2.0/files/123456789/content" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -F file=@./node_config_v2.json
```

```bash [OPTIONS 上传前预检]
curl -s -X OPTIONS "https://upload.box.com/api/2.0/files/content" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "huge_dump.csv",
       "size": 10485760,
       "parent": { "id": "0" }
     }'
```
:::

#### 要素五：实战暗坑与避坑指南
> [!IMPORTANT] **域名隔离暗坑：严禁使用 `api.box.com` 发送上传请求**
> 上传流量是纯流式吞吐，Box 将其完全路由到专门优化的网络基础设施。所有 Uploads 请求的 Base URL 必须使用 `https://upload.box.com/api/2.0`。若错误发往 `api.box.com`，服务器会直接拒绝请求。

---

### 06. Uploads (Chunked)

#### 要素一：技术本质与核心能力
针对 50MB 以上至 50TB 的海量数据，直接上传极易因 TCP 偶发丢包造成重传雪崩。Uploads (Chunked) 提供工业级的**分块并行会话机制**：通过 4 步状态机（初始化 Session -> 分块上传 Parts -> 组装 Commit -> 意外中途 Abort），支持多线程并行传输与断点续传。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 创建大文件分块会话 | `POST` | `https://upload.box.com/api/2.0/files/upload_sessions` | [Official Spec](https://developer.box.com/reference/post-files-upload-sessions) |
| 为已有文件创建分块会话 | `POST` | `https://upload.box.com/api/2.0/files/{file_id}/upload_sessions` | [Official Spec](https://developer.box.com/reference/post-files-id-upload-sessions) |
| 获取当前会话状态 | `GET` | `https://upload.box.com/api/2.0/files/upload_sessions/{session_id}` | [Official Spec](https://developer.box.com/reference/get-files-upload-sessions-id) |
| 上传指定切片数据 | `PUT` | `https://upload.box.com/api/2.0/files/upload_sessions/{session_id}` | [Official Spec](https://developer.box.com/reference/put-files-upload-sessions-id) |
| 列出已持久化切片 | `GET` | `https://upload.box.com/api/2.0/files/upload_sessions/{session_id}/parts` | [Official Spec](https://developer.box.com/reference/get-files-upload-sessions-id-parts) |
| 最终提交与拼装 | `POST` | `https://upload.box.com/api/2.0/files/upload_sessions/{session_id}/commit` | [Official Spec](https://developer.box.com/reference/post-files-upload-sessions-id-commit) |
| 终止/废弃分块会话 | `DELETE` | `https://upload.box.com/api/2.0/files/upload_sessions/{session_id}` | [Official Spec](https://developer.box.com/reference/delete-files-upload-sessions-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (Init)** | `folder_id` | `string` | **是** | 存放的目标目录 ID |
| **Body (Init)** | `file_size` | `int64` | **是** | 待上传文件的总体严格字节数 |
| **Body (Init)** | `file_name` | `string` | **是** | 上传后保存的完整文件名 |
| **Header (PUT)** | `Content-Range` | `string` | **是** | 切片区间头：`bytes {start}-{end}/{total_size}` |
| **Header (PUT)** | `Digest` | `string` | **是** | 单切片哈希头：`sha={base64_sha1}` |
| **Body (Commit)** | `parts` | `array` | **是** | 各切片结构数组：`[{"part_id","offset","size","sha1"}]` |
| **Header (Commit)**| `Digest` | `string` | **是** | 整个完整文件的总 SHA-1 校验散列串 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 1. 创建会话]
curl -s -X POST "https://upload.box.com/api/2.0/files/upload_sessions" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "folder_id": "0",
       "file_size": 104857600,
       "file_name": "data_dump_100MB.tar.gz"
     }'
```

```bash [PUT 2. 上传特定分块]
curl -s -X PUT "https://upload.box.com/api/2.0/files/upload_sessions/D3A1B2C3D4/part" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Range: bytes 0-8388607/104857600" \
     -H "Digest: sha=FPuS8b...base64sha1==" \
     -H "Content-Type: application/octet-stream" \
     --data-binary @part_0.bin
```

```bash [POST 3. 提交组装]
curl -s -X POST "https://upload.box.com/api/2.0/files/upload_sessions/D3A1B2C3D4/commit" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Digest: sha=OverallSha1Base64==" \
     -H "Content-Type: application/json" \
     -d '{
       "parts": [
         { "part_id": "01", "offset": 0, "size": 8388608, "sha1": "FPuS8b..." }
       ]
     }'
```

```bash [DELETE 4. 中途废弃]
curl -s -X DELETE "https://upload.box.com/api/2.0/files/upload_sessions/D3A1B2C3D4" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!CAUTION] **核心暗坑：Part 大小严格一致性校验与 Digest 计算**
> 1. Box 握手返回的 Session 明确指定了 `part_size`（通常为 8MB 的整数倍）。除了最后一个分块大小可小于 `part_size` 外，其余所有前置分块的字节数必须**严格等于**协商的 `part_size`，否则直接返回 `400 Bad Request`。
> 2. 每个分块必须带 `Digest: sha=<Base64编码的SHA1>`，Commit 时还需提交全量文件的 SHA1 校验码。

---

### 07. Downloads

#### 要素一：技术本质与核心能力
Downloads 模块负责从存储集群中提取文件的**真实二进制字节流**。Box API 在该端点默认不直接吐出大文件内容，而是通过标准 HTTP 协议的 `302 Found` 重定向机制，将客户端引导至最近边缘 CDN 节点的临时安全 URL。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 下载文件完整字节流 | `GET` | `/files/{file_id}/content` | [Official Spec](https://developer.box.com/reference/get-files-id-content) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `file_id` | `string` | **是** | 待下载文件的唯一 ID |
| **Header** | `Range` | `string` | 否 | 支持断点分段下载（格式如 `bytes=0-1048575`） |
| **Query** | `version` | `string` | 否 | 下载历史指定版本的 ID（缺省下载最新当前版） |
| **Response** | `Location` | `header` | **是** | HTTP 302 重定向的目标预签名下载 URL |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 自动跟随重定向下载]
curl -L -X GET "https://api.box.com/2.0/files/123456789/content" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -o "./downloaded_file.parquet"
```

```bash [GET 仅获取 302 预签名下载链接]
curl -s -i -X GET "https://api.box.com/2.0/files/123456789/content" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" | grep -i "location:"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!WARNING] **重定向安全泄漏：跟随重定向时严禁泄漏 Bearer Token**
> 在使用通用 HTTP 客户端库（如 Python requests、Go http.Client 或 cURL）时，请务必注意：重定向的目标地址为预签名的临时 CDN 存储桶 URL。**切勿**将 Box 的 `Authorization: Bearer` 请求头透传给 CDN 域名，现代客户端默认会在跨域时自动剥离 Authorization 头以确保凭证安全。

---

### 08. Zip Downloads

#### 要素一：技术本质与核心能力
针对一次性批量下载多个文件或深层嵌套目录树的场景，若逐个调用 GET 会导致严重的连接开销与限流风险。Zip Downloads 提供**服务端无感异步打包压缩能力**：发起打包请求，轮询就绪状态，流式提取归档 Zip 包。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 创建打包下载会话 | `POST` | `/zip_downloads` | [Official Spec](https://developer.box.com/reference/post-zip-downloads) |
| 轮询打包状态进度 | `GET` | `/zip_downloads/{id}/status` | [Official Spec](https://developer.box.com/reference/get-zip-downloads-id-status) |
| 流式下载打包文件 | `GET` | `https://dl.boxcloud.com/2.0/zip_downloads/{id}/content` | [Official Spec](https://developer.box.com/reference/get-zip-downloads-id-content) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `download_file_name` | `string` | **是** | 压缩包保存名称（必须以 `.zip` 结尾） |
| **Body (POST)** | `items` | `object[]` | **是** | 待压缩清单：`[{"type":"file|folder", "id":"..."}]` |
| **Path (Poll)** | `id` | `string` | **是** | Zip 下载会话 ID |
| **Status 返回**| `state` | `string` | - | 状态枚举：`"in_progress"`、`"succeeded"`、`"failed"` |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 1. 创建打包任务]
curl -s -X POST "https://api.box.com/2.0/zip_downloads" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "download_file_name": "batch_export_2026.zip",
       "items": [
         { "type": "file", "id": "123456" },
         { "type": "folder", "id": "987654" }
       ]
     }'
```

```bash [GET 2. 轮询状态]
curl -s -X GET "https://api.box.com/2.0/zip_downloads/z1a2b3/status" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [GET 3. 提取 Zip 包]
curl -L -X GET "https://dl.boxcloud.com/2.0/zip_downloads/z1a2b3/content" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -o "./batch_export_2026.zip"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!CAUTION] **单包上限阈值：10,000 个文件或 32GB**
> Zip Downloads 具有硬性边界限制：单个压缩包内包含的文件总数不得超过 10,000 个，未压缩前总字节数不得超过 32GB。若超标，接口在创建阶段将直接失败并抛出超出阈值异常。

---

### 09. Folder Locks

#### 要素一：技术本质与核心能力
在数据同步或自动化处理中，为防止人工或下游进程意外删除或移动正在处理的目录结构，Folder Locks 提供了**悲观保护锁语义**。锁定的目录将被禁止删除（prevent_deletion）或禁止移动（prevent_move）。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询目录锁清单 | `GET` | `/folder_locks?folder_id={folder_id}` | [Official Spec](https://developer.box.com/reference/get-folder-locks) |
| 对指定目录施加锁 | `POST` | `/folder_locks` | [Official Spec](https://developer.box.com/reference/post-folder-locks) |
| 解除并删除目录锁 | `DELETE` | `/folder_locks/{folder_lock_id}` | [Official Spec](https://developer.box.com/reference/delete-folder-locks-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query (GET)** | `folder_id` | `string` | **是** | 待检查锁的目录 ID |
| **Body (POST)** | `folder.type` | `string` | **是** | 固定枚举值 `"folder"` |
| **Body (POST)** | `folder.id` | `string` | **是** | 锁定目标目录 ID |
| **Body (POST)** | `locked_operations.move` | `boolean` | 否 | 是否禁止移动该目录（默认 `true`） |
| **Body (POST)** | `locked_operations.delete`| `boolean` | 否 | 是否禁止删除该目录（默认 `true`） |
| **Path (DEL)** | `folder_lock_id` | `string` | **是** | 待释放的锁记录 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 加锁]
curl -s -X POST "https://api.box.com/2.0/folder_locks" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "folder": {
         "type": "folder",
         "id": "987654321"
       },
       "locked_operations": {
         "move": true,
         "delete": true
       }
     }'
```

```bash [GET 查询锁状态]
curl -s -X GET "https://api.box.com/2.0/folder_locks?folder_id=987654321" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [DELETE 释放锁]
curl -s -X DELETE "https://api.box.com/2.0/folder_locks/889900" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!IMPORTANT] **解铃还须系铃人：锁所有权与权限要求**
> Folder Lock 具有严格的权限绑定。若当前 API 调用主体非该锁的创建者或不具备企业管理员超级权限，直接调用 DELETE 释放锁将触发 `403 Access Denied`。

---

### 10. Collections

#### 要素一：技术本质与核心能力
Collections 模块是 Box 中的**虚拟分类标签机制**（如系统预设的 "Favorites" 收藏夹）。它不改变文件与目录在磁盘上的树状物理位置，仅通过虚拟关系表建立索引聚合。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 列出当前用户所有集合 | `GET` | `/collections` | [Official Spec](https://developer.box.com/reference/get-collections) |
| 获取指定集合详情 | `GET` | `/collections/{collection_id}` | [Official Spec](https://developer.box.com/reference/get-collections-id) |
| 分页检索集合内条目 | `GET` | `/collections/{collection_id}/items` | [Official Spec](https://developer.box.com/reference/get-collections-id-items) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `collection_id` | `string` | **是** | 集合唯一 ID（通过 GET `/collections` 发现） |
| **Query** | `limit` | `integer` | 否 | 分页条目上限（默认 100） |
| **Query** | `offset` | `integer` | 否 | 分页起始偏移量 |
| **Query** | `fields` | `string[]` | 否 | 指定条目返回的属性字段列表 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 列出所有集合]
curl -s -X GET "https://api.box.com/2.0/collections" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [GET 遍历集合内条目]
curl -s -X GET "https://api.box.com/2.0/collections/12345/items?limit=50" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!NOTE] **只读端点性质：集合的新增条目归口于目标对象的 PUT 请求**
> Collections 自身只有 GET 端点！如果想将某个文件放入收藏夹，并不是向 `/collections` 发起 POST，而是向该文件发起 `PUT /files/{file_id}`，并在请求体中修改 `collections: [{"id": "12345"}]`。

---

### 11. Recent items

#### 要素一：技术本质与核心能力
Recent items 模块提供当前调用身份在 Box 平台上**按时间倒序排列的最近交互资源流**（包括打开、预览、修改等动作）。适用于增量同步轮询检测与活动快照提取。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 获取最近访问清单 | `GET` | `/recent_items` | [Official Spec](https://developer.box.com/reference/get-recent-items) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query** | `limit` | `integer` | 否 | 返回条目数量限制（最大 1000） |
| **Query** | `marker` | `string` | 否 | 游标分页标记 |
| **Query** | `fields` | `string[]` | 否 | 额外返回的资源字段 |
| **条目属性** | `interaction_type` | `enum` | - | 动作类型：`item_preview` / `item_modify` / `item_open` |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 轮询最近变动]
curl -s -X GET "https://api.box.com/2.0/recent_items?limit=20" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!WARNING] **事件准实时延迟与不可作为硬性审计基准**
> Recent items 的索引建立存在数秒至数分钟的准实时缓存窗口。如果系统对事件的严密性与零丢失有硬性要求，应使用 Enterprise Events 流，而非依赖 Recent items。

---

### 12. Transfer folders

#### 要素一：技术本质与核心能力
当企业员工离职或系统服务账号注销迁移时，Transfer folders 模块负责将指定用户根目录（ID 为 "0"）下的所有资产及其子树的所有权，**原子化完整过户**给另一位目标指定用户。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 过户用户根目录所有权 | `PUT` | `/users/{user_id}/folders/0` | [Official Spec](https://developer.box.com/reference/put-users-id-folders-0) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `user_id` | `string` | **是** | 待交出资产的原始用户 ID |
| **Path** | `folder_id` | `string` | **是** | 必须严格为根目录 `"0"` |
| **Query** | `notify` | `boolean` | 否 | 是否向交接双方发送邮件提醒（默认 `false`） |
| **Body (PUT)** | `owned_by.id` | `string` | **是** | 接收资产的目标用户 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [PUT 资产所有权整树过户]
curl -s -X PUT "https://api.box.com/2.0/users/11223344/folders/0" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "owned_by": {
         "id": "99887766"
       }
     }'
```
:::

#### 要素五：实战暗坑与避坑指南
> [!CAUTION] **高危单向动作：必须具备企业管理级权限**
> 1. 此操作为**不可逆**资产移交，调用方必须具备企业管理员或 `manage_users` 核心权限。
> 2. 目标接收用户的存储配额必须足以容纳被过户用户的总数据量，否则请求将在排队执行时失败。

---

### 13. Web links

#### 要素一：技术本质与核心能力
Web links 模块允许在常规的 Box 目录树中创建**指向外部网络资源的超链接对象**。在外部看它如同一个文件节点，但其 Payload 存储的是目标 URL 及描述说明。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 获取外部链接信息 | `GET` | `/web_links/{web_link_id}` | [Official Spec](https://developer.box.com/reference/get-web-links-id) |
| 创建外部链接节点 | `POST` | `/web_links` | [Official Spec](https://developer.box.com/reference/post-web-links) |
| 更新链接地址或名称 | `PUT` | `/web_links/{web_link_id}` | [Official Spec](https://developer.box.com/reference/put-web-links-id) |
| 删除外部链接 | `DELETE` | `/web_links/{web_link_id}` | [Official Spec](https://developer.box.com/reference/delete-web-links-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `web_link_id` | `string` | **是** | 网页链接条目 ID |
| **Body (POST)** | `url` | `string(URL)`| **是** | 目标外部网址（必须带 `https://` 协议前缀） |
| **Body (POST)** | `parent.id` | `string` | **是** | 存放该快捷方式的目录 ID（根目录填 `"0"`） |
| **Body (POST)** | `name` | `string` | 否 | 链接展示标题 |
| **Body (POST)** | `description` | `string` | 否 | 链接用途简述 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 创建链接]
curl -s -X POST "https://api.box.com/2.0/web_links" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://docs.snowflake.com",
       "parent": { "id": "0" },
       "name": "Snowflake Documentation Link",
       "description": "Production Documentation Pointer"
     }'
```

```bash [GET 获取链接]
curl -s -X GET "https://api.box.com/2.0/web_links/778899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [PUT 修改链接]
curl -s -X PUT "https://api.box.com/2.0/web_links/778899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Updated Docs Link"
     }'
```

```bash [DELETE 删除链接]
curl -s -X DELETE "https://api.box.com/2.0/web_links/778899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!NOTE] **协议头完整性校验**
> 提交的 URL 字段必须带标准网络协议方案头（如 `https://` 或 `http://`），否则接口会拒绝创建并返回 `400 Invalid URL format`。

---

### 14. App item associations

#### 要素一：技术本质与核心能力
管理 Box 文件或目录与外部第三方 SaaS/应用系统（例如 Slack 讨论线程、DocuSign 电子签章任务等）之间的**双向元数据关联关系映射**。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询文件关联的外部应用 | `GET` | `/files/{file_id}/app_item_associations` | [Official Spec](https://developer.box.com/reference/get-files-id-app-item-associations) |
| 查询目录关联的外部应用 | `GET` | `/folders/{folder_id}/app_item_associations` | [Official Spec](https://developer.box.com/reference/get-folders-id-app-item-associations) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `file_id` / `folder_id` | `string` | **是** | 目标资源对象的唯一标识符 |
| **Query** | `limit` | `integer` | 否 | 分页条目数量（默认 100） |
| **Query** | `marker` | `string` | 否 | 游标标识 |
| **返回字段** | `app_item.application_type`| `string` | - | 关联的应用系统标识（如 `"slack"`, `"jira"`） |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查询文件级应用关联]
curl -s -X GET "https://api.box.com/2.0/files/123456789/app_item_associations" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [GET 查询目录级应用关联]
curl -s -X GET "https://api.box.com/2.0/folders/987654321/app_item_associations" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!WARNING] **应用集成授权前置依赖**
> 若未在 Box Admin Console 中开通并授权对应的外部集成应用（App Item），调用该端点将始终返回空条目数组 `[]`。

---

### 15. Trashed files

#### 要素一：技术本质与核心能力
管理因调用普通 `DELETE /files/{id}` 而进入回收站的文件。该模块提供**二次生命周期管理**：查看软删除文件的垃圾箱快照、撤销删除恢复至原位置，或者执行永久硬删除（不可逆粉碎）。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查看回收站中的单个文件 | `GET` | `/files/{file_id}/trash` | [Official Spec](https://developer.box.com/reference/get-files-id-trash) |
| 从回收站恢复文件 | `POST` | `/files/{file_id}` | [Official Spec](https://developer.box.com/reference/post-files-id) |
| 永久硬删除文件 (粉碎) | `DELETE` | `/files/{file_id}/trash` | [Official Spec](https://developer.box.com/reference/delete-files-id-trash) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `file_id` | `string` | **是** | 处于回收站中的文件 ID |
| **Body (POST)** | `name` | `string` | 否 | 恢复时重命名的文件名（用于解决同名冲突） |
| **Body (POST)** | `parent.id` | `string` | 否 | 恢复到的目标父目录 ID（若原父目录已毁） |
| **Query (GET)** | `fields` | `string[]` | 否 | 包含属性（如 `trashed_at`, `purged_at`） |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查看垃圾箱详情]
curl -s -X GET "https://api.box.com/2.0/files/123456789/trash" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [POST 撤销删除还原]
curl -s -X POST "https://api.box.com/2.0/files/123456789" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{}'
```

```bash [DELETE 永久销毁]
curl -s -X DELETE "https://api.box.com/2.0/files/123456789/trash" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!CAUTION] **恢复冲突 (409 Conflict) 与原父目录丢失**
> 1. 若文件被删除期间，原父目录中又创建了同名文件，恢复请求将返回 `409 Item with the same name already exists`。必须在 POST 请求体中指定新的 `parent` ID 或新的 `name`。
> 2. 若原父目录已被移入垃圾箱，文件将无法直接还原，需显式指定还原的目标父目录。

---

### 16. Trashed folders

#### 要素一：技术本质与核心能力
管理已被软删除入垃圾箱的整个目录树结构。支持查询垃圾箱目录元数据、将整棵子树一键撤销恢复，或彻底物理抹除整棵目录树。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查看回收站中的单个目录 | `GET` | `/folders/{folder_id}/trash` | [Official Spec](https://developer.box.com/reference/get-folders-id-trash) |
| 从回收站还原目录树 | `POST` | `/folders/{folder_id}` | [Official Spec](https://developer.box.com/reference/post-folders-id) |
| 永久硬删除目录树 | `DELETE` | `/folders/{folder_id}/trash` | [Official Spec](https://developer.box.com/reference/delete-folders-id-trash) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `folder_id` | `string` | **是** | 处于回收站中的目录 ID |
| **Body (POST)** | `name` | `string` | 否 | 恢复时指定新目录名 |
| **Body (POST)** | `parent.id` | `string` | 否 | 恢复时指定新父目录 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查看垃圾箱目录]
curl -s -X GET "https://api.box.com/2.0/folders/987654321/trash" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [POST 撤销删除还原整个目录]
curl -s -X POST "https://api.box.com/2.0/folders/987654321" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{}'
```

```bash [DELETE 永久销毁整棵目录树]
curl -s -X DELETE "https://api.box.com/2.0/folders/987654321/trash" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!WARNING] **异步清理延迟**
> 永久硬删除深层大目录时，Box 后台执行异步递归垃圾回收。在接口响应 `204 No Content` 后的数秒内，若立即创建同名目录可能短暂遭遇命名冲突。

---

### 17. Trashed items

#### 要素一：技术本质与核心能力
全局回收站条目的**聚合分页检索通道**。不同于前述单对象查询，Trashed items 跨文件、目录及超链接维度，统一按列表形式分页吐出当前租户回收站内的所有残余资产。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 全局分页拉取回收站清单 | `GET` | `/folders/trash/items` | [Official Spec](https://developer.box.com/reference/get-folders-trash-items) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query** | `limit` | `integer` | 否 | 每次拉取条目数上限（默认 100，最大 1000） |
| **Query** | `offset` | `integer` | 否 | 分页偏移量 |
| **Query** | `sort` | `string` | 否 | 排序字段（`name`, `date`, `size`） |
| **Query** | `direction` | `string` | 否 | 排序顺序（`ASC` 或 `DESC`） |
| **条目属性** | `purged_at` | `date-time` | - | 预计被系统物理抹除的过期时间戳 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 分页检索回收站]
curl -s -X GET "https://api.box.com/2.0/folders/trash/items?limit=100&offset=0" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!NOTE] **生命周期到期自动清理**
> 企业管理员可配置回收站保留周期（如 30 天或 90 天）。过期条目将被 Box 巡检后台物理清除，不再出现于 `/folders/trash/items` 列表中。

---

### 18. Trashed web links

#### 要素一：技术本质与核心能力
针对被软删除的外部网址快捷方式节点，提供专属的查阅、还原与硬销毁生命周期控制。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查看回收站内的 Web Link | `GET` | `/web_links/{web_link_id}/trash` | [Official Spec](https://developer.box.com/reference/get-web-links-id-trash) |
| 从回收站还原 Web Link | `POST` | `/web_links/{web_link_id}` | [Official Spec](https://developer.box.com/reference/post-web-links-id) |
| 永久硬删除 Web Link | `DELETE` | `/web_links/{web_link_id}/trash` | [Official Spec](https://developer.box.com/reference/delete-web-links-id-trash) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `web_link_id` | `string` | **是** | 待还原或销毁的 Web Link ID |
| **Body (POST)** | `name` | `string` | 否 | 还原时重命名的新标题 |
| **Body (POST)** | `parent.id` | `string` | 否 | 还原到的目标父目录 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查看]
curl -s -X GET "https://api.box.com/2.0/web_links/778899/trash" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [POST 还原]
curl -s -X POST "https://api.box.com/2.0/web_links/778899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{}'
```

```bash [DELETE 永久销毁]
curl -s -X DELETE "https://api.box.com/2.0/web_links/778899/trash" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!NOTE] **轻量元数据节点恢复无副作用**
> Web Link 恢复仅涉及纯元数据指向，无物理存储块搬运开销，恢复成功率极高，主要需注意原目录是否存在。

---

### 19. Archives

#### 要素一：技术本质与核心能力
Box 最新推出的 **Archives（冷数据归档）** 模块（基于官方 v2025.0 规范体系）。专用于将低频访问、需要长周期保存的数据从热存储分层剥离至具备成本效益与合规保护的归档池中。支持创建归档策略包、查询归档列表与调优状态。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询租户归档列表 | `GET` | `/archives` | [Official Spec](https://developer.box.com/reference/v2025.0/get-archives) |
| 创建新的归档策略包 | `POST` | `/archives` | [Official Spec](https://developer.box.com/reference/v2025.0/post-archives) |
| 更新归档配置或锁定状态 | `PUT` | `/archives/{archive_id}` | [Official Spec](https://developer.box.com/reference/v2025.0/put-archives-id) |
| 删除/注销归档任务 | `DELETE` | `/archives/{archive_id}` | [Official Spec](https://developer.box.com/reference/v2025.0/delete-archives-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 必须严格携带版本头：`2025.0` |
| **Query (GET)** | `limit` | `integer` | 否 | 每次返回上限（最大 1000） |
| **Query (GET)** | `marker` | `string` | 否 | 游标标识 |
| **Body (POST)** | `name` | `string` | **是** | 归档名称（1-100 字符，禁包含 `/` 与 `\`） |
| **Body (POST)** | `description` | `string` | 否 | 归档说明（最大 255 字符） |
| **Body (POST)** | `storage_policy_id` | `string` | 否 | 绑定的底层存储策略 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 创建归档策略]
curl -s -X POST "https://api.box.com/2.0/archives" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Cold_Tier_Backup_2026",
       "description": "Important cold tier storage archive",
       "storage_policy_id": "100001"
     }'
```

```bash [GET 查询归档清单]
curl -s -X GET "https://api.box.com/2.0/archives" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0"
```

```bash [PUT 更新归档配置]
curl -s -X PUT "https://api.box.com/2.0/archives/arc_12345" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Locked_Cold_Tier_Backup_2026"
     }'
```

```bash [DELETE 移除归档]
curl -s -X DELETE "https://api.box.com/2.0/archives/arc_12345" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0"
```
:::

#### 要素五：实战暗坑与避坑指南
> [!CAUTION] **版本协议头与企业级许可门槛**
> 1. Archives 属于 v2025.0+ 引入的最新合规特性，调用时必须显式附带 `box-version: 2025.0` 请求头，否则将响应 `400 Bad Request`。
> 2. 该能力依赖企业高级归档合规订阅（GCM Scope），在普通开发者沙箱环境中调用可能返回 `403 Feature Not Enabled`。

---

## 8.5 总结与工业级实践自检清单

在全面掌握 Content Management 19 大模块后，建议在每一次编写生产级脚本或调用代码前，进行如下「六重自检」：

```txt
┌──────────────────────────────────────────────────────────────┐
│                  Box API 工业级集成自检清单                  │
├──────────────────────────────────────────────────────────────┤
│ [ ] 1. 域名分流: 小文件/元数据用 api.box.com, 上传用 upload.box.com
│ [ ] 2. 根目录语义: 根目录 ID 严格填 "0", 严禁使用 "/" 或 "root"
│ [ ] 3. 大文件分流: 超过 50MB 必须使用 Uploads (Chunked) 分块协议
│ [ ] 4. 并发防护: 关键 PUT 元数据修改必须配合 ETag 与 If-Match 请求头
│ [ ] 5. 分页防护: 遍历上千文件目录必须开启 usemarker=true 游标模式
│ [ ] 6. 软删两阶段: 清楚区分 DELETE(入回收站) 与 /trash 永久销毁边界
└──────────────────────────────────────────────────────────────┘
```
