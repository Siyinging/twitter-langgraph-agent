# 期权策略计算引擎设计

## 核心计算架构

### 1. 期权定价模型

```typescript
// src/core/optionPricing.ts

export interface OptionParameters {
  spotPrice: number        // 标的价格
  strikePrice: number     // 行权价
  timeToExpiry: number    // 到期时间(天数)
  riskFreeRate: number    // 无风险利率
  volatility: number      // 隐含波动率
  dividendYield: number   // 股息率
}

export class BlackScholesCalculator {
  /**
   * Black-Scholes期权定价公式
   */
  static calculateCallPrice(params: OptionParameters): number {
    const { spotPrice, strikePrice, timeToExpiry, riskFreeRate, volatility } = params
    const T = timeToExpiry / 365
    
    const d1 = (Math.log(spotPrice / strikePrice) + (riskFreeRate + 0.5 * volatility ** 2) * T) 
               / (volatility * Math.sqrt(T))
    const d2 = d1 - volatility * Math.sqrt(T)
    
    const callPrice = spotPrice * this.normalCDF(d1) 
                      - strikePrice * Math.exp(-riskFreeRate * T) * this.normalCDF(d2)
    
    return Math.max(0, callPrice)
  }

  static calculatePutPrice(params: OptionParameters): number {
    const callPrice = this.calculateCallPrice(params)
    const { spotPrice, strikePrice, timeToExpiry, riskFreeRate } = params
    const T = timeToExpiry / 365
    
    // Put-Call Parity: Put = Call - S + K*e^(-r*T)
    return callPrice - spotPrice + strikePrice * Math.exp(-riskFreeRate * T)
  }

  private static normalCDF(x: number): number {
    return 0.5 * (1 + this.erf(x / Math.sqrt(2)))
  }

  private static erf(x: number): number {
    // Abramowitz and Stegun approximation
    const a1 =  0.254829592
    const a2 = -0.284496736
    const a3 =  1.421413741
    const a4 = -1.453152027
    const a5 =  1.061405429
    const p  =  0.3275911

    const sign = Math.sign(x)
    x = Math.abs(x)

    const t = 1.0 / (1.0 + p * x)
    const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x)

    return sign * y
  }
}
```

### 2. 期权策略定义系统

