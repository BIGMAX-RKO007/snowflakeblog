# 第 01 章：Snowflake 账号申请与初始化配置

作为金融企业（如三井证券）在进行云原生转型验证时，首要步骤是申请并初始化 Snowflake 30天免费企业级试用环境（包含 $400 计算额度）。

---

## 1. 账号申请入口与关键参数

访问官方注册入口：[https://signup.snowflake.com/](https://signup.snowflake.com/)

| 配置项 | 推荐选型 | 业务与合规考量 |
| :--- | :--- | :--- |
| **Snowflake Edition** | **Enterprise（企业版）** | 支持 **90天时间旅行 (Time Travel)**、**动态数据脱敏 (Data Masking)** 以及多集群仓储，这是金融级监管与合规审计的最低门槛。 |
| **Cloud Provider** | **AWS (Amazon Web Services)** | 日资券商在东京区域使用率最高的底层云之一，生态工具链完备。 |
| **Region (区域)** | **Asia Pacific (Tokyo) - `ap-northeast-1`** | **数据主权合规要求**：日本金融厅 (FSA) 要求核心客户交易数据常驻境内，且网络延迟极低。 |

---

## 2. 注册全流程步骤与界面指引

### 步骤 1：访问注册入口并填写基本信息
输入姓名、公司邮箱及职位信息：
![注册首页](../images/01_img_01.png)

### 步骤 2：选择版本与云厂商区域
选择 **Enterprise** 版本，底层选择 **AWS - Asia Pacific (Tokyo)**：
![选择版本与区域](../images/01_img_02.png)

### 步骤 3：验证与激活邮件
提交后查收标题为 *"Activate your Snowflake account"* 的官方邮件，点击激活按钮：
![激活邮件提示](../images/01_img_03.png)
![邮件内容确认](../images/01_img_04.png)

### 步骤 4：设置管理员密码与首次登录
设置登录账号和安全强密码（初始具备 `ACCOUNTADMIN` 权限）：
![密码设置界面](../images/01_img_05.png)
![成功登录Snowsight](../images/01_img_06.png)

---

## 3. Web 控制台语言设置（切换为日语）

为了符合日本业务现场的操作习惯，可将 Snowsight 控制台界面语言设置为日语：

1. 点击左下角或右上角个人 Profile 图标进入 **Preferences（首选项）**；
2. 在 **Language & Region** 中，将语言切换为 **日本語 (Japanese)**：

![语言首选项设置](../images/01_img_09.png)
![界面切换为日语效果](../images/01_img_10.png)
![日语导航界面](../images/01_img_11.png)

---

## 4. 账号系统预置角色体系认知

```mermaid
graph TD
    AA["ACCOUNTADMIN\n全局最高权限\n(仅用于账单、组织管理、紧急授权)"]
    SA["SECURITYADMIN\n全局安全管理员\n(负责网络策略、安全审计、MANAGE GRANTS)"]
    UA["USERADMIN\n用户与角色管理员\n(负责创建/修改 USER 和 ROLE)"]
    SY["SYSADMIN\n系统运维管理员\n(负责创建 Warehouse、Database 等所有物理对象)"]

    AA --> SA
    SA --> UA
    AA --> SY
```

> [!CAUTION]
> **金融级安全军规**：日常运维与迁移绝不可使用 `ACCOUNTADMIN`。
> 必须遵循职责分离，使用 `USERADMIN` 统一管理人员角色生命周期，使用 `SYSADMIN` 管控计算与存储资源！
