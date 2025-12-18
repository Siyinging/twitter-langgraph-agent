# Design: 12格精简棋盘设计

## Requirements

### 设计目标
基于MVP核心循环需求，设计一个12格的精简棋盘版本：
1. **降低复杂度**：从28格减少到12格，保持核心教育价值
2. **快速实现**：每格事件设计简单明确，开发周期2-3周
3. **平衡分布**：合理分配投资、事件、决策类格子比例
4. **教育导向**：每个格子都有明确的金融知识学习点

### 功能约束
**包含元素：**
- 4个投资资产格（BTC、ETH、传统资产、SignalPlus）
- 4个市场事件格（利好、风险、新闻、黑天鹅）
- 2个策略决策格（顾问、对冲）
- 2个特殊功能格（起始点、奖励）

**排除元素：**
- 复杂的期权策略组合
- 多步骤决策流程
- 实时API数据依赖
- 多人交互功能

## Solution

### 1. 棋盘布局设计

#### 1.1 12格矩形布局
```
┌─────────┬─────────┬─────────┬─────────┐
│ 格子1   │ 格子2   │ 格子3   │ 格子4   │
│ 🏠起始点│📈市场机会│₿BTC矿场 │🎯投资顾问│
├─────────┼─────────┼─────────┼─────────┤
│ 格子12  │         │         │ 格子5   │
│🚀信号站  │  中央   │  信息   │⟠ETH DeFi│
├─────────┤  显示   │  面板   ├─────────┤
│ 格子11  │  区域   │  区域   │ 格子6   │
│⚠️黑天鹅 │         │         │⚠️风险警告│
├─────────┼─────────┼─────────┼─────────┤
│ 格子10  │ 格子9   │ 格子8   │ 格子7   │
│🎁奖励池 │🛡️风险对冲│📰突发新闻│🏦蓝筹ETF│
└─────────┴─────────┴─────────┴─────────┘
```

#### 1.2 棋盘尺寸规范
```css
.game-board {
  width: 600px;
  height: 450px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 8px;
  margin: 0 auto;
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.board-space {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  min-height: 120px;
}

.center-area {
  grid-column: 2 / 4;
  grid-row: 2 / 3;
  background: linear-gradient(135deg, #1e40af, #3730a3);
  color: white;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
```

### 2. 格子详细设计

#### 2.1 投资资产区 (4格)

**格子3 - BTC矿场**
```javascript
const btcMiningFarm = {
  id: 3,
  type: 'INVESTMENT_ASSET',
  name: 'BTC矿场',
  icon: '₿',
  basePrice: 200,
  
  // 收益机制
  income: {
    baseAmount: 15,        // 基础每回合收益
    volatilityFactor: 0.8, // 受市场波动影响
    upgradable: true       // 可升级
  },
  
  // 风险因素
  risks: [
    { type: 'REGULATION', probability: 0.1, impact: -0.3 },
    { type: 'POWER_COST', probability: 0.15, impact: -0.2 },
    { type: 'DIFFICULTY_INCREASE', probability: 0.2, impact: -0.15 }
  ],
  
  // 教育内容
  learningPoints: [
    '理解比特币挖矿的工作量证明机制',
    '学习挖矿难度调整和奖励减半',
    '认识挖矿的能源消耗和环境影响',
    '了解矿池和独立挖矿的区别'
  ],
  
  // 事件处理
  onLand: function(player) {
    if (!player.assets.btcMining) {
      return this.showPurchaseDialog(player);
    } else {
      return this.showUpgradeDialog(player);
    }
  },
  
  showPurchaseDialog: function(player) {
    const currentPrice = this.calculateCurrentPrice();
    return {
      type: 'DECISION',
      title: 'BTC矿场投资机会',
      description: `发现一座现代化比特币矿场，装备最新ASIC设备。当前市场条件下，预期每回合收益$${this.income.baseAmount}。`,
      marketInfo: {
        btcPrice: game.market.btcPrice,
        difficulty: '当前难度适中',
        powerCost: '电费成本稳定'
      },
      options: [
        {
          text: `投资购买 ($${currentPrice})`,
          cost: currentPrice,
          enabled: player.cash >= currentPrice,
          action: () => this.purchase(player, currentPrice),
          explanation: '开始挖矿事业，获得稳定BTC收益'
        },
        {
          text: '暂不投资',
          cost: 0,
          action: () => ({ message: '等待更好的投资时机' }),
          explanation: '观望市场，寻找更佳机会'
        }
      ],
      timeout: 15000,
      defaultOption: 1
    };
  }
};
```

**格子5 - ETH DeFi协议**
```javascript
const ethDefiProtocol = {
  id: 5,
  type: 'INVESTMENT_ASSET',
  name: 'ETH DeFi协议',
  icon: '⟠',
  basePrice: 150,
  
  // DeFi特有机制
  defiMechanics: {
    stakingReward: 12,      // 质押奖励
    liquidityMining: 8,     // 流动性挖矿
    impermanentLoss: 0.05,  // 无常损失风险
    smartContractRisk: 0.02 // 智能合约风险
  },
  
  // 教育重点
  learningPoints: [
    '了解去中心化金融(DeFi)基本概念',
    '学习流动性提供和收益农场',
    '认识无常损失和智能合约风险',
    '掌握质押和借贷机制'
  ],
  
  onLand: function(player) {
    const currentAPY = this.calculateAPY();
    return {
      type: 'DECISION',
      title: 'DeFi协议参与机会',
      description: `顶级DeFi协议开放流动性挖矿，当前年化收益率${currentAPY}%。支持ETH质押和LP代币挖矿。`,
      riskWarning: '注意：DeFi投资存在智能合约风险和无常损失',
      options: [
        {
          text: `参与DeFi ($${this.basePrice})`,
          cost: this.basePrice,
          enabled: player.cash >= this.basePrice,
          action: () => this.stakeDeFi(player),
          details: `质押ETH获得${this.defiMechanics.stakingReward}%年收益`
        },
        {
          text: '学习DeFi知识',
          cost: 10,
          action: () => this.openLearningCenter(),
          details: '花费$10获得DeFi基础教程'
        },
        {
          text: '暂不参与',
          cost: 0,
          action: () => ({ message: '谨慎观望DeFi市场' })
        }
      ]
    };
  }
};
```

