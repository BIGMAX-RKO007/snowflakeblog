import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(
  defineConfig({
    title: '三井証券DX：Oracle to Snowflake',
    description: '三井证券核心交易数据从 Oracle 到 Snowflake 的企业级数据迁移与 RBAC 实战',
    lastUpdated: true,
    cleanUrls: true,

    locales: {
      root: {
        label: '简体中文',
        lang: 'zh-CN',
        link: '/zh/00_architecture_overview',
        themeConfig: {
          nav: [
            { text: '项目概览', link: '/zh/00_architecture_overview' },
            {
              text: '实战教程',
              items: [
                { text: '01. 账号申请与配置', link: '/zh/01_snowflake_signup' },
                { text: '02. Oracle环境与模拟数据', link: '/zh/02_oracle_setup_and_data' },
                { text: '03. Snowflake RBAC权限搭建', link: '/zh/03_snowflake_rbac_setup' },
                { text: '04. 数据迁移实战', link: '/zh/04_data_migration' },
                { text: '05. 数据突合对账', link: '/zh/05_data_reconciliation' },
                { text: '06. 生产避坑指南', link: '/zh/06_troubleshooting_tips' },
              ]
            },
            {
              text: '脚本仓库',
              items: [
                { text: 'Oracle DDL & 数据脚本', link: 'https://github.com/BIGMAX-RKO007/snowflakeblog/tree/main/scripts/oracle' },
                { text: 'Snowflake 权限与迁移脚本', link: 'https://github.com/BIGMAX-RKO007/snowflakeblog/tree/main/scripts/snowflake' },
                { text: '突合验证脚本', link: 'https://github.com/BIGMAX-RKO007/snowflakeblog/tree/main/scripts/validation' },
              ]
            }
          ],
          sidebar: [
            {
              text: '三井证券迁移实战教程',
              items: [
                { text: '00. 业务背景与架构设计', link: '/zh/00_architecture_overview' },
                { text: '01. Snowflake 账号申请与初始化', link: '/zh/01_snowflake_signup' },
                { text: '02. Oracle 11g 搭建与模拟数据', link: '/zh/02_oracle_setup_and_data' },
                { text: '03. Snowflake RBAC 权限设计实战', link: '/zh/03_snowflake_rbac_setup' },
                { text: '04. 数据迁移：Stage 与 COPY INTO', link: '/zh/04_data_migration' },
                { text: '05. 迁移后两方数据差异突合对账', link: '/zh/05_data_reconciliation' },
                { text: '06. 生产避坑指南与解决方案', link: '/zh/06_troubleshooting_tips' },
              ]
            }
          ],
          docFooter: {
            prev: '上一篇',
            next: '下一篇'
          },
          outline: {
            label: '本页导航',
            level: 'deep'
          }
        }
      },
      ja: {
        label: '日本語',
        lang: 'ja-JP',
        link: '/ja/00_architecture_overview',
        themeConfig: {
          nav: [
            { text: 'プロジェクト概要', link: '/ja/00_architecture_overview' },
            {
              text: '実践チュートリアル',
              items: [
                { text: '01. アカウント開設と初期設定', link: '/ja/01_snowflake_signup' },
                { text: '02. Oracle環境構築と模擬データ投入', link: '/ja/02_oracle_setup_and_data' },
                { text: '03. RBAC権限モデルと環境構築', link: '/ja/03_snowflake_rbac_setup' },
                { text: '04. データ移行実務 (COPY INTO)', link: '/ja/04_data_migration' },
                { text: '05. 移行後データ突合検証', link: '/ja/05_data_reconciliation' },
                { text: '06. 本番運用トラブルシューティング', link: '/ja/06_troubleshooting_tips' },
              ]
            },
            {
              text: 'GitHub リポジトリ',
              link: 'https://github.com/BIGMAX-RKO007/snowflakeblog'
            }
          ],
          sidebar: [
            {
              text: '三井証券移行実践マニュアル',
              items: [
                { text: '00. プロジェクト背景とアーキテクチャ設計', link: '/ja/00_architecture_overview' },
                { text: '01. Snowflake アカウント開設と初期設定', link: '/ja/01_snowflake_signup' },
                { text: '02. Oracle 移行元環境構築と模擬データ投入', link: '/ja/02_oracle_setup_and_data' },
                { text: '03. 3層RBAC権限モデルと環境構築', link: '/ja/03_snowflake_rbac_setup' },
                { text: '04. データ移行実務（抽出・ステージ・取込）', link: '/ja/04_data_migration' },
                { text: '05. 移行後データ突合検証・整合性監査', link: '/ja/05_data_reconciliation' },
                { text: '06. トラブルシューティングとベストプラクティス', link: '/ja/06_troubleshooting_tips' },
              ]
            }
          ],
          docFooter: {
            prev: '前のページ',
            next: '次のページ'
          },
          outline: {
            label: '目次',
            level: 'deep'
          }
        }
      }
    },

    themeConfig: {
      siteTitle: '三井証券 DX 移行実戦',
      logo: 'https://www.snowflake.com/wp-content/themes/snowflake/assets/img/snowflake-logo.svg',
      socialLinks: [
        { icon: 'github', link: 'https://github.com/BIGMAX-RKO007/snowflakeblog' }
      ],
      search: {
        provider: 'local',
        options: {
          locales: {
            root: {
              translations: {
                button: { buttonText: '搜索文档', buttonAriaLabel: '搜索文档' },
                modal: {
                  noResultsText: '无法找到相关结果',
                  resetButtonTitle: '清除查询条件',
                  footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' }
                }
              }
            },
            ja: {
              translations: {
                button: { buttonText: 'ドキュメント検索', buttonAriaLabel: 'ドキュメント検索' },
                modal: {
                  noResultsText: '該当する結果が見つかりません',
                  resetButtonTitle: '検索条件をクリア',
                  footer: { selectText: '選択', navigateText: '移動', closeText: '閉じる' }
                }
              }
            }
          }
        }
      },
      footer: {
        message: 'Released under the MIT License.',
        copyright: 'Copyright © 2026 Mitsui Securities Migration Project Team'
      }
    },

    mermaid: {
      theme: 'default'
    }
  })
)