```typescript
// src/types/optionStrategy.ts

export interface OptionLeg {
  type: 'call' | 'put'
  action: 'buy' | 'sell'
  strike: number
  quantity: number
  expiry: Date
  premium?: number  // 如果未提供则计算
}

export interface StrategyDefinition {
  id: string
  name: string
  displayName: string
  description: string
  category: 'basic' | 'spread' | 'combination' | 'advanced'
  legs: OptionLeg[]
  
  // 策略特性
  maxProfit: number | 'unlimited'
  maxLoss: number | 'unlimited' 
  breakevens: number[]
  
  // 市场观点
  marketView: 'bullish' | 'bearish' | 'neutral' | 'volatile' | 'stable'
  riskLevel: 1 | 2 | 3 | 4 | 5  // 1=低风险, 5=高风险
  
  // 教学信息
  teachingNotes: string
  whenToUse: string[]
  prosAndCons: {
    pros: string[]
    cons: string[]
  }
}

// 预定义策略模板
export const STRATEGY_TEMPLATES: Record<string, StrategyDefinition> = {
  longCall: {
    id: 'long-call',
    name: 'longCall',
    displayName: '买入看涨期权',
    description: '买入看涨期权，适合看涨市场',
    category: 'basic',
    legs: [
      { type: 'call', action: 'buy', strike: 50000, quantity: 1, expiry: new Date() }
    ],
    maxProfit: 'unlimited',
    maxLoss: -500,  // 期权费
    breakevens: [50500],
    marketView: 'bullish',
    riskLevel: 2,
    teachingNotes: '最基础的看涨策略，风险有限，潜在收益无限',
    whenToUse: ['预期标的价格大幅上涨', '波动率较低时买入'],
    prosAndCons: {
      pros: ['风险有限', '潜在收益无限', '策略简单'],
      cons: ['时间衰减', '需要明显价格变动']
    }
  },
  
  longPut: {
    id: 'long-put',
    name: 'longPut', 
    displayName: '买入看跌期权',
    description: '买入看跌期权，适合看跌市场',
    category: 'basic',
    legs: [
      { type: 'put', action: 'buy', strike: 50000, quantity: 1, expiry: new Date() }
    ],
    maxProfit: 49500,  // 行权价减去期权费
    maxLoss: -500,
    breakevens: [49500],
    marketView: 'bearish',
    riskLevel: 2,
    teachingNotes: '基础看跌策略，适合下跌行情',
    whenToUse: ['预期标的价格下跌', '作为对冲工具'],
    prosAndCons: {
      pros: ['风险有限', '下跌保护', '策略简单'],
      cons: ['时间衰减', '需要价格下跌']
    }
  },

  bullSpread: {
    id: 'bull-spread',
    name: 'bullSpread',
    displayName: '牛市价差',
    description: '买入低行权价看涨期权，卖出高行权价看涨期权',
    category: 'spread',
    legs: [
      { type: 'call', action: 'buy', strike: 48000, quantity: 1, expiry: new Date() },
      { type: 'call', action: 'sell', strike: 52000, quantity: 1, expiry: new Date() }
    ],
    maxProfit: 3700,  // 价差-净期权费
    maxLoss: -300,
    breakevens: [48300],
    marketView: 'bullish',
    riskLevel: 2,
    teachingNotes: '温和看涨策略，收益和风险都有限',
    whenToUse: ['适度看涨', '降低期权费成本'],
    prosAndCons: {
      pros: ['成本较低', '风险有限', '时间衰减影响小'],
      cons: ['收益有限', '需要价格在区间内']
    }
  },

  straddle: {
    id: 'straddle',
    name: 'straddle',
    displayName: '跨式组合',
    description: '同时买入相同行权价的看涨和看跌期权',
    category: 'combination',
    legs: [
      { type: 'call', action: 'buy', strike: 50000, quantity: 1, expiry: new Date() },
      { type: 'put', action: 'buy', strike: 50000, quantity: 1, expiry: new Date() }
    ],
    maxProfit: 'unlimited',
    maxLoss: -1000,  // 总期权费
    breakevens: [49000, 51000],
    marketView: 'volatile',
    riskLevel: 3,
    teachingNotes: '适合预期大幅波动但方向不确定的情况',
    whenToUse: ['预期重大消息发布', '波动率低时建立'],
    prosAndCons: {
      pros: ['双向获利机会', '适合震荡市场'],
      cons: ['成本较高', '需要大幅价格变动']
    }
  },

  butterfly: {
    id: 'butterfly',
    name: 'butterfly',
    displayName: '蝶式价差',
    description: '买入1份低行权价+1份高行权价看涨，卖出2份中间行权价看涨',
    category: 'advanced',
    legs: [
      { type: 'call', action: 'buy', strike: 48000, quantity: 1, expiry: new Date() },
      { type: 'call', action: 'sell', strike: 50000, quantity: 2, expiry: new Date() },
      { type: 'call', action: 'buy', strike: 52000, quantity: 1, expiry: new Date() }
    ],
    maxProfit: 1800,
    maxLoss: -200,
    breakevens: [48200, 51800],
    marketView: 'stable',
    riskLevel: 3,
    teachingNotes: '适合预期价格在特定区间内波动的情况',
    whenToUse: ['预期低波动', '价格在目标区间'],
    prosAndCons: {
      pros: ['风险有限', '适合横盘市场'],
      cons: ['收益有限', '需要精确判断']
    }
  },

  ironCondor: {
    id: 'iron-condor',
    name: 'ironCondor',
    displayName: '铁鹰价差',
    description: '卖出中间两个行权价的期权，买入外侧保护期权',
    category: 'advanced',
    legs: [
      { type: 'put', action: 'buy', strike: 46000, quantity: 1, expiry: new Date() },
      { type: 'put', action: 'sell', strike: 48000, quantity: 1, expiry: new Date() },
      { type: 'call', action: 'sell', strike: 52000, quantity: 1, expiry: new Date() },
      { type: 'call', action: 'buy', strike: 54000, quantity: 1, expiry: new Date() }
    ],
    maxProfit: 800,   // 净权利金收入
    maxLoss: -1200,   // 最大价差-净收入
    breakevens: [47200, 52800],
    marketView: 'stable',
    riskLevel: 3,
    teachingNotes: '获取时间价值的策略，适合盘整市场',
    whenToUse: ['预期低波动', '获取时间价值'],
    prosAndCons: {
      pros: ['收取权利金', '适合震荡市场'],
      cons: ['收益有限', '需要价格稳定']
    }
  }
}
```

### 3. 策略盈亏计算引擎

