# 第 08-2 讲：Box 核心 API 实战指南 —— Authentication & Users（认证与用户管理）

> **【开门见山 · 技术定位】**
>
> 企业级身份治理与凭证生命周期：OAuth 2.0 握手、JWT 认证、用户/用户组自动化配置与设备准入控制。无业务噪音，纯粹以技术概念、身份状态机与 HTTP 契约为主线。

> 📖 **Box 官方权威规范与文档**：
> - [Box API Reference - Authentication & Users 资源手册](https://developer.box.com/reference/resources/user/)
> - [Box 身份认证与安全治理开发者指南](https://developer.box.com/guides/authentication/)
> - [OAuth 2.0 与 CCG 凭据生命周期官方规范](https://developer.box.com/guides/authentication/oauth2/)

---

## 08-2.1 全景 CRUD 能力矩阵沙盘

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
| **01** | **Authorization** | **OAuth 2.0 授权、凭证发放与主动吊销**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">OAuth 2.0 authorization and token management</span> | `root_readwrite` | ✅ | ✅ | ❌ | ❌ | [直达](#01-authorization) |
| **02** | **Users** | **企业成员生命周期（创建、配额、状态切换与注销）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage users</span> | `manage_users` | ✅ | ✅ | ✅ | ✅ | [直达](#02-users) |
| **03** | **User avatars** | **用户头像图片二进制流获取、上传与删除**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage user profile images</span> | `manage_users` | ✅ | ✅ | ❌ | ✅ | [直达](#03-user-avatars) |
| **04** | **Groups** | **企业用户组体系管理（部门划分与批量授权）**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Create and manage user groups</span> | `manage_groups` | ✅ | ✅ | ✅ | ✅ | [直达](#04-groups) |
| **05** | **Group memberships** | **用户组与成员绑定关系映射及管理员提权**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage user membership in groups</span> | `manage_groups` | ✅ | ✅ | ✅ | ✅ | [直达](#05-group-memberships) |
| **06** | **Invites** | **企业外部成员受邀入驻与邀请状态查询**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Invite users to join Box</span> | `manage_users` | ✅ | ✅ | ❌ | ❌ | [直达](#06-invites) |
| **07** | **Email aliases** | **用户辅助邮箱别名绑定与主邮箱切换**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage user email aliases</span> | `manage_users` | ✅ | ✅ | ❌ | ✅ | [直达](#07-email-aliases) |
| **08** | **Session termination** | **紧急安全事件响应：强制注销用户/组的全部终端会话**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Terminate user or group sessions</span> | `manage_users` | ❌ | ✅ | ❌ | ❌ | [直达](#08-session-termination) |
| **09** | **Device pinners** | **企业设备信任绑定治理与离线访问权限吊销**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage device pinning for offline access</span> | `manage_enterprise` | ✅ | ❌ | ❌ | ✅ | [直达](#09-device-pinners) |
| **10** | **External Users** | **外部非受管协作者跨域访问治理与批量清理 (v2025.0)**<br><span style="font-size:0.75rem;color:var(--vp-c-text-2)">Manage external user access</span> | `manage_users` | ✅ | ✅ | ❌ | ❌ | [直达](#10-external-users) |

</div>

---

## 08-2.2 统一技术前置规范

在调用本分类 API 之前，所有 HTTP 客户端均需遵循以下基准通信契约：

```txt
1. Base API URL:       https://api.box.com/2.0
2. 认证凭证 Header:    Authorization: Bearer <ACCESS_TOKEN>
3. 内容交互 Header:    Content-Type: application/json (OAuth 表单或上传除外)
4. 租户企业标识:       企业管理员上下文或 As-User: <USER_ID> 代理标头
```

---

## 08-2.3 单个 API 模块五要素深度实操

### <span id="01-authorization">01. Authorization</span>

#### 要素一：技术本质与核心能力
管理 Box 开放平台的身份授信协议链。提供标准 Authorization Code 流程、客户端凭证（CCG）、JWT 企业服务账号签名握手，以及 Refresh Token 自动轮换与凭证主动注销销毁机制。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 获取用户授权重定向 URL | `GET` | `/authorize` | [Official Spec](https://developer.box.com/reference/get-authorize) |
| 换取或刷新 Access / Refresh Token | `POST` | `/oauth2/token` | [Official Spec](https://developer.box.com/reference/post-oauth2-token) |
| 主动废弃指定 Token | `POST` | `/oauth2/revoke` | [Official Spec](https://developer.box.com/reference/post-oauth2-revoke) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Query (Auth)** | `response_type` | `string` | **是** | 固定为 'code' |
| **Query (Auth)** | `client_id` | `string` | **是** | 应用唯一客户端标识 |
| **Body (Token)** | `grant_type` | `string` | **是** | 授权模式：'authorization_code' / 'refresh_token' / 'client_credentials' |
| **Body (Token)** | `code` | `string` | **否** | OAuth 重定向获取的一次性 Code |
| **Body (Token)** | `client_secret` | `string` | **是** | 客户端应用通信密钥 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 获取 Token]
curl -s -X POST "https://api.box.com/oauth2/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=authorization_code" \
     -d "code=AUTH_CODE_HERE" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET"
```

```bash [POST 刷新 Token]
curl -s -X POST "https://api.box.com/oauth2/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=refresh_token" \
     -d "refresh_token=YOUR_REFRESH_TOKEN" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET"
```

```bash [POST 吊销 Token]
curl -s -X POST "https://api.box.com/oauth2/revoke" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET" \
     -d "token=TOKEN_TO_REVOKE"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> Refresh Token 一次性轮换击穿：Box 的 Refresh Token 在被使用一次后立即作废，并生成新的 Refresh Token。分布式微服务多副本同时刷新时，后发请求必报 400 invalid_grant。生产环境必须采用分布式锁严格单点串行刷新。

---

### <span id="02-users">02. Users</span>

#### 要素一：技术本质与核心能力
负责租户内部所有账号实体的状态机生命周期。管理受管用户（Managed User）与无邮箱的平台集成专用应用用户（App User），支持存储配额限定、封禁冻结以及级联强制注销。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 分页查询企业租户用户列表 | `GET` | `/users` | [Official Spec](https://developer.box.com/reference/get-users) |
| 获取当前认证主体上下文详情 | `GET` | `/users/me` | [Official Spec](https://developer.box.com/reference/get-users-me) |
| 新建受管用户或 App User | `POST` | `/users` | [Official Spec](https://developer.box.com/reference/post-users) |
| 更新用户信息、角色、配额或状态 | `PUT` | `/users/{user_id}` | [Official Spec](https://developer.box.com/reference/put-users-id) |
| 删除或注销指定用户 | `DELETE` | `/users/{user_id}` | [Official Spec](https://developer.box.com/reference/delete-users-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `user_id` | `string` | **是** | 目标用户 ID（'me' 表示当前调用上下文） |
| **Body (POST)** | `name` | `string` | **是** | 用户姓名 |
| **Body (POST)** | `login` | `string` | **否** | 用户主登录邮箱（App User 可免填） |
| **Body (POST)** | `is_platform_access_only` | `boolean` | **否** | 是否创建纯 API App User |
| **Body (PUT)** | `status` | `enum` | **否** | 状态：'active', 'inactive', 'cannot_delete_edit' |
| **Body (PUT)** | `space_amount` | `int64` | **否** | 存储空间字节数配额上限 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查当前用户]
curl -s -X GET "https://api.box.com/2.0/users/me" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [POST 建新用户]
curl -s -X POST "https://api.box.com/2.0/users" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"name": "Dev_Engineer_01", "login": "dev01@example.com", "role": "coadmin"}'
```

```bash [PUT 封禁用户]
curl -s -X PUT "https://api.box.com/2.0/users/123456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"status": "inactive"}'
```

```bash [DELETE 彻底注销]
curl -s -X DELETE "https://api.box.com/2.0/users/123456?notify=false" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 非空用户删除报错：待删除用户根目录下若仍有文件资产，直接调用 DELETE 会响应 400 Bad Request。必须先调用 Transfer folders 过户资产，或在请求 URL 尾部强制追加 ?force=true。

---

### <span id="03-user-avatars">03. User avatars</span>

#### 要素一：技术本质与核心能力
管理用户的个性化视觉形象。提供标准二进制字节流获取、multipart/form-data 头像替换与重置为默认剪影。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 获取用户头像图片二进制流 | `GET` | `/users/{user_id}/avatar` | [Official Spec](https://developer.box.com/reference/get-users-id-avatar) |
| 上传或更新用户自定义头像 | `POST` | `/users/{user_id}/avatar` | [Official Spec](https://developer.box.com/reference/post-users-id-avatar) |
| 删除用户头像并恢复默认 | `DELETE` | `/users/{user_id}/avatar` | [Official Spec](https://developer.box.com/reference/delete-users-id-avatar) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `user_id` | `string` | **是** | 目标用户唯一标识符 |
| **FormData** | `pic` | `binary` | **是** | 上传的头像二进制图片流（jpg/png/gif） |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 提取头像]
curl -s -X GET "https://api.box.com/2.0/users/123456/avatar" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" -o avatar.png
```

```bash [POST 上传头像]
curl -s -X POST "https://api.box.com/2.0/users/123456/avatar" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -F pic=@./profile.png
```

```bash [DELETE 恢复默认]
curl -s -X DELETE "https://api.box.com/2.0/users/123456/avatar" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 文件体积上限：图片体积不得超过 1MB，否则服务端直接响应 400 Bad Request。

---

### <span id="04-groups">04. Groups</span>

#### 要素一：技术本质与核心能力
支持企业组织架构的逻辑映射。通过创建跨部门或项目制用户组，实现对文件树协同权限的批量赋权与集中回收。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 分页查询企业内所有用户组 | `GET` | `/groups` | [Official Spec](https://developer.box.com/reference/get-groups) |
| 创建新的企业用户组 | `POST` | `/groups` | [Official Spec](https://developer.box.com/reference/post-groups) |
| 获取指定用户组详情 | `GET` | `/groups/{group_id}` | [Official Spec](https://developer.box.com/reference/get-groups-id) |
| 修改用户组名称或邀请权限 | `PUT` | `/groups/{group_id}` | [Official Spec](https://developer.box.com/reference/put-groups-id) |
| 解散并删除用户组 | `DELETE` | `/groups/{group_id}` | [Official Spec](https://developer.box.com/reference/delete-groups-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `group_id` | `string` | **是** | 用户组唯一 ID |
| **Body (POST)** | `name` | `string` | **是** | 用户组名称（企业内唯一） |
| **Body (POST)** | `invitability_level` | `enum` | **否** | 邀请权限级别：'admins_only', 'admins_and_members', 'all_managed_users' |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 创建组]
curl -s -X POST "https://api.box.com/2.0/groups" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"name": "Data_Lake_Operators", "invitability_level": "admins_only"}'
```

```bash [GET 查所有组]
curl -s -X GET "https://api.box.com/2.0/groups?limit=50" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [PUT 修改组名]
curl -s -X PUT "https://api.box.com/2.0/groups/778899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"name": "Core_ETL_Engineers"}'
```

```bash [DELETE 删除组]
curl -s -X DELETE "https://api.box.com/2.0/groups/778899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 组名租户内唯一性约束：创建已存在的组名将触发 409 Conflict。写入前必须通过名称搜索或列表查询确保幂等。

---

### <span id="05-group-memberships">05. Group memberships</span>

#### 要素一：技术本质与核心能力
管理用户与用户组之间的多对多关联桥接表。支持为组内成员赋予普通成员（member）或组管理员（admin）角色。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询指定组下的所有组员 | `GET` | `/groups/{group_id}/memberships` | [Official Spec](https://developer.box.com/reference/get-groups-id-memberships) |
| 查询指定用户所属的所有组 | `GET` | `/users/{user_id}/memberships` | [Official Spec](https://developer.box.com/reference/get-users-id-memberships) |
| 将用户加入指定组 | `POST` | `/group_memberships` | [Official Spec](https://developer.box.com/reference/post-group-memberships) |
| 修改成员在组内的角色 | `PUT` | `/group_memberships/{id}` | [Official Spec](https://developer.box.com/reference/put-group-memberships-id) |
| 将用户从指定组中剔除 | `DELETE` | `/group_memberships/{id}` | [Official Spec](https://developer.box.com/reference/delete-group-memberships-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `group_membership_id` | `string` | **是** | 成员绑定记录唯一 ID |
| **Body (POST)** | `user.id` | `string` | **是** | 用户 ID |
| **Body (POST)** | `group.id` | `string` | **是** | 用户组 ID |
| **Body (POST/PUT)** | `role` | `enum` | **否** | 组内角色：'member' 或 'admin' |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 加入组]
curl -s -X POST "https://api.box.com/2.0/group_memberships" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"user": {"id": "123456"}, "group": {"id": "778899"}, "role": "member"}'
```

```bash [PUT 提拔为组管理]
curl -s -X PUT "https://api.box.com/2.0/group_memberships/gm_9988" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"role": "admin"}'
```

```bash [DELETE 移出组]
curl -s -X DELETE "https://api.box.com/2.0/group_memberships/gm_9988" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 重复加入报 409：用户已经在组内时重复添加会抛出 409 Conflict。自动化脚本写入前必须做好已存在异常捕获或先查后加。

---

### <span id="06-invites">06. Invites</span>

#### 要素一：技术本质与核心能力
负责企业成员入驻招募通道。通过邮件向外部自由用户发送企业受管邀请，并追踪邀请被接受或过期的生命周期。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 向指定邮箱发送企业入驻邀请函 | `POST` | `/invites` | [Official Spec](https://developer.box.com/reference/post-invites) |
| 查询指定邀请的审批与接受状态 | `GET` | `/invites/{invite_id}` | [Official Spec](https://developer.box.com/reference/get-invites-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `invite_id` | `string` | **是** | 邀请记录 ID |
| **Body (POST)** | `enterprise.id` | `string` | **是** | 目标企业租户 ID |
| **Body (POST)** | `actionable_by.login` | `string` | **是** | 被邀请者的登录邮箱 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 发出邀请]
curl -s -X POST "https://api.box.com/2.0/invites" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"enterprise": {"id": "111222"}, "actionable_by": {"login": "partner@vendor.com"}}'
```

```bash [GET 查邀请进度]
curl -s -X GET "https://api.box.com/2.0/invites/inv_456" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 目标邮箱已被第三方企业受管：若受邀用户属于其他 Box Enterprise，邀请将无法直接合并，必须由其原管理员释放。

---

### <span id="07-email-aliases">07. Email aliases</span>

#### 要素一：技术本质与核心能力
管理用户的多个邮箱识别符。支持向用户账号绑定别名邮箱，使外部用户可以通过任意已认证别名向其共享文件。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 查询用户绑定的所有别名邮箱 | `GET` | `/users/{user_id}/email_aliases` | [Official Spec](https://developer.box.com/reference/get-users-id-email-aliases) |
| 为用户增加辅助别名邮箱 | `POST` | `/users/{user_id}/email_aliases` | [Official Spec](https://developer.box.com/reference/post-users-id-email-aliases) |
| 删除已绑定的指定别名邮箱 | `DELETE` | `/users/{user_id}/email_aliases/{alias_id}` | [Official Spec](https://developer.box.com/reference/delete-users-id-email-aliases-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `user_id` | `string` | **是** | 用户 ID |
| **Path** | `email_alias_id` | `string` | **是** | 别名记录唯一 ID |
| **Body (POST)** | `email` | `string` | **是** | 待绑定的新邮箱地址 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 列出别名]
curl -s -X GET "https://api.box.com/2.0/users/123456/email_aliases" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [POST 绑定别名]
curl -s -X POST "https://api.box.com/2.0/users/123456/email_aliases" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"email": "dev.backup@example.com"}'
```

```bash [DELETE 解绑别名]
curl -s -X DELETE "https://api.box.com/2.0/users/123456/email_aliases/ea_8899" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 主登录邮箱不可通过别名端点删除：主登录邮箱受用户核心唯一索引保护，若要删除主邮箱，必须先将其替换为其他地址。

---

### <span id="08-session-termination">08. Session termination</span>

#### 要素一：技术本质与核心能力
企业应对账号凭证泄露或员工突发离职的最高防线。在服务端向指定用户或整个组的所有终端广播会话注销指令，瞬间作废全部 Cookies、OAuth Token 与桌面挂载。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 批量强制终结指定用户的全部在线活跃会话 | `POST` | `/users/terminate_sessions` | [Official Spec](https://developer.box.com/reference/post-users-terminate-sessions) |
| 批量强制终结指定用户组下所有成员的会话 | `POST` | `/groups/terminate_sessions` | [Official Spec](https://developer.box.com/reference/post-groups-terminate-sessions) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Body (POST)** | `user_ids` | `string[]` | **是** | 强制注销的用户 ID 数组 |
| **Body (POST)** | `user_logins` | `string[]` | **否** | 强制注销的用户登录邮箱数组 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 强退用户会话]
curl -s -X POST "https://api.box.com/2.0/users/terminate_sessions" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"user_ids": ["123456", "987654"]}'
```

```bash [POST 强退整组会话]
curl -s -X POST "https://api.box.com/2.0/groups/terminate_sessions" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"group_ids": ["778899"]}'
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 异步处理特征（202 Accepted）：接口立即返回 202，后台异步进行会话清理。调用方如需确认，需通过事件流（Events Stream）观察 session_terminated 事件日志。

---

### <span id="09-device-pinners">09. Device pinners</span>

#### 要素一：技术本质与核心能力
管控企业物理终端接入边界。Box Device Trust 允许将用户绑定的移动或桌面硬件生成 Pin 记录，当设备丢失或报废时，管理员可通过 API 强制解除绑定。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 分页查询企业内所有被 Pin 绑定的设备清单 | `GET` | `/enterprises/{enterprise_id}/device_pinners` | [Official Spec](https://developer.box.com/reference/get-enterprises-id-device-pinners) |
| 查询单个设备的硬件标识与绑定详情 | `GET` | `/device_pinners/{id}` | [Official Spec](https://developer.box.com/reference/get-device-pinners-id) |
| 解除并删除指定设备的 Pin 信任关系 | `DELETE` | `/device_pinners/{id}` | [Official Spec](https://developer.box.com/reference/delete-device-pinners-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Path** | `enterprise_id` | `string` | **是** | 企业租户唯一标识符 |
| **Path** | `device_pinner_id` | `string` | **是** | 设备 Pin 记录唯一 ID |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [GET 查企业绑定设备]
curl -s -X GET "https://api.box.com/2.0/enterprises/111222/device_pinners?direction=desc" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

```bash [DELETE 强制解绑设备]
curl -s -X DELETE "https://api.box.com/2.0/device_pinners/dp_5566" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 需要企业 Device Pinning 策略开启：若租户 Admin Console 未开启该策略，接口将响应 403 Forbidden 或空清单。

---

### <span id="10-external-users">10. External Users</span>

#### 要素一：技术本质与核心能力
基于 Box 官方 v2025.0 规范，提供对参与企业协同的外部第三方用户的治理能力。支持批量提交外部协作者访问关系移除作业。

#### 要素二：核心能力与端点拓扑字典
| 能力动作 | HTTP 动词 | URI 拓扑 | 官方深度直通车 |
| :--- | :---: | :--- | :--- |
| 提交批量删除外部协作者访问权的后台作业 | `POST` | `/v2025.0/external_users/delete_jobs` | [Official Spec](https://developer.box.com/reference/v2025.0/post-external-users-delete-jobs) |
| 轮询外部用户清理任务的执行状态 | `GET` | `/v2025.0/external_users/delete_jobs/{id}` | [Official Spec](https://developer.box.com/reference/v2025.0/get-external-users-delete-jobs-id) |

#### 要素三：核心请求参数与 Payload 字段拓扑
| 字段位置 | 字段名称 (Field) | 类型 (Type) | 必填 | 规范定义与说明 |
| :--- | :--- | :---: | :---: | :--- |
| **Header** | `box-version` | `string` | **是** | 必须指定版本头：'2025.0' |
| **Body (POST)** | `user_ids` | `string[]` | **是** | 待清除访问权限的外部用户 ID 列表 |

#### 要素四：尚硅谷三板斧实操 (cURL)
::: code-group
```bash [POST 提交清理作业]
curl -s -X POST "https://api.box.com/2.0/external_users/delete_jobs" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0" \
     -H "Content-Type: application/json" \
     -d '{"user_ids": ["ext_1122", "ext_3344"]}'
```

```bash [GET 查作业进度]
curl -s -X GET "https://api.box.com/2.0/external_users/delete_jobs/job_9988" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "box-version: 2025.0"
```

:::

#### 要素五：实操暗坑与避坑指南【重点】
> [!CAUTION] **生产避险要点**
> 外部用户（External Users）非物理删除：该作业负责批量剥离外部协作者对本企业全部资产的读写映射，不会删除外部用户在其他租户中的独立账号。

---

## 08-2.4 总结与工业级实践自检清单

```txt
┌──────────────────────────────────────────────────────────────┐
│             Box API 08-2 工业级集成自检清单             │
├──────────────────────────────────────────────────────────────┤
│ [ ] 1. Token 互斥刷新: 生产集群多副本必须使用分布式锁串行刷新 refresh_token
│ [ ] 2. 别名解绑顺序: 严禁直接 DELETE 主登录邮箱，必须先 PUT 切换主邮箱
│ [ ] 3. 非空用户删除: 拥有个人资产的用户删除前必须显式过户或带 force=true
│ [ ] 4. 组名全局唯一: 同租户内用户组重名将触发 409 Conflict，写入前需幂等探测
│ [ ] 5. 会话强退异步性: terminate_sessions 响应 202 Accepted，秒级内全面注销 Token
│ [ ] 6. 外部协作者治理: External Users 清理作业为跨域解绑，不销毁外部物理账号
└──────────────────────────────────────────────────────────────┘
```