**格子7 - 蓝筹ETF**
```javascript
const bluechipETF = {
  id: 7,
  type: 'INVESTMENT_ASSET',  
  name: '蓝筹ETF',
  icon: '🏦',
  basePrice: 100,
  
  // 传统金融特性
  characteristics: {
    stability: 'HIGH',
    volatility: 0.15,       // 低波动率
    dividendYield: 0.08,    // 8%年分红
    correlationWithCrypto: -0.3  // 与加密货币负相关
  },
  
  learningPoints: [
    '理解ETF的分散投资原理',
    '学习传统金融资产配置',
    '对比传统投资与加密投资',
    '了解风险管理的重要性'
  ],
  
  onLand: function(player) {
    return {
      type: 'DECISION',
      title: '蓝筹ETF稳健投资',
      description: '投资标普500指数ETF，享受美股蓝筹公司成长红利。风险低，收益稳定。',
      comparison: {
        vs_crypto: '相比加密货币，波动率低70%',
        vs_cash: '相比现金，年化收益高5-8%'
      },
      options: [
        {
          text: `购买ETF份额 ($${this.basePrice})`,
          cost: this.basePrice,
          enabled: player.cash >= this.basePrice,
          action: () => this.purchaseETF(player),
          benefits: ['每回合稳定收益$8', '分散投资风险', '对冲加密资产']
        },
        {
          text: '定投计划',
          cost: 50,
          action: () => this.setupDCA(player),
          details: '每回合自动投入$50，分散风险'
        },
        {
          text: '继续观望',
          cost: 0,
          action: () => ({ message: '保持现金仓位' })
        }
      ]
    };
  }
};
```

**格子12 - SignalPlus股份**
```javascript
const signalplusShares = {
  id: 12,
  type: 'INVESTMENT_ASSET',
  name: 'SignalPlus股份',
  icon: '🚀',
  basePrice: 300,
  
  // 特殊优势
  advantages: {
    professionalData: true,    // 获得专业数据权限
    learningBonus: 1.5,       // 学习经验1.5倍加成  
    tradingDiscount: 0.1,     // 交易手续费9折
    exclusiveContent: true     // 独家内容权限
  },
  
  learningPoints: [
    '了解期权交易平台商业模式',
    '学习金融科技公司价值评估',
    '认识衍生品交易的重要性',
    '掌握投资平台股权的优势'
  ],
  
  onLand: function(player) {
    return {
      type: 'DECISION',
      title: 'SignalPlus股权投资',
      description: '投资领先的加密期权交易平台，获得平台收益分成和专业权限。',
      exclusiveBenefits: [
        '📊 专业市场数据访问权限',
        '📚 VIP学习资源和一对一指导',
        '💰 平台收益分成（每回合$20）',
        '🎯 交易手续费优惠'
      ],
      options: [
        {
          text: `购买股份 ($${this.basePrice})`,
          cost: this.basePrice,
          enabled: player.cash >= this.basePrice,
          action: () => this.purchaseShares(player),
          highlight: true
        },
        {
          text: '申请试用权限',
          cost: 50,
          action: () => this.requestTrial(player),
          details: '体验7天VIP权限'
        },
        {
          text: '访问SignalPlus官网',
          cost: 0,
          action: () => window.open('https://signalplus.com'),
          details: '了解平台详细信息'
        }
      ],
      callToAction: '🚀 加入SignalPlus生态，与专业交易者同行！'
    };
  }
};
```

#### 2.2 市场事件区 (4格)