```typescript
// src/core/strategyCalculator.ts

export interface MarketCondition {
  currentPrice: number
  targetPrice: number
  priceChange: number
  volatilityChange: number
  timeElapsed: number  // 经过的天数
}

export class StrategyCalculator {
  constructor(private pricingModel: BlackScholesCalculator) {}

  /**
   * 计算策略在特定市场条件下的盈亏
   */
  calculateStrategyPnL(
    strategy: StrategyDefinition,
    market: MarketCondition,
    baseParameters: Partial<OptionParameters>
  ): StrategyResult {
    
    let totalPnL = 0
    const legResults: LegResult[] = []

    for (const leg of strategy.legs) {
      const legPnL = this.calculateLegPnL(leg, market, baseParameters)
      totalPnL += legPnL.pnl
      legResults.push(legPnL)
    }

    return {
      totalPnL,
      legResults,
      isProfit: totalPnL > 0,
      profitPercentage: this.calculateProfitPercentage(totalPnL, strategy),
      explanation: this.generateExplanation(strategy, market, totalPnL),
      teachingPoints: this.getTeachingPoints(strategy, market, totalPnL)
    }
  }

  private calculateLegPnL(
    leg: OptionLeg,
    market: MarketCondition,
    baseParams: Partial<OptionParameters>
  ): LegResult {
    
    const optionParams: OptionParameters = {
      spotPrice: market.targetPrice,
      strikePrice: leg.strike,
      timeToExpiry: Math.max(1, (baseParams.timeToExpiry || 7) - market.timeElapsed),
      riskFreeRate: baseParams.riskFreeRate || 0.05,
      volatility: (baseParams.volatility || 0.8) * (1 + market.volatilityChange),
      dividendYield: baseParams.dividendYield || 0
    }

    // 计算期权当前价值
    const currentValue = leg.type === 'call' 
      ? BlackScholesCalculator.calculateCallPrice(optionParams)
      : BlackScholesCalculator.calculatePutPrice(optionParams)

    // 计算初始期权费（建仓时的价格）
    const initialParams = {
      ...optionParams,
      spotPrice: market.currentPrice,
      timeToExpiry: baseParams.timeToExpiry || 7,
      volatility: baseParams.volatility || 0.8
    }

    const initialPremium = leg.premium || (
      leg.type === 'call' 
        ? BlackScholesCalculator.calculateCallPrice(initialParams)
        : BlackScholesCalculator.calculatePutPrice(initialParams)
    )

    // 计算盈亏
    const valueDifference = currentValue - initialPremium
    const pnl = leg.action === 'buy' 
      ? valueDifference * leg.quantity
      : -valueDifference * leg.quantity

    return {
      legId: `${leg.type}-${leg.action}-${leg.strike}`,
      initialPremium,
      currentValue,
      pnl,
      description: this.describeLegResult(leg, pnl)
    }
  }

  /**
   * 为教学目的生成策略解释
   */
  private generateExplanation(
    strategy: StrategyDefinition,
    market: MarketCondition,
    totalPnL: number
  ): string {
    const priceDirection = market.targetPrice > market.currentPrice ? '上涨' : '下跌'
    const priceChangePercent = Math.abs(market.priceChange * 100).toFixed(1)
    
    let explanation = `在当前市场条件下：\n`
    explanation += `• 价格${priceDirection} ${priceChangePercent}% (从 $${market.currentPrice.toLocaleString()} 到 $${market.targetPrice.toLocaleString()})\n`
    
    if (totalPnL > 0) {
      explanation += `✅ 使用${strategy.displayName}策略获得盈利 $${totalPnL.toLocaleString()}\n`
      explanation += `这是因为 ${this.explainWhyProfitable(strategy, market)}`
    } else {
      explanation += `❌ 使用${strategy.displayName}策略产生亏损 $${Math.abs(totalPnL).toLocaleString()}\n`
      explanation += `这是因为 ${this.explainWhyUnprofitable(strategy, market)}`
    }

    return explanation
  }

  private explainWhyProfitable(strategy: StrategyDefinition, market: MarketCondition): string {
    const marketDirection = market.targetPrice > market.currentPrice ? 'bullish' : 'bearish'
    
    if (strategy.marketView === marketDirection) {
      return `该策略的市场观点(${strategy.marketView})与实际市场走势一致。`
    } else if (strategy.marketView === 'volatile' && Math.abs(market.priceChange) > 0.05) {
      return `该策略适合高波动市场，而市场确实出现了显著价格变动。`
    } else if (strategy.marketView === 'stable' && Math.abs(market.priceChange) < 0.03) {
      return `该策略适合稳定市场，而价格变动幅度较小符合预期。`
    }
    
    return `市场条件符合该策略的预期情况。`
  }

  private explainWhyUnprofitable(strategy: StrategyDefinition, market: MarketCondition): string {
    const marketDirection = market.targetPrice > market.currentPrice ? 'bullish' : 'bearish'
    
    if (strategy.marketView === 'bullish' && marketDirection === 'bearish') {
      return `该策略适合上涨市场，但实际价格下跌了。`
    } else if (strategy.marketView === 'bearish' && marketDirection === 'bullish') {
      return `该策略适合下跌市场，但实际价格上涨了。`
    } else if (strategy.marketView === 'volatile' && Math.abs(market.priceChange) < 0.02) {
      return `该策略需要大幅价格变动，但市场波动不够大。`
    } else if (strategy.marketView === 'stable' && Math.abs(market.priceChange) > 0.05) {
      return `该策略适合稳定市场，但价格出现了较大波动。`
    }
    
    return `市场条件不符合该策略的预期。`
  }

  /**
   * 生成教学要点
   */
  private getTeachingPoints(
    strategy: StrategyDefinition,
    market: MarketCondition,
    totalPnL: number
  ): string[] {
    const points: string[] = []
    
    // 基于策略类型的教学点
    points.push(`${strategy.displayName}是${strategy.category === 'basic' ? '基础' : '高级'}策略`)
    
    if (strategy.riskLevel <= 2) {
      points.push('这是相对低风险的策略，适合初学者')
    } else if (strategy.riskLevel >= 4) {
      points.push('这是高风险策略，需要丰富的交易经验')
    }

    // 基于结果的教学点
    if (totalPnL > 0) {
      points.push('选择了适合当前市场条件的策略，体现了良好的市场判断')
    } else {
      points.push('这次的策略选择提供了宝贵的学习机会，帮助理解不同市场条件下的策略效果')
    }

    // 策略特定的学习点
    points.push(...this.getStrategySpecificTeaching(strategy))

    return points
  }

  private getStrategySpecificTeaching(strategy: StrategyDefinition): string[] {
    switch (strategy.id) {
      case 'long-call':
        return ['看涨期权的时间价值会随时间衰减', '需要价格有明显上涨才能盈利']
      case 'long-put':
        return ['看跌期权可以作为投资组合的保险', '适合在市场不确定时建立']
      case 'bull-spread':
        return ['价差策略可以降低期权费成本', '收益被限制在价差范围内']
      case 'straddle':
        return ['跨式组合适合重大事件前建立', '需要足够大的价格变动来覆盖期权费']
      case 'butterfly':
        return ['蝶式价差在目标价格附近收益最大', '适合预期横盘整理的市场']
      case 'iron-condor':
        return ['铁鹰策略通过卖出期权收取时间价值', '需要价格在预设区间内波动']
      default:
        return ['每种策略都有其适用的市场环境', '关键是匹配策略与市场预期']
    }
  }
}

// 结果类型定义
export interface StrategyResult {
  totalPnL: number
  legResults: LegResult[]
  isProfit: boolean
  profitPercentage: number
  explanation: string
  teachingPoints: string[]
}

export interface LegResult {
  legId: string
  initialPremium: number
  currentValue: number
  pnl: number
  description: string
}
```

