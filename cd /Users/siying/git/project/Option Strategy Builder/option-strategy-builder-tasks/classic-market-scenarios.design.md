# 加密市场经典行情游戏设计

## 9格游戏棋盘设计

### 棋盘布局（顺时针方向）
```
[8] 2024牛市回调    [0] 起点          [1] 2021牛市狂欢
    (-25%)        (开始游戏)         (+300%)

[7] 2022熊市深跌    [中心] 策略帮助    [2] 2022年初震荡  
    (-75%)         SignalPlus       (+/-15%)

[6] DeFi Summer     [5] 疫情暴跌       [4] 2023年复苏
    (+400%)         (-50%)           (+120%)

[3] 中本聪愿景
    (长期持有奖励)
```

## 历年经典市场场景

### 格子0：起点 - 踏入加密世界
**场景描述**：欢迎来到加密期权交易世界！
- **时间背景**：2024年现在
- **市场状态**：BTC $43,000，准备开始你的期权学习之旅
- **教学重点**：期权基础知识介绍
- **奖励**：获得 $10,000 初始资金

### 格子1：2021牛市狂欢 - 散户FOMO
**历史背景**：2021年1-11月，BTC从$29k涨到$69k
- **价格变动**：+300% 
- **市场特征**：机构入场，散户FOMO，"数字黄金"概念爆发
- **波动率**：极高波动，日内±10%常见
- **推荐策略**：Long Call, Bull Call Spread, Covered Call
- **教学重点**：牛市中如何控制贪婪，何时获利了结

### 格子2：2022年初震荡 - 美联储转鹰
**历史背景**：2022年1-3月，美联储加息预期，BTC $35k-$47k震荡
- **价格变动**：±15%区间震荡
- **市场特征**：宏观不确定性增加，资金流动性收紧
- **波动率**：高波动率，但方向不明
- **推荐策略**：Straddle, Iron Condor, Butterfly
- **教学重点**：横盘市场中的波动率策略

### 格子3：中本聪愿景 - 长期主义
**特殊格子**：教育内容格
- **概念教学**：比特币的长期价值主张
- **策略教学**：什么是HODL，什么时候适合用期权保护持仓
- **奖励机制**：选择正确答案获得知识加成
- **推荐策略**：Protective Put, Covered Call
- **教学重点**：长期投资vs短期交易的期权应用

### 格子4：2023年复苏 - 银行业危机后的反弹
**历史背景**：2023年3-12月，硅谷银行事件后BTC重新受到关注
- **价格变动**：+120%（从$20k到$44k）
- **市场特征**：传统金融不稳定，比特币避险属性显现
- **波动率**：中等波动，稳步上涨
- **推荐策略**：Bull Call Spread, Long Call, Call Ratio Spread
- **教学重点**：温和牛市中的价差策略优势

### 格子5：疫情暴跌 - 黑天鹅事件
**历史背景**：2020年3月，疫情爆发，BTC从$10k跌到$3.8k
- **价格变动**：-50%
- **市场特征**：流动性危机，所有资产同步下跌
- **波动率**：极高波动率，恐慌性抛售
- **推荐策略**：Long Put, Bear Put Spread, Protective Put
- **教学重点**：危机时期的风险管理和抄底策略

### 格子6：DeFi Summer - 创新泡沫
**历史背景**：2020年6-9月，DeFi协议爆发，带动ETH暴涨
- **价格变动**：+400%（以ETH为例）
- **市场特征**：技术创新推动，新概念层出不穷
- **波动率**：超高波动率，新兴市场特征
- **推荐策略**：Long Call, Call Calendar Spread, 谨慎使用高倍杠杆
- **教学重点**：创新周期中的机会和风险

### 格子7：2022熊市深跌 - Luna/FTX崩盘
**历史背景**：2022年5-11月，Terra生态崩塌，FTX破产
- **价格变动**：-75%（从$47k到$15.5k）
- **市场特征**：信任危机，行业洗牌，"只有潮水退了才知道谁在裸泳"
- **波动率**：高波动率，持续下跌趋势
- **推荐策略**：Long Put, Bear Spread, Protective strategies
- **教学重点**：熊市生存策略，风险管理的重要性