**格子2 - 市场机会**
```javascript
const marketOpportunity = {
  id: 2,
  type: 'MARKET_EVENT',
  name: '市场机会',
  icon: '📈',
  
  // 事件库
  events: [
    {
      id: 'bull_run',
      title: '牛市来临！',
      description: '主要加密货币集体突破，BTC冲破阻力位，市场情绪高涨',
      impact: 'BULLISH',
      effect: {
        assetMultiplier: 1.15,  // 所有资产价值+15%
        cashBonus: 100         // 额外现金奖励
      },
      probability: 0.25
    },
    {
      id: 'institutional_adoption',
      title: '机构入场',
      description: '知名投资银行宣布配置加密资产，带动市场信心提升',
      impact: 'BULLISH',
      effect: {
        specificAssets: { BTC: 1.2, ETH: 1.18 },
        experienceBonus: 50
      },
      probability: 0.20
    },
    {
      id: 'tech_breakthrough',
      title: '技术突破',
      description: 'Layer2解决方案取得重大进展，区块链可扩展性问题得到改善',
      impact: 'BULLISH',
      effect: {
        futureIncomeMultiplier: 1.1,  // 未来收益+10%
        unlockNewOpportunity: true
      },
      probability: 0.15
    }
  ],
  
  onLand: function(player) {
    const event = this.selectRandomEvent();
    const result = this.applyEventEffect(player, event);
    
    return {
      type: 'EVENT_RESULT',
      title: event.title,
      description: event.description,
      outcome: result,
      educational: this.getEducationalContent(event),
      signalPlusLink: 'https://signalplus.com/market-analysis'
    };
  },
  
  selectRandomEvent: function() {
    const totalWeight = this.events.reduce((sum, e) => sum + e.probability, 0);
    let random = Math.random() * totalWeight;
    
    for (const event of this.events) {
      random -= event.probability;
      if (random <= 0) return event;
    }
    
    return this.events[0]; // 默认返回第一个
  },
  
  getEducationalContent: function(event) {
    const educational = {
      bull_run: {
        concept: '牛市特征',
        explanation: '牛市是价格持续上涨的市场状态，通常伴随交易量放大、市场情绪乐观',
        strategy: '牛市策略：适度增仓，但要控制风险，避免盲目追高',
        indicators: ['价格突破关键阻力', '成交量放大', '市场情绪指标上升']
      },
      institutional_adoption: {
        concept: '机构投资影响',
        explanation: '机构投资者入场通常带来大量资金流入，提升市场稳定性',
        strategy: '跟随机构策略，但要注意机构可能的获利回吐',
        indicators: ['机构持仓增加', '大额转账活动', '期货市场溢价']
      },
      tech_breakthrough: {
        concept: '技术驱动价值',
        explanation: '区块链技术进步是长期价值增长的根本驱动力',
        strategy: '关注技术基本面，布局有真实应用场景的项目',
        indicators: ['开发活跃度', '用户增长', '实际应用落地']
      }
    };
    
    return educational[event.id] || {};
  }
};
```

**格子6 - 风险警告**
```javascript
const riskWarning = {
  id: 6,
  type: 'MARKET_EVENT',
  name: '风险警告',
  icon: '⚠️',
  
  events: [
    {
      id: 'regulatory_crackdown',
      title: '监管收紧',
      description: '监管部门发布新规，对加密货币交易实施更严格监管',
      impact: 'BEARISH',
      effect: {
        assetMultiplier: 0.88,  // 资产价值-12%
        complianceCost: 50      // 合规成本
      },
      probability: 0.30
    },
    {
      id: 'market_manipulation',
      title: '市场操控',
      description: '发现大户联合操控市场，监管介入调查，市场信心受损',
      impact: 'BEARISH',
      effect: {
        randomAssetLoss: 0.15,  // 随机资产损失15%
        trustPenalty: true
      },
      probability: 0.20
    },
    {
      id: 'security_breach',
      title: '安全事件',
      description: '主要交易所发生安全漏洞，用户资金安全引发担忧',
      impact: 'BEARISH',
      effect: {
        securityCost: 80,       // 安全升级成本
        temporaryFreeze: 1      // 暂停1回合交易
      },
      probability: 0.25
    }
  ],
  
  onLand: function(player) {
    const event = this.selectRandomEvent();
    
    // 提供风险缓解选项
    return {
      type: 'RISK_DECISION',
      title: event.title,
      description: event.description,
      riskLevel: this.calculateRiskLevel(player, event),
      options: [
        {
          text: '承担风险',
          cost: 0,
          action: () => this.acceptRisk(player, event),
          risk: '可能损失较大，但无额外成本'
        },
        {
          text: '购买保险',
          cost: this.calculateInsuranceCost(event),
          action: () => this.buyInsurance(player, event),
          benefit: '减少50%潜在损失'
        },
        {
          text: '临时清仓',
          cost: player.totalAssetValue * 0.02, // 2%交易成本
          action: () => this.liquidateAssets(player),
          benefit: '完全避免损失，但支付交易费用'
        }
      ],
      educational: this.getRiskEducation(event)
    };
  },
  
  getRiskEducation: function(event) {
    return {
      concept: '风险管理原则',
      principles: [
        '分散投资：不要把所有鸡蛋放在一个篮子里',
        '止损设置：预先确定最大可接受损失',
        '保险对冲：适当购买保险或对冲工具',
        '信息获取：及时关注市场风险信号'
      ],
      warningSignals: [
        '异常大额交易',
        '监管政策变化',
        '技术安全漏洞',
        '市场情绪极端化'
      ]
    };
  }
};
```

**格子8 - 突发新闻**
```javascript
const breakingNews = {
  id: 8,
  type: 'MARKET_EVENT',
  name: '突发新闻',
  icon: '📰',
  
  newsCategories: {
    MACRO_ECONOMIC: {
      weight: 0.3,
      events: [
        '美联储宣布利率决议，市场波动加剧',
        '全球通胀数据公布，投资者情绪分化',
        '地缘政治紧张局势升级，避险情绪上升'
      ]
    },
    
    CRYPTO_SPECIFIC: {
      weight: 0.4,
      events: [
        'BTC现货ETF获得重大进展',
        '以太坊网络升级成功完成',
        '新兴公链获得重大投资'
      ]
    },
    
    REGULATORY: {
      weight: 0.2,
      events: [
        '重要国家更新加密货币法规',
        '国际监管协调取得进展',
        '税务政策影响加密资产'
      ]
    },
    
    TECHNOLOGICAL: {
      weight: 0.1,
      events: [
        '量子计算对加密安全的影响',
        'Web3基础设施重大突破',
        'DeFi协议安全升级完成'
      ]
    }
  },
  
  onLand: function(player) {
    const news = this.generateNews();
    const impact = this.calculateNewsImpact(news);
    
    return {
      type: 'NEWS_EVENT',
      title: '📰 突发新闻',
      news: news,
      impact: impact,
      reaction: {
        message: '新闻事件将在下回合生效，现在可以调整投资策略',
        delay: 1, // 延迟1回合生效
        options: [
          {
            text: '调整投资组合',
            action: () => this.showPortfolioAdjustment(player),
            details: '根据新闻预判市场走向'
          },
          {
            text: '获取深度分析',
            cost: 30,
            action: () => this.getAnalysis(news),
            benefit: '获得专业解读和投资建议'
          },
          {
            text: '保持当前策略',
            cost: 0,
            action: () => ({ message: '维持现状，观察市场反应' })
          }
        ]
      },
      signalPlusIntegration: {
        link: 'https://t.signalplus.com/crypto-news/trending-24h?lang=zh-CN',
        reward: { experience: 20, cash: 50 },
        message: '访问SignalPlus获取更多市场资讯'
      }
    };
  }
};
```

