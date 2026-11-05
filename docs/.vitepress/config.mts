import process from 'node:process'
import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(
  defineConfig({
    base: process.env.BASE_PATH || (process.env.CF_PAGES ? '/' : (process.env.GITHUB_ACTIONS ? '/snowflakeblog/' : '/')),
    title: '銀行証券DX：Oracle to Snowflake',
    description: '銀行証券コア取引データにおける Oracle から Snowflake への企業級データ移行実務',
    lastUpdated: true,
    cleanUrls: true,
    ignoreDeadLinks: true,
    rewrites: {
      'ja/:rest*': ':rest*'
    },

    locales: {
      root: {
        label: '日本語',
        lang: 'ja-JP',
        link: '/',
        themeConfig: {
          nav: [
            { text: 'Snowflake 数倉実践', link: '/00_architecture_overview' },
            { text: 'dbt 分析エンジニアリング', link: '/dbt/01_what_is_dbt' },
            {
              text: '数倉実践チュートリアル',
              items: [
                { text: '01. アカウント開設と初期設定', link: '/01_snowflake_signup' },
                { text: '02. Oracle環境構築と模擬データ投入', link: '/02_oracle_setup_and_data' },
                { text: '03. 3層RBAC権限モデルと環境構築', link: '/03_snowflake_rbac_setup' },
                { text: '04. データ移行実務 (COPY INTO)', link: '/04_data_migration' },
                { text: '05. 移行後データ突合検証・整合性監査', link: '/05_data_reconciliation' },
                { text: '06. トラブルシューティングとベストプラクティス', link: '/06_troubleshooting_tips' },
                { text: '07. Snowflake Openflow による Box 連携と Cortex 検索', link: '/07_openflow_box_integration' },
                {
                  text: '08. Box API 実践ガイド (8-1 〜 8-8)',
                  collapsed: false,
                  items: [
                    { text: '08-1. Content Management（19大モジュール）', link: '/08_01_box_content_management' },
                    { text: '08-2. Authentication & Users（10大モジュール）', link: '/08_02_box_authentication_users' },
                    { text: '08-3. Sharing & Collaboration（14大モジュール）', link: '/08_03_box_sharing_collaboration' },
                    { text: '08-4. Search & Metadata（11大モジュール）', link: '/08_04_box_search_metadata' },
                    { text: '08-5. Events & Webhooks（2大モジュール）', link: '/08_05_box_events_webhooks' },
                    { text: '08-6. AI & Intelligence（3大モジュール）', link: '/08_06_box_ai_intelligence' },
                    { text: '08-7. Automation & Workflows（7大モジュール）', link: '/08_07_box_automation_workflows' },
                    { text: '08-8. Administration & Compliance（20大モジュール）', link: '/08_08_box_admin_compliance' },
                  ]
                },
                { text: '09. Snowflake 外部 API アクセス完全ガイド', link: '/09_snowflake_external_api_access' },
                { text: '10. Streamlit in Snowflake データ可視化', link: '/10_snowflake_streamlit_visualization' },
                { text: '11. Snowflake コスト計算とガバナンス実践', link: '/11_snowflake_cost_management' },
              ]
            }
          ],
          sidebar: {
            '/dbt/': [
              {
                text: 'dbt 分析エンジニアリング実践',
                items: [
                  { text: '01. dbt 入門とモダンデータスタック', link: '/dbt/01_what_is_dbt' },
                  { text: '02. 開発基盤構築とKey-Pair認証', link: '/dbt/02_environment_setup_and_snowflake' },
                ]
              }
            ],
            '/': [
              {
                text: '銀行証券移行実践マニュアル',
                items: [
                  { text: '00. プロジェクト背景とアーキテクチャ設計', link: '/00_architecture_overview' },
                  { text: '01. Snowflake アカウント開設と初期設定', link: '/01_snowflake_signup' },
                  { text: '02. Oracle 移行元環境構築と模擬データ投入', link: '/02_oracle_setup_and_data' },
                  { text: '03. 3層RBAC権限モデルと環境構築', link: '/03_snowflake_rbac_setup' },
                  { text: '04. データ移行実務（抽出・ステージ・取込）', link: '/04_data_migration' },
                  { text: '05. 移行後データ突合検証・整合性監査', link: '/05_data_reconciliation' },
                  { text: '06. トラブルシューティングとベストプラクティス', link: '/06_troubleshooting_tips' },
                  { text: '07. Snowflake Openflow による Box 連携と Cortex 検索', link: '/07_openflow_box_integration' },
                  {
                    text: '08. Box API 実践ガイド (8-1 〜 8-8)',
                    collapsed: false,
                    items: [
                      { text: '08-1. Content Management（19大モジュール）', link: '/08_01_box_content_management' },
                      { text: '08-2. Authentication & Users（10大モジュール）', link: '/08_02_box_authentication_users' },
                      { text: '08-3. Sharing & Collaboration（14大モジュール）', link: '/08_03_box_sharing_collaboration' },
                      { text: '08-4. Search & Metadata（11大モジュール）', link: '/08_04_box_search_metadata' },
                      { text: '08-5. Events & Webhooks（2大モジュール）', link: '/08_05_box_events_webhooks' },
                      { text: '08-6. AI & Intelligence（3大モジュール）', link: '/08_06_box_ai_intelligence' },
                      { text: '08-7. Automation & Workflows（7大モジュール）', link: '/08_07_box_automation_workflows' },
                      { text: '08-8. Administration & Compliance（20大モジュール）', link: '/08_08_box_admin_compliance' },
                    ]
                  },
                  { text: '09. Snowflake 外部 API アクセス完全ガイド', link: '/09_snowflake_external_api_access' },
                  { text: '10. Streamlit in Snowflake (SiS) データ可視化', link: '/10_snowflake_streamlit_visualization' },
                  { text: '11. Snowflake コスト計算とガバナンス実践', link: '/11_snowflake_cost_management' },
                ]
              }
            ]
          },
          docFooter: {
            prev: '前のページ',
            next: '次のページ'
          },
          outline: {
            label: '目次',
            level: 'deep'
          }
        }
      },
      zh: {
        label: '简体中文',
        lang: 'zh-CN',
        link: '/zh/',
        themeConfig: {
          nav: [
            { text: 'Snowflake 数仓实战', link: '/zh/00_architecture_overview' },
            { text: 'dbt 分析工程实战', link: '/zh/dbt/01_what_is_dbt' },
            {
              text: '数仓实战章节',
              items: [
                { text: '01. 账号申请与配置', link: '/zh/01_snowflake_signup' },
                { text: '02. Oracle环境与模拟数据', link: '/zh/02_oracle_setup_and_data' },
                { text: '03. Snowflake RBAC权限搭建', link: '/zh/03_snowflake_rbac_setup' },
                { text: '04. 数据迁移实战', link: '/zh/04_data_migration' },
                { text: '05. 数据突合对账', link: '/zh/05_data_reconciliation' },
                { text: '06. 生产避坑指南', link: '/zh/06_troubleshooting_tips' },
                { text: '07. Openflow 接入 Box 与 Cortex 知识检索', link: '/zh/07_openflow_box_integration' },
                {
                  text: '08. Box API 实战指南 (8-1 〜 8-8)',
                  collapsed: false,
                  items: [
                    { text: '08-1. Content Management（19 大模块）', link: '/zh/08_01_box_content_management' },
                    { text: '08-2. Authentication & Users（10 大模块）', link: '/zh/08_02_box_authentication_users' },
                    { text: '08-3. Sharing & Collaboration（14 大模块）', link: '/zh/08_03_box_sharing_collaboration' },
                    { text: '08-4. Search & Metadata（11 大模块）', link: '/zh/08_04_box_search_metadata' },
                    { text: '08-5. Events & Webhooks（2 大模块）', link: '/zh/08_05_box_events_webhooks' },
                    { text: '08-6. AI & Intelligence（3 大模块）', link: '/zh/08_06_box_ai_intelligence' },
                    { text: '08-7. Automation & Workflows（7 大模块）', link: '/zh/08_07_box_automation_workflows' },
                    { text: '08-8. Administration & Compliance（20 大模块）', link: '/zh/08_08_box_admin_compliance' },
                  ]
                },
                { text: '09. Snowflake 外部 API 调用全流程实战', link: '/zh/09_snowflake_external_api_access' },
                { text: '10. Streamlit in Snowflake 数据可视化全流程实战', link: '/zh/10_snowflake_streamlit_visualization' },
                { text: '11. Snowflake 费用成本精算与治理实战', link: '/zh/11_snowflake_cost_management' },
              ]
            }
          ],
          sidebar: {
            '/zh/dbt/': [
              {
                text: 'dbt 现代分析工程实战',
                items: [
                  { text: '01. 初识 dbt 与现代数据栈', link: '/zh/dbt/01_what_is_dbt' },
                  { text: '02. 工程底座搭建与Key-Pair安全认证', link: '/zh/dbt/02_environment_setup_and_snowflake' },
                ]
              }
            ],
            '/zh/': [
              {
                text: '银行证券迁移实战教程',
                items: [
                  { text: '00. 业务背景与架构设计', link: '/zh/00_architecture_overview' },
                  { text: '01. Snowflake 账号申请与初始化', link: '/zh/01_snowflake_signup' },
                  { text: '02. Oracle 11g 搭建与模拟数据', link: '/zh/02_oracle_setup_and_data' },
                  { text: '03. Snowflake RBAC 权限设计实战', link: '/zh/03_snowflake_rbac_setup' },
                  { text: '04. 数据迁移：Stage 与 COPY INTO', link: '/zh/04_data_migration' },
                  { text: '05. 迁移后两方数据差异突合对账', link: '/zh/05_data_reconciliation' },
                  { text: '06. 生产避坑指南与解决方案', link: '/zh/06_troubleshooting_tips' },
                  { text: '07. Snowflake Openflow 接入 Box 与 Cortex 知识检索', link: '/zh/07_openflow_box_integration' },
                  {
                    text: '08. Box API 实战指南 (8-1 〜 8-8)',
                    collapsed: false,
                    items: [
                      { text: '08-1. Content Management（19 大模块）', link: '/zh/08_01_box_content_management' },
                      { text: '08-2. Authentication & Users（10 大模块）', link: '/zh/08_02_box_authentication_users' },
                      { text: '08-3. Sharing & Collaboration（14 大模块）', link: '/zh/08_03_box_sharing_collaboration' },
                      { text: '08-4. Search & Metadata（11 大模块）', link: '/zh/08_04_box_search_metadata' },
                      { text: '08-5. Events & Webhooks（2 大模块）', link: '/zh/08_05_box_events_webhooks' },
                      { text: '08-6. AI & Intelligence（3 大模块）', link: '/zh/08_06_box_ai_intelligence' },
                      { text: '08-7. Automation & Workflows（7 大模块）', link: '/zh/08_07_box_automation_workflows' },
                      { text: '08-8. Administration & Compliance（20 大模块）', link: '/zh/08_08_box_admin_compliance' },
                    ]
                  },
                  { text: '09. Snowflake 外部 API 调用全流程实战', link: '/zh/09_snowflake_external_api_access' },
                  { text: '10. Streamlit in Snowflake 数据可视化全流程实战', link: '/zh/10_snowflake_streamlit_visualization' },
                  { text: '11. Snowflake 费用成本精算与治理实战', link: '/zh/11_snowflake_cost_management' },
                ]
              }
            ]
          },
          docFooter: {
            prev: '上一篇',
            next: '下一篇'
          },
          outline: {
            label: '本页导航',
            level: 'deep'
          }
        }
      }
    },

    themeConfig: {
      siteTitle: '銀行証券 DX 移行実戦',
      logo: '/snowflake.svg',
      logoLink: '/',
      search: {
        provider: 'local',
        options: {
          locales: {
            root: {
              translations: {
                button: { buttonText: 'ドキュメント検索', buttonAriaLabel: 'ドキュメント検索' },
                modal: {
                  noResultsText: '該当する結果が見つかりません',
                  resetButtonTitle: '検索条件をクリア',
                  footer: { selectText: '選択', navigateText: '移動', closeText: '閉じる' }
                }
              }
            },
            zh: {
              translations: {
                button: { buttonText: '搜索文档', buttonAriaLabel: '搜索文档' },
                modal: {
                  noResultsText: '无法找到相关结果',
                  resetButtonTitle: '清除查询条件',
                  footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' }
                }
              }
            }
          }
        }
      },
      footer: {
        message: 'Enterprise Data Cloud Architecture',
        copyright: 'Copyright © 2026 Mitsui Securities Migration Project Team'
      }
    },

    vite: {
      optimizeDeps: {
        include: ['fastdom', 'mermaid']
      }
    },

    mermaid: {
      theme: 'default'
    }
  })
)