### 格子8：2024牛市回调 - ETF获批后的获利了结
**历史背景**：2024年1-3月，现货ETF获批后的短期回调
- **价格变动**：-25%（从$73k到$50k）
- **市场特征**："利好出尽是利空"，机构获利了结
- **波动率**：中等波动率，技术性调整
- **推荐策略**：Buy the Dip策略，Bull Put Spread
- **教学重点**：如何区分技术调整和趋势反转

## 扩展期权策略库

### 基础策略（4种）
1. **Long Call** - 买入看涨期权
2. **Long Put** - 买入看跌期权  
3. **Short Call** - 卖出看涨期权（需保证金）
4. **Short Put** - 卖出看跌期权（现金担保）

### 价差策略（6种）
5. **Bull Call Spread** - 牛市看涨价差
6. **Bear Put Spread** - 熊市看跌价差
7. **Bull Put Spread** - 牛市看跌价差（收取权利金）
8. **Bear Call Spread** - 熊市看涨价差（收取权利金）
9. **Call Calendar Spread** - 看涨日历价差
10. **Put Calendar Spread** - 看跌日历价差

### 组合策略（6种）
11. **Long Straddle** - 长跨式组合
12. **Short Straddle** - 短跨式组合
13. **Long Strangle** - 长宽跨式组合
14. **Iron Condor** - 铁鹰式组合
15. **Butterfly Spread** - 蝶式价差
16. **Iron Butterfly** - 铁蝶式组合

### 保护策略（4种）
17. **Protective Put** - 保护性看跌期权
18. **Covered Call** - 备兑看涨期权
19. **Collar** - 领口策略
20. **Cash-Secured Put** - 现金担保看跌期权

## 游戏机制设计

### 策略选择系统
```typescript
interface StrategyChoice {
  scenario: MarketScenario
  availableStrategies: Strategy[]  // 根据市场情况筛选
  difficultyLevel: 'beginner' | 'intermediate' | 'advanced'
  timeLimit: number  // 选择时间限制
}

// 示例：2021牛市狂欢场景
const bullMarket2021: StrategyChoice = {
  scenario: MARKET_SCENARIOS.bullRun2021,
  availableStrategies: [
    STRATEGIES.longCall,
    STRATEGIES.bullCallSpread, 
    STRATEGIES.coveredCall,
    STRATEGIES.shortPut  // 进阶选项
  ],
  difficultyLevel: 'intermediate',
  timeLimit: 30
}
```

### 教育内容分层
```typescript
interface EducationContent {
  basic: string       // 基础解释
  intermediate: string // 进阶分析  
  expert: string      // 专家观点
  historicalContext: string // 历史背景
  lessonsLearned: string[] // 教训总结
}

// 示例：2022熊市教学内容
const bearMarket2022Education: EducationContent = {
  basic: "熊市中，资产价格下跌，看跌期权变得有价值",
  intermediate: "Luna/FTX事件显示了交易对手风险的重要性",
  expert: "系统性风险面前，相关性趋于1，分散投资失效",
  historicalContext: "这是加密史上最严重的信任危机...",
  lessonsLearned: [
    "永远不要把所有资产放在一个平台",
    "理解你投资的项目的基本面",
    "熊市是学习的最佳时期"
  ]
}
```

### 得分和排名系统
```typescript
interface GameScoring {
  strategyAccuracy: number    // 策略选择的准确性
  riskManagement: number      // 风险控制能力
  learningProgress: number    // 学习进度
  historicalKnowledge: number // 历史认知
  totalScore: number
}

// 评分权重
const SCORING_WEIGHTS = {
  profitLoss: 0.4,           // 实际盈亏40%
  strategyOptimality: 0.3,   // 策略最优性30%
  riskAdjusted: 0.2,         // 风险调整后收益20%
  educationBonus: 0.1        // 教育问题加分10%
}
```

这个设计将真实的市场历史与期权教育完美结合，让用户在游戏中体验加密市场的起起落落，学会在不同市场环境下选择合适的期权策略。