**格子11 - 黑天鹅事件**
```javascript
const blackSwanEvent = {
  id: 11,
  type: 'MARKET_EVENT', 
  name: '黑天鹅事件',
  icon: '⚠️',
  
  // 低概率高影响事件
  events: [
    {
      id: 'flash_crash',
      title: '闪电崩盘',
      description: '市场出现技术性错误，导致价格瞬间暴跌50%后快速恢复',
      probability: 0.02,
      impact: {
        immediateEffect: -0.3,  // 立即损失30%
        recoveryRate: 0.8,      // 80%概率下回合恢复
        learningValue: 100      // 高学习价值
      }
    },
    {
      id: 'exchange_hack',
      title: '重大黑客攻击',
      description: '全球最大交易所遭受攻击，10亿美元资金被盗',
      probability: 0.01,
      impact: {
        marketPanic: true,
        assetFreeze: 2,         // 冻结2回合
        safetyBonus: 200        // 安全资产获得溢价
      }
    },
    {
      id: 'quantum_threat',
      title: '量子计算威胁',
      description: '量子计算突破威胁现有加密算法，市场恐慌性抛售',
      probability: 0.005,
      impact: {
        techPanic: true,
        modernAssetsPenalty: -0.4,  // 现代资产重创
        traditionalAssetBonus: 0.2  // 传统资产受益
      }
    }
  ],
  
  onLand: function(player) {
    // 黑天鹅事件触发概率很低
    if (Math.random() > 0.05) { // 95%概率无事发生
      return {
        type: 'NO_EVENT',
        title: '虚惊一场',
        description: '市场传言四起，但经核实为不实消息。',
        lesson: '在投资中要学会辨别真假信息，避免被市场情绪左右。',
        reward: { experience: 10 }
      };
    }
    
    const event = this.selectCriticalEvent();
    
    return {
      type: 'BLACK_SWAN',
      title: '⚠️ ' + event.title,
      description: event.description,
      warning: '这是一个低概率高影响事件，请谨慎应对！',
      
      // 应对选择
      options: [
        {
          text: '紧急止损',
          cost: player.totalAssetValue * 0.05, // 5%手续费
          action: () => this.emergencyStop(player, event),
          result: '快速止损，减少损失但支付高额手续费'
        },
        {
          text: '坚持持有',
          cost: 0,
          action: () => this.holdThrough(player, event),
          result: '承受全部冲击，但可能获得恢复后的超额收益'
        },
        {
          text: '危机抄底',
          cost: player.cash * 0.5,
          enabled: player.cash >= 100,
          action: () => this.buyTheDip(player, event),
          result: '在危机中寻找机会，高风险高回报'
        }
      ],
      
      educational: {
        concept: '黑天鹅事件',
        definition: '极低概率但影响巨大的不可预测事件',
        examples: ['2008金融危机', '新冠疫情', '911事件'],
        strategy: [
          '保持适当现金流动性',
          '分散投资降低单点风险', 
          '建立应急预案和止损机制',
          '危机中的机会识别能力'
        ],
        nassimTaleb: '纳西姆·塔勒布提出的黑天鹅理论提醒我们要为极端事件做准备'
      }
    };
  }
};
```

#### 2.3 策略决策区 (2格)