### 4. 游戏集成接口

```typescript
// src/services/gameCalculationService.ts

export class GameCalculationService {
  private calculator: StrategyCalculator

  constructor() {
    this.calculator = new StrategyCalculator(BlackScholesCalculator)
  }

  /**
   * 游戏中的策略选择计算
   */
  async calculateGameChoice(
    strategyId: string,
    marketScenario: MarketScenario,
    currentPrice: number = 50000
  ): Promise<GameStrategyResult> {
    
    const strategy = STRATEGY_TEMPLATES[strategyId]
    if (!strategy) {
      throw new Error(`未找到策略: ${strategyId}`)
    }

    // 构建市场条件
    const marketCondition: MarketCondition = {
      currentPrice,
      targetPrice: currentPrice * (1 + marketScenario.priceChange),
      priceChange: marketScenario.priceChange,
      volatilityChange: marketScenario.volatilityChange,
      timeElapsed: marketScenario.timeToExpiry
    }

    // 计算结果
    const result = this.calculator.calculateStrategyPnL(
      strategy,
      marketCondition,
      {
        volatility: 0.8,
        riskFreeRate: 0.05,
        timeToExpiry: 7,
        dividendYield: 0
      }
    )

    // 游戏化结果处理
    return {
      profit: Math.round(result.totalPnL),
      isOptimal: this.isOptimalChoice(strategyId, marketScenario),
      explanation: result.explanation,
      teachingPoints: result.teachingPoints,
      alternativeStrategies: this.getAlternativeAnalysis(marketScenario),
      scoreBonus: this.calculateScoreBonus(result.totalPnL, strategy.riskLevel)
    }
  }

  private isOptimalChoice(strategyId: string, scenario: MarketScenario): boolean {
    return scenario.recommendedStrategy.includes(strategyId)
  }

  private getAlternativeAnalysis(scenario: MarketScenario): AlternativeStrategy[] {
    return scenario.recommendedStrategy.map(strategyId => {
      const strategy = STRATEGY_TEMPLATES[strategyId]
      return {
        strategyId,
        name: strategy.displayName,
        reason: `适合${this.getMarketDescription(scenario)}的策略`
      }
    })
  }

  private getMarketDescription(scenario: MarketScenario): string {
    if (scenario.priceChange > 0.05) return '强烈看涨'
    if (scenario.priceChange < -0.05) return '强烈看跌'
    if (Math.abs(scenario.priceChange) < 0.02) return '盘整横盘'
    return scenario.priceChange > 0 ? '温和看涨' : '温和看跌'
  }

  private calculateScoreBonus(pnl: number, riskLevel: number): number {
    // 基础分数
    let bonus = Math.max(0, pnl / 10)
    
    // 风险调整
    if (riskLevel >= 4 && pnl > 0) {
      bonus *= 1.5  // 高风险策略成功给予加分
    }
    
    return Math.round(bonus)
  }
}

export interface GameStrategyResult {
  profit: number
  isOptimal: boolean
  explanation: string
  teachingPoints: string[]
  alternativeStrategies: AlternativeStrategy[]
  scoreBonus: number
}

export interface AlternativeStrategy {
  strategyId: string
  name: string
  reason: string
}
```

