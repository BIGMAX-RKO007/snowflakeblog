import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(
  defineConfig({
    title: '銀行証券DX：Oracle to Snowflake',
    description: '銀行証券コア取引データにおける Oracle から Snowflake への企業級データ移行実務',
    lastUpdated: true,
    cleanUrls: true,
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
            { text: 'プロジェクト概要', link: '/00_architecture_overview' },
            {
              text: '実践チュートリアル',
              items: [
                { text: '01. アカウント開設と初期設定', link: '/01_snowflake_signup' },
                { text: '02. Oracle環境構築と模擬データ投入', link: '/02_oracle_setup_and_data' },
                { text: '03. 3層RBAC権限モデルと環境構築', link: '/03_snowflake_rbac_setup' },
                { text: '04. データ移行実務 (COPY INTO)', link: '/04_data_migration' },
                { text: '05. 移行後データ突合検証・整合性監査', link: '/05_data_reconciliation' },
                { text: '06. トラブルシューティングとベストプラクティス', link: '/06_troubleshooting_tips' },
              ]
            }
          ],
          sidebar: [
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
      },
      zh: {
        label: '简体中文',
        lang: 'zh-CN',
        link: '/zh/',
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
            }
          ],
          sidebar: [
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