**格子4 - 投资顾问**
```javascript
const investmentAdvisor = {
  id: 4,
  type: 'STRATEGY_DECISION',
  name: '投资顾问',
  icon: '🎯',
  serviceFee: 20,
  
  services: {
    MARKET_FORECAST: {
      name: '市场预测',
      cost: 20,
      duration: 3, // 3回合有效
      benefits: [
        '提前知晓市场事件类型（利好/利空）',
        '获得资产价格走势提示',
        '风险事件早期预警'
      ]
    },
    
    PORTFOLIO_ANALYSIS: {
      name: '投资组合分析',
      cost: 30,
      benefits: [
        '获得当前投资组合风险评估',
        '推荐最优资产配置比例',
        '个性化投资建议'
      ]
    },
    
    LEARNING_ACCELERATION: {
      name: '学习加速',
      cost: 25,
      duration: 5, // 5回合有效
      benefits: [
        '所有学习获得的经验值×1.5',
        '解锁高级投资策略',
        '专属SignalPlus教程访问'
      ]
    }
  },
  
  onLand: function(player) {
    return {
      type: 'SERVICE_SELECTION',
      title: '🎯 专业投资顾问',
      description: '资深投资顾问为您提供个性化投资建议和市场分析',
      
      // 顾问评估当前状况
      currentAssessment: this.assessPlayer(player),
      
      services: Object.entries(this.services).map(([key, service]) => ({
        id: key,
        name: service.name,
        cost: service.cost,
        duration: service.duration,
        benefits: service.benefits,
        enabled: player.cash >= service.cost,
        recommended: this.isRecommended(player, key)
      })),
      
      freeAdvice: this.getFreeAdvice(player),
      
      options: [
        ...Object.keys(this.services).map(serviceId => ({
          text: this.services[serviceId].name,
          cost: this.services[serviceId].cost,
          enabled: player.cash >= this.services[serviceId].cost,
          action: () => this.purchaseService(player, serviceId)
        })),
        {
          text: '免费咨询',
          cost: 0,
          action: () => this.provideFreeAdvice(player),
          details: '获得基础投资建议和学习指导'
        },
        {
          text: '暂不需要',
          cost: 0,
          action: () => ({ message: '继续自主投资' })
        }
      ]
    };
  },
  
  assessPlayer: function(player) {
    const assessment = {
      riskLevel: 'MODERATE',
      diversification: 'LOW',
      cashRatio: player.cash / player.totalValue,
      recommendations: []
    };
    
    // 风险评估
    if (player.cash < player.totalValue * 0.1) {
      assessment.riskLevel = 'HIGH';
      assessment.recommendations.push('建议保持更多现金流动性');
    }
    
    // 多元化评估
    const assetCount = Object.keys(player.assets || {}).length;
    if (assetCount < 2) {
      assessment.diversification = 'LOW';
      assessment.recommendations.push('考虑分散投资，降低单一资产风险');
    }
    
    // 现金比例评估
    if (assessment.cashRatio > 0.5) {
      assessment.recommendations.push('现金过多，可以考虑增加投资');
    } else if (assessment.cashRatio < 0.1) {
      assessment.recommendations.push('现金不足，建议保留应急资金');
    }
    
    return assessment;
  },
  
  getFreeAdvice: function(player) {
    const advice = [];
    
    if (player.level < 3) {
      advice.push('💡 新手建议：先学习基础知识，再进行投资');
    }
    
    if (player.cash > player.totalValue * 0.8) {
      advice.push('💡 现金管理：适度投资，让资金增值');
    }
    
    if (!player.visitedSignalPlus) {
      advice.push('💡 学习资源：访问SignalPlus获取专业知识');
    }
    
    return advice.length > 0 ? advice : ['💡 您的投资策略总体合理，继续保持！'];
  }
};
```

**格子9 - 风险对冲**
```javascript
const riskHedging = {
  id: 9,
  type: 'STRATEGY_DECISION',
  name: '风险对冲',
  icon: '🛡️',
  
  hedgingStrategies: {
    INSURANCE_POLICY: {
      name: '投资保险',
      baseCost: 30,
      coverage: 0.8, // 覆盖80%损失
      duration: 5,   // 5回合有效
      description: '为投资组合购买保险，减少突发风险损失'
    },
    
    SAFE_HAVEN: {
      name: '避险资产',
      cost: 50,
      allocation: 0.3, // 30%资产转为避险
      returns: 0.02,   // 2%稳定回报
      description: '将部分资产转换为黄金等避险资产'
    },
    
    STOP_LOSS: {
      name: '止损机制',
      cost: 15,
      trigger: 0.15, // 15%损失触发
      duration: 10,  // 10回合有效
      description: '设置自动止损，资产跌幅超过15%时自动卖出'
    },
    
    DIVERSIFICATION: {
      name: '多元化配置',
      cost: 40,
      rebalancing: true,
      correlation: -0.5, // 负相关资产配置
      description: '重新配置投资组合，增加负相关资产'
    }
  },
  
  onLand: function(player) {
    const currentRisk = this.assessRisk(player);
    const recommendations = this.getRecommendations(player, currentRisk);
    
    return {
      type: 'RISK_MANAGEMENT',
      title: '🛡️ 风险对冲策略',
      description: '专业风险管理顾问帮助您构建防御性投资组合',
      
      riskAssessment: {
        level: currentRisk.level,
        factors: currentRisk.factors,
        exposure: currentRisk.exposure,
        recommendation: recommendations
      },
      
      strategies: Object.entries(this.hedgingStrategies).map(([key, strategy]) => ({
        id: key,
        name: strategy.name,
        cost: this.calculateCost(player, strategy),
        description: strategy.description,
        effectiveness: this.calculateEffectiveness(player, strategy),
        enabled: player.cash >= this.calculateCost(player, strategy),
        recommended: recommendations.includes(key)
      })),
      
      options: [
        ...Object.keys(this.hedgingStrategies).map(strategyId => ({
          text: this.hedgingStrategies[strategyId].name,
          cost: this.calculateCost(player, this.hedgingStrategies[strategyId]),
          enabled: player.cash >= this.calculateCost(player, this.hedgingStrategies[strategyId]),
          action: () => this.implementStrategy(player, strategyId),
          details: this.hedgingStrategies[strategyId].description
        })),
        {
          text: '风险评估报告',
          cost: 10,
          action: () => this.generateRiskReport(player),
          details: '获得详细的投资组合风险分析'
        },
        {
          text: '暂不对冲',
          cost: 0,
          action: () => ({ message: '选择承担当前风险水平' })
        }
      ],
      
      educational: {
        concept: '投资风险对冲',
        principles: [
          '对冲不是为了消除所有风险，而是管理风险',
          '适度对冲可以平滑收益曲线',
          '对冲成本要与潜在损失进行权衡',
          '分散投资是最基本的对冲策略'
        ],
        warrenBuffett: '巴菲特说：风险来自于你不知道自己在做什么'
      }
    };
  },
  
  assessRisk: function(player) {
    let riskScore = 0;
    const factors = [];
    
    // 现金不足风险
    const cashRatio = player.cash / player.totalValue;
    if (cashRatio < 0.1) {
      riskScore += 3;
      factors.push('流动性风险：现金比例过低');
    }
    
    // 集中度风险
    const assetCount = Object.keys(player.assets || {}).length;
    if (assetCount < 3) {
      riskScore += 2;
      factors.push('集中度风险：投资过于集中');
    }
    
    // 市场风险
    if (game.market.volatility > 0.7) {
      riskScore += 2;
      factors.push('市场风险：当前波动率较高');
    }
    
    return {
      level: riskScore < 3 ? 'LOW' : riskScore < 6 ? 'MODERATE' : 'HIGH',
      score: riskScore,
      factors: factors,
      exposure: this.calculateExposure(player)
    };
  }
};
```

#### 2.4 特殊功能区 (2格)

**格子1 - 起始点**
```javascript
const startingPoint = {
  id: 1,
  type: 'SPECIAL',
  name: '起始点', 
  icon: '🏠',
  
  // 经过起始点的奖励
  passBonus: {
    cash: 50,           // 基础现金奖励
    experience: 5,      // 经验奖励
    levelMultiplier: 1.2 // 等级加成
  },
  
  // 停留在起始点的特殊功能
  landingFeatures: {
    REST_AND_RECOVER: '休息恢复，获得额外奖励',
    STRATEGY_REVIEW: '回顾投资策略，重新规划',
    MARKET_BRIEFING: '获得市场简报和趋势分析',
    SIGNALPLUS_WELCOME: 'SignalPlus新手指导'
  },
  
  onPass: function(player) {
    const bonus = Math.floor(this.passBonus.cash * (1 + (player.level - 1) * 0.2));
    const expGain = this.passBonus.experience + player.level;
    
    player.cash += bonus;
    player.experience += expGain;
    
    return {
      type: 'PASS_BONUS',
      title: '🏠 经过起始点',
      message: `获得薪资奖励 $${bonus} 和经验 ${expGain}！`,
      animation: 'cash_rain',
      sound: 'bonus_sound'
    };
  },
  
  onLand: function(player) {
    return {
      type: 'STARTING_POINT_MENU',
      title: '🏠 投资者之家',
      subtitle: '在这里休息整顿，规划下一步投资策略',
      
      options: [
        {
          text: '📊 查看投资报告',
          cost: 0,
          action: () => this.generateInvestmentReport(player),
          description: '全面分析当前投资表现'
        },
        {
          text: '🎯 制定投资计划',
          cost: 20,
          action: () => this.createInvestmentPlan(player),
          description: '基于市场情况调整投资策略'
        },
        {
          text: '📚 SignalPlus学习',
          cost: 0,
          action: () => this.openLearningHub(),
          description: '访问SignalPlus教育资源'
        },
        {
          text: '💤 休息一回合',
          cost: 0,
          action: () => this.takeRest(player),
          description: '跳过下次投掷，获得额外现金$30'
        },
        {
          text: '继续游戏',
          cost: 0,
          action: () => ({ message: '精力充沛，继续投资之旅！' })
        }
      ],
      
      welcomeMessage: player.roundsPlayed === 0 ? 
        '🎉 欢迎来到加密期权大富翁！在SignalPlus的支持下，开启您的投资学习之旅。' : 
        `👋 欢迎回家！这是您的第${Math.floor(player.roundsPlayed / 12) + 1}次回到起始点。`
    };
  }
};
```