### 5. 测试用例设计

```typescript
// src/core/__tests__/strategyCalculator.test.ts

describe('StrategyCalculator', () => {
  let calculator: StrategyCalculator
  
  beforeEach(() => {
    calculator = new StrategyCalculator(BlackScholesCalculator)
  })

  describe('Long Call Strategy', () => {
    it('should calculate profit when price rises above breakeven', () => {
      const market: MarketCondition = {
        currentPrice: 50000,
        targetPrice: 52000,  // 4% 上涨
        priceChange: 0.04,
        volatilityChange: 0,
        timeElapsed: 3
      }
      
      const result = calculator.calculateStrategyPnL(
        STRATEGY_TEMPLATES.longCall,
        market,
        { volatility: 0.8, riskFreeRate: 0.05, timeToExpiry: 7 }
      )
      
      expect(result.isProfit).toBe(true)
      expect(result.totalPnL).toBeGreaterThan(0)
    })
    
    it('should calculate loss when price stays flat', () => {
      const market: MarketCondition = {
        currentPrice: 50000,
        targetPrice: 50000,  // 无变化
        priceChange: 0,
        volatilityChange: 0,
        timeElapsed: 6  // 时间衰减
      }
      
      const result = calculator.calculateStrategyPnL(
        STRATEGY_TEMPLATES.longCall,
        market,
        { volatility: 0.8, riskFreeRate: 0.05, timeToExpiry: 7 }
      )
      
      expect(result.isProfit).toBe(false)
      expect(result.totalPnL).toBeLessThan(0)
    })
  })

  describe('Butterfly Strategy', () => {
    it('should maximize profit at center strike', () => {
      const market: MarketCondition = {
        currentPrice: 49000,
        targetPrice: 50000,  // 到达中间行权价
        priceChange: 0.02,
        volatilityChange: -0.2,  // 波动率下降
        timeElapsed: 5
      }
      
      const result = calculator.calculateStrategyPnL(
        STRATEGY_TEMPLATES.butterfly,
        market,
        { volatility: 0.8, riskFreeRate: 0.05, timeToExpiry: 7 }
      )
      
      expect(result.isProfit).toBe(true)
      // 在中心行权价附近应该盈利最大
    })
  })
})
```

这个期权策略计算引擎设计提供了：

1. **准确的期权定价**：基于Black-Scholes模型
2. **完整的策略支持**：覆盖6种核心期权策略
3. **教学功能集成**：详细解释和学习要点
4. **游戏化适配**：适合大富翁游戏的结果格式
5. **可扩展架构**：便于添加新策略和功能
6. **全面的测试**：确保计算准确性

现在进行下一个任务：制定开发阶段和里程碑计划。