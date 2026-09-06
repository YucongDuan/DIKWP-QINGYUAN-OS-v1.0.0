# DIKWP-QINGYUAN-OS 1.0.0

## 清源：主动认知环境免疫、操纵断链与证据回流系统

DIKWP-QINGYUAN-OS 是一个可离线运行、可审计、可申诉的研究型原型。它主动识别和削弱以下有害链条：

- 缺少证据却以绝对口吻传播的高风险主张；
- 通过恐惧、羞辱、稀缺、保密、权威幻觉或群体压力操纵决策；
- 依靠自动播放、无限滚动、变动奖励、连续签到和推送压力制造依赖；
- 面向儿童、老人、患者、低识读群体或经济困难者的定向利用；
- 把广告、课程、社群、投资、疗愈或“正能量”包装成知识，却隐瞒利益关系、证据和退款条件；
- 在现实生活中要求转账、停药、借贷、断联、退出教育或放弃独立核验的高控制行为。

系统不把“负面”当作“错误”。有证据的坏消息、公共安全警示、批评、异议、揭弊、悲伤和现实风险必须被保护；正面、励志、疗愈和成功叙事也不因听起来积极而自动可信。

## 核心路线

系统同时运行三个非同构世界模型：

1. **证据—来源模型**：逐条主张检查来源、证据、可复核性、独立性和确定性是否匹配；
2. **操纵—成瘾—利益模型**：检查压力语言、上瘾设计、定向脆弱人群和商业回流；
3. **伤害—自主—表达权模型**：评估潜在伤害，同时保护批评、异议、少数意见和公共利益材料。

三个模型不压缩成单一“真假分”或“正负能量分”。结论采用硬约束、分层处置和明确的权利防火墙。

## 八级处置阶梯

| 级别 | 处置 | 说明 |
|---|---|---|
| L0 | 保留并呈现 | 对有证据的警示、批评和公共利益内容不得因“负面”而降权 |
| L1 | 来源与证据回流 | 展示作者、来源、利益关系、主张证据和不确定性 |
| L2 | 语境与反证 | 提供替代解释、范围限制和可改变结论的证据要求 |
| L3 | 认知摩擦 | 分享延迟、购买冷静期、关闭自动播放、会话休息和引用确认 |
| L4 | 操纵断链 | 建议停止上瘾式推荐增益、暂停联盟营销和未披露商业激励 |
| L5 | 限时隔离 | 仅对高风险、低证据且存在操纵/脆弱人群利用的内容提出可申诉临时隔离 |
| L6 | 具名人工复核 | 医疗、金融、法律或平台安全人员按权限复核 |
| L7 | 紧急安全升级 | 仅在明确迫近危险时进入适用的人类安全流程 |

对单个条目，原型只生成计划，不自动执行任何外部删除、降权、举报、支付冻结、网络通信或现实控制。`shield` 命令可以在用户明确控制的本地副本中主动关闭自动播放、移除推荐增益、暂停本地获利资格并临时收起高风险条目；原始记录进入可申诉的哈希归档而不被删除：

```text
automatic_external_action_authority = 0
automatic_deletion = false
```

## 快速运行

### 单文件 ZipApp

```bash
python DIKWP_QINGYUAN_OS.pyz inspect
python DIKWP_QINGYUAN_OS.pyz demo --output outputs/demo
python DIKWP_QINGYUAN_OS.pyz suite --output outputs/reference
python DIKWP_QINGYUAN_OS.pyz assess my_item.json --output outputs/my_item
python DIKWP_QINGYUAN_OS.pyz shield demo_feed/mixed_feed.json --output outputs/shielded_feed
python DIKWP_QINGYUAN_OS.pyz verify outputs/my_item/evidence_ledger.jsonl
```

### 源码运行

```bash
PYTHONPATH=src python -m qingyuan_os inspect
PYTHONPATH=src python -m qingyuan_os suite --examples examples --output outputs/reference
```

Windows 可双击 `run_demo.bat`，Linux/macOS 可执行 `./run_demo.sh`。自定义输入可从 `templates/content_item_template.json` 开始。

## 每次评估的输出

- `assessment.json`：三个世界模型和非聚合向量；
- `intervention_plan.json`：限时、可逆、可申诉的处置计划；
- `truth_return_card.json`：主张级证据、来源、利益和权利说明；
- `incentive_circuit_map.json`：创作者、主张、推荐、受众和支付回路；
- `real_life_support_plan.json`：现实生活中的非强制支持步骤；
- `semantic_graph.json`：D/I/K/W/P 多记录及实际路径；
- `residual_queue.json`：证据、来源、利益、权利和现实结果债务；
- `appeal_packet.json`：独立申诉与改判接口；
- `qingyuan_certificate.json`：机器可读有界证书；
- `evidence_ledger.jsonl`：十阶段哈希链接账本；
- 中英文报告与输出哈希清单。

## D/I/K/W/P

- **D**：可重放的来源、内容哈希、证据记录；
- **I**：会改变后继的差异、矛盾、操纵信号和模型冲突；
- **K**：只在提交材料和声明语境内成立的有界评估；
- **W**：自主、伤害、脆弱人群、公共利益、表达权和公平后果；
- **P**：具名、限时、可逆、可申诉的处置与证据回流关系。

D/I/K/W/P 是开放角色而非五级道德阶梯，允许全部 25 类有向路径。新证据可以撤销目的，后果可以重开知识，目的可以要求新的证据。

## 现实生活协议

对不愿改变认知的人，系统不以羞辱、孤立、欺骗或强制“去洗脑”为策略。它优先：

1. 检查迫近危险；
2. 请求只核对一项具体主张的许可；
3. 将人、关系、主张和利益链分开；
4. 暂停转账、停药、借贷、断联等不可逆决定；
5. 做一个小而可逆的独立核验；
6. 恢复替代关系、信息源和生活选择；
7. 高风险时由具备资质的人依法介入。

对拒绝讨论且不存在迫近危险的人，只保护共享财产、未成年人、组织职责和明确法律边界，不强制改造其世界观。

## 适用边界

本系统：

- 不是万能事实判定器；
- 不从关键词推断恶意；
- 不从信念诊断精神疾病或行为能力；
- 不进行法律裁决、临床诊断或信用评分；
- 不提供秘密永久黑名单；
- 不把用户、作者或群体等同于某条主张；
- 不以政治立场、宗教、文化、悲观情绪或不受欢迎的观点作为限制理由；
- 不宣称合成案例已证明现实效果。

## 许可证

- 核心运行时代码：AGPL-3.0-or-later；
- Schema 与互操作接口：Apache-2.0；
- 文档、案例和图形：CC BY 4.0。

Copyright © 2026 Yucong Duan and contributors.