**格子10 - 奖励池**
```javascript
const rewardPool = {
  id: 10,
  type: 'SPECIAL',
  name: '奖励池',
  icon: '🎁',
  
  // 奖励类型
  rewardTypes: {
    CASH_PRIZE: {
      weight: 0.4,
      amounts: [50, 100, 200, 500],
      probabilities: [0.4, 0.3, 0.2, 0.1]
    },
    
    EXPERIENCE_BOOST: {
      weight: 0.25,
      amounts: [20, 50, 100],
      probabilities: [0.5, 0.3, 0.2]
    },
    
    LEARNING_VOUCHER: {
      weight: 0.2,
      types: ['SignalPlus VIP试用', '投资顾问券', '风险对冲券'],
      values: [100, 50, 75]
    },
    
    ASSET_BONUS: {
      weight: 0.1,
      multipliers: [1.05, 1.1, 1.15],
      durations: [3, 2, 1] // 回合数
    },
    
    MYSTERY_BOX: {
      weight: 0.05,
      contents: 'RANDOM' // 完全随机奖励
    }
  },
  
  onLand: function(player) {
    const reward = this.generateReward();
    
    return {
      type: 'REWARD_EVENT',
      title: '🎁 恭喜中奖！',
      description: '您触发了奖励池机制，可以选择领取奖励或进行挑战获得更大奖励',
      
      guaranteedReward: reward.guaranteed,
      
      options: [
        {
          text: '直接领取奖励',
          cost: 0,
          action: () => this.claimReward(player, reward.guaranteed),
          guaranteed: true,
          result: this.describeReward(reward.guaranteed)
        },
        {
          text: '🎲 挑战双倍奖励',
          cost: 0,
          action: () => this.challengeDoubleReward(player, reward),
          risk: '50%概率获得双倍奖励，50%概率奖励减半',
          potential: this.describeReward(this.doubleReward(reward.guaranteed))
        },
        {
          text: '🧠 知识问答挑战',
          cost: 0,
          action: () => this.knowledgeChallenge(player, reward),
          description: '答对问题获得额外经验奖励',
          educational: true
        }
      ],
      
      animation: 'treasure_chest',
      celebration: true
    };
  },
  
  generateReward: function() {
    const rewardType = this.selectRewardType();
    
    switch (rewardType) {
      case 'CASH_PRIZE':
        const amount = this.selectFromProbability(
          this.rewardTypes.CASH_PRIZE.amounts,
          this.rewardTypes.CASH_PRIZE.probabilities
        );
        return {
          guaranteed: { type: 'CASH', amount: amount },
          description: `现金奖励 $${amount}`
        };
        
      case 'EXPERIENCE_BOOST':
        const exp = this.selectFromProbability(
          this.rewardTypes.EXPERIENCE_BOOST.amounts,
          this.rewardTypes.EXPERIENCE_BOOST.probabilities
        );
        return {
          guaranteed: { type: 'EXPERIENCE', amount: exp },
          description: `经验奖励 ${exp}点`
        };
        
      case 'LEARNING_VOUCHER':
        const voucher = Math.floor(Math.random() * this.rewardTypes.LEARNING_VOUCHER.types.length);
        return {
          guaranteed: { 
            type: 'VOUCHER', 
            name: this.rewardTypes.LEARNING_VOUCHER.types[voucher],
            value: this.rewardTypes.LEARNING_VOUCHER.values[voucher]
          },
          description: `学习券：${this.rewardTypes.LEARNING_VOUCHER.types[voucher]}`
        };
        
      case 'ASSET_BONUS':
        const multiplier = this.rewardTypes.ASSET_BONUS.multipliers[
          Math.floor(Math.random() * this.rewardTypes.ASSET_BONUS.multipliers.length)
        ];
        return {
          guaranteed: { 
            type: 'ASSET_BONUS', 
            multiplier: multiplier,
            duration: 3
          },
          description: `资产收益加成 ${((multiplier - 1) * 100).toFixed(0)}%，持续3回合`
        };
        
      case 'MYSTERY_BOX':
        return this.generateMysteryReward();
    }
  },
  
  knowledgeChallenge: function(player, reward) {
    const questions = [
      {
        question: '什么是期权的内在价值？',
        options: [
          '期权的市场价格',
          '标的资产价格与执行价格的差额',
          '期权的时间价值',
          '期权的波动率'
        ],
        correct: 1,
        explanation: '内在价值是标的资产当前价格与期权执行价格之间的差额（对于看涨期权）'
      },
      {
        question: 'DeFi中的"无常损失"是指什么？',
        options: [
          '智能合约被黑客攻击的损失',
          '提供流动性时因价格变化导致的机会成本',
          '交易手续费的损失',
          '网络拥堵造成的损失'
        ],
        correct: 1,
        explanation: '无常损失是指在AMM中提供流动性时，由于价格变化导致的相对于单纯持有资产的损失'
      }
    ];
    
    const question = questions[Math.floor(Math.random() * questions.length)];
    
    return {
      type: 'KNOWLEDGE_QUIZ',
      question: question.question,
      options: question.options,
      onAnswer: (selectedIndex) => {
        if (selectedIndex === question.correct) {
          // 答对了，获得奖励 + 额外经验
          const baseReward = this.claimReward(player, reward.guaranteed);
          const bonusExp = 50;
          player.experience += bonusExp;
          
          return {
            success: true,
            message: '🎉 答对了！' + question.explanation,
            reward: baseReward + `，额外获得${bonusExp}经验！`
          };
        } else {
          // 答错了，获得基础奖励
          const baseReward = this.claimReward(player, reward.guaranteed);
          return {
            success: false,
            message: '答错了，正确答案是：' + question.explanation,
            reward: baseReward,
            encouragement: '继续学习，下次一定能答对！'
          };
        }
      }
    };
  }
};
```

### 3. 中央信息面板设计

```javascript
const centralInfoPanel = {
  position: { gridColumn: '2 / 4', gridRow: '2 / 3' },
  
  displayComponents: {
    GAME_STATUS: {
      roundNumber: 'current',
      playerPosition: 'animated',
      diceResult: 'with_animation',
      nextAction: 'clear_instruction'
    },
    
    MARKET_OVERVIEW: {
      btcPrice: 'real_time_simulation',
      ethPrice: 'real_time_simulation', 
      volatilityIndex: 'color_coded',
      trendIndicator: 'arrow_with_percentage'
    },
    
    QUICK_STATS: {
      totalValue: 'prominent_display',
      roundPnL: 'color_coded',
      levelProgress: 'progress_bar',
      achievementHints: 'rotating_tips'
    }
  },
  
  render: function(gameState) {
    return `
      <div class="central-panel">
        <div class="panel-header">
          <h3>第 ${gameState.roundNumber} 回合</h3>
          <div class="player-level">Lv.${gameState.player.level}</div>
        </div>
        
        <div class="dice-area">
          <div class="dice-container">
            <div class="dice ${gameState.isRolling ? 'rolling' : ''}">${gameState.dice[0]}</div>
            <div class="dice ${gameState.isRolling ? 'rolling' : ''}">${gameState.dice[1]}</div>
          </div>
          <div class="dice-sum">总点数: ${gameState.dice[0] + gameState.dice[1]}</div>
        </div>
        
        <div class="market-summary">
          <div class="market-item">
            <span class="label">BTC</span>
            <span class="price">${gameState.market.btcPrice.toLocaleString()}</span>
          </div>
          <div class="market-item">
            <span class="label">ETH</span>
            <span class="price">${gameState.market.ethPrice.toLocaleString()}</span>
          </div>
          <div class="volatility-indicator">
            <span class="label">波动率</span>
            <span class="value ${this.getVolatilityClass(gameState.market.volatility)}">
              ${(gameState.market.volatility * 100).toFixed(1)}%
            </span>
          </div>
        </div>
        
        <div class="signalplus-branding">
          <img src="./assets/signalplus-mini-logo.svg" alt="SignalPlus">
          <span>专业数据支持</span>
        </div>
      </div>
    `;
  }
};
```

## Tests

### 棋盘测试用例

#### T1: 12格布局测试
```javascript
describe('SimplifiedBoard Layout', () => {
  test('棋盘创建正确的12个格子', () => {
    const board = new SimplifiedBoard();
    expect(board.spaces.length).toBe(12);
    
    // 验证格子类型分布
    const assetSpaces = board.spaces.filter(s => s.type === 'INVESTMENT_ASSET');
    const eventSpaces = board.spaces.filter(s => s.type === 'MARKET_EVENT');
    const decisionSpaces = board.spaces.filter(s => s.type === 'STRATEGY_DECISION');
    const specialSpaces = board.spaces.filter(s => s.type === 'SPECIAL');
    
    expect(assetSpaces.length).toBe(4);
    expect(eventSpaces.length).toBe(4);
    expect(decisionSpaces.length).toBe(2);
    expect(specialSpaces.length).toBe(2);
  });
  
  test('玩家移动逻辑正确', () => {
    const board = new SimplifiedBoard();
    let position = 0;
    
    // 测试正常移动
    position = board.movePlayer(position, 3);
    expect(position).toBe(3);
    
    // 测试越界循环
    position = board.movePlayer(10, 5);
    expect(position).toBe(3); // (10 + 5) % 12 = 3
  });
});
```

#### T2: 格子事件测试
```javascript
describe('Space Events', () => {
  test('BTC矿场购买逻辑', () => {
    const btcSpace = new BTCMiningFarm();
    const player = createTestPlayer({ cash: 300 });
    
    const result = btcSpace.onLand(player);
    
    expect(result.type).toBe('DECISION');
    expect(result.options.length).toBeGreaterThan(1);
    expect(result.options[0].enabled).toBe(true); // 现金充足，可以购买
  });
  
  test('市场事件概率分布', () => {
    const marketSpace = new MarketOpportunity();
    const results = [];
    
    // 运行1000次模拟
    for (let i = 0; i < 1000; i++) {
      const event = marketSpace.selectRandomEvent();
      results.push(event.id);
    }
    
    // 验证概率分布大致正确
    const bullRunCount = results.filter(id => id === 'bull_run').length;
    expect(bullRunCount).toBeGreaterThan(200); // 约25%概率
    expect(bullRunCount).toBeLessThan(300);
  });
});
```

#### T3: 教育内容测试
```javascript
describe('Educational Content', () => {
  test('每个格子都有学习要点', () => {
    const allSpaces = [
      new BTCMiningFarm(),
      new ETHDeFiProtocol(), 
      new BluechipETF(),
      new SignalPlusShares()
    ];
    
    allSpaces.forEach(space => {
      expect(space.learningPoints).toBeDefined();
      expect(space.learningPoints.length).toBeGreaterThan(0);
      expect(space.learningPoints[0]).toMatch(/[\u4e00-\u9fff]/); // 包含中文
    });
  });
  
  test('SignalPlus集成链接有效', () => {
    const spaces = getAllSpaces();
    const signalPlusLinks = spaces
      .filter(space => space.signalPlusLink)
      .map(space => space.signalPlusLink);
      
    signalPlusLinks.forEach(link => {
      expect(link).toMatch(/^https:\/\/signalplus\.com/);
    });
  });
});
```

### 游戏平衡测试

#### B1: 经济平衡测试
```javascript
describe('Game Economy Balance', () => {
  test('游戏不会过快结束', () => {
    const simulation = new GameSimulation();
    const results = [];
    
    // 运行100场游戏模拟
    for (let i = 0; i < 100; i++) {
      const gameLength = simulation.playToEnd();
      results.push(gameLength);
    }
    
    const averageLength = results.reduce((a, b) => a + b) / results.length;
    expect(averageLength).toBeGreaterThan(20); // 平均至少20回合
    expect(averageLength).toBeLessThan(60);    // 平均不超过60回合
  });
  
  test('破产率合理', () => {
    const simulation = new GameSimulation();
    let bankruptcies = 0;
    
    for (let i = 0; i < 100; i++) {
      const result = simulation.playToEnd();
      if (result.endReason === 'BANKRUPTCY') {
        bankruptcies++;
      }
    }
    
    const bankruptcyRate = bankruptcies / 100;
    expect(bankruptcyRate).toBeLessThan(0.2); // 破产率小于20%
  });
});
```

### 响应式设计测试

#### R1: 多设备适配测试
```css
/* 测试不同屏幕尺寸下的布局 */
@media (max-width: 768px) {
  .game-board {
    width: 100vw;
    height: 60vh;
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: repeat(3, 1fr);
    gap: 4px;
    padding: 10px;
  }
  
  .board-space {
    min-height: 80px;
    padding: 8px;
    font-size: 12px;
  }
  
  .central-panel {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .game-board {
    height: 50vh;
  }
  
  .board-space {
    min-height: 60px;
    padding: 6px;
    font-size: 10px;
  }
}
```