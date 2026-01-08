# 扩展期权策略库设计

## 策略分级系统

### 🟢 初级策略 (Level 1) - 5种
**目标用户**：期权新手，刚接触加密市场
**特点**：风险可控，概念简单，易于理解

1. **Long Call (LC)**
   - 中文名：买入看涨期权
   - 适用场景：强烈看涨
   - 最大盈利：无限
   - 最大亏损：期权费
   - 教学重点：期权基础概念，时间价值

2. **Long Put (LP)**
   - 中文名：买入看跌期权
   - 适用场景：强烈看跌
   - 最大盈利：行权价-期权费
   - 最大亏损：期权费
   - 教学重点：看跌期权的保护作用

3. **Covered Call (CC)**
   - 中文名：备兑看涨期权
   - 适用场景：持有现货，中性偏涨
   - 最大盈利：期权费+现货涨幅（到行权价）
   - 最大亏损：现货跌幅-期权费
   - 教学重点：增强收益策略

4. **Cash-Secured Put (CSP)**
   - 中文名：现金担保看跌期权
   - 适用场景：想要低价买入，中性偏涨
   - 最大盈利：期权费
   - 最大亏损：行权价-现货价格-期权费
   - 教学重点：收取权利金策略

5. **Protective Put (PP)**
   - 中文名：保护性看跌期权
   - 适用场景：持有现货，担心下跌
   - 最大盈利：无限-期权费
   - 最大亏损：期权费+现货跌幅（到行权价）
   - 教学重点：风险对冲原理

### 🔵 中级策略 (Level 2) - 8种
**目标用户**：有基础期权知识，了解价差概念
**特点**：收益和风险都有限，策略相对复杂

6. **Bull Call Spread (BCS)**
   - 中文名：牛市看涨价差
   - 组合：买入低行权价Call + 卖出高行权价Call
   - 适用场景：温和看涨
   - 教学重点：价差策略降低成本

7. **Bear Put Spread (BPS)**
   - 中文名：熊市看跌价差
   - 组合：买入高行权价Put + 卖出低行权价Put
   - 适用场景：温和看跌
   - 教学重点：有限风险的看跌策略

8. **Bull Put Spread (BPS2)**
   - 中文名：牛市看跌价差
   - 组合：卖出高行权价Put + 买入低行权价Put
   - 适用场景：中性偏涨，收取权利金
   - 教学重点：卖方策略的优势

9. **Bear Call Spread (BCS2)**
   - 中文名：熊市看涨价差
   - 组合：卖出低行权价Call + 买入高行权价Call
   - 适用场景：中性偏跌，收取权利金
   - 教学重点：限制风险的卖方策略

10. **Long Straddle (LS)**
    - 中文名：买入跨式组合
    - 组合：买入ATM Call + 买入ATM Put
    - 适用场景：预期大幅波动，方向不明
    - 教学重点：波动率策略

11. **Long Strangle (LSt)**
    - 中文名：买入宽跨式组合
    - 组合：买入OTM Call + 买入OTM Put
    - 适用场景：预期大幅波动，成本较低
    - 教学重点：成本优化的波动率策略

12. **Call Calendar Spread (CCS)**
    - 中文名：看涨日历价差
    - 组合：卖出近月Call + 买入远月Call
    - 适用场景：中性市场，时间套利
    - 教学重点：时间价值衰减策略

13. **Put Calendar Spread (PCS)**
    - 中文名：看跌日历价差
    - 组合：卖出近月Put + 买入远月Put
    - 适用场景：中性市场，时间套利
    - 教学重点：时间价值管理

### 🔶 高级策略 (Level 3) - 5种
**目标用户**：经验丰富的期权交易者
**特点**：复杂组合，精确预期，高技术要求

14. **Iron Condor (IC)**
    - 中文名：铁鹰式组合
    - 组合：BCS + BPS (或 BPS2 + BCS2)
    - 适用场景：低波动率，区间震荡
    - 教学重点：收取权利金的区间策略

15. **Butterfly Spread (BS)**
    - 中文名：蝶式价差
    - 组合：1×买入低Call + 2×卖出中间Call + 1×买入高Call
    - 适用场景：预期价格在特定点位
    - 教学重点：精确预测策略

16. **Iron Butterfly (IB)**
    - 中文名：铁蝶式组合
    - 组合：Short Straddle + Protective Wings
    - 适用场景：极低波动率
    - 教学重点：高级收益策略

17. **Short Straddle (SS)**
    - 中文名：卖出跨式组合
    - 组合：卖出ATM Call + 卖出ATM Put
    - 适用场景：低波动率，强烈中性观点
    - 教学重点：高风险高收益策略

18. **Collar (Col)**
    - 中文名：领口策略
    - 组合：持有现货 + Protective Put + Covered Call
    - 适用场景：持有现货，限制涨跌幅
    - 教学重点：风险管理组合

### 🔴 专家策略 (Level 4) - 2种
**目标用户**：专业交易者，深度理解期权
**特点**：复杂执行，动态调整，专业要求极高

19. **Ratio Call Spread (RCS)**
    - 中文名：比例看涨价差
    - 组合：买入1个低行权价Call + 卖出2个高行权价Call
    - 适用场景：温和看涨，但预期涨幅有限
    - 教学重点：非对称风险收益

20. **Ratio Put Spread (RPS)**
    - 中文名：比例看跌价差
    - 组合：买入1个高行权价Put + 卖出2个低行权价Put
    - 适用场景：温和看跌，但预期跌幅有限
    - 教学重点：复杂比例策略

## 策略与历史场景匹配

### 2021牛市狂欢 (+300%)
**推荐策略等级**：Level 1-2
- 🟢 Long Call, Covered Call
- 🔵 Bull Call Spread, Call Calendar Spread
- **错误策略示例**：Long Put, Bear Spread

### 2022熊市深跌 (-75%)  
**推荐策略等级**：Level 1-2
- 🟢 Long Put, Protective Put
- 🔵 Bear Put Spread, Long Straddle
- **错误策略示例**：Long Call, Bull Spread

### 2022年初震荡 (±15%)
**推荐策略等级**：Level 2-3
- 🔵 Long Straddle, Long Strangle
- 🔶 Iron Condor, Butterfly Spread
- **错误策略示例**：单向策略

### DeFi Summer (+400%)
**推荐策略等级**：Level 1-4
- 🟢 Long Call (ETH)
- 🔴 Ratio Call Spread (高风险高收益)
- **教学重点**：创新泡沫的识别

### 疫情暴跌 (-50%)
**推荐策略等级**：Level 1-2
- 🟢 Long Put, Protective Put
- 🔵 Bear Put Spread
- **教学重点**：黑天鹅事件应对

## 游戏中的策略解锁系统

### 解锁条件
- **Level 1**：游戏开始即可使用
- **Level 2**：完成3个Level 1策略
- **Level 3**：完成5个Level 2策略，且平均得分>70分
- **Level 4**：完成所有Level 3策略，且至少1个满分

### 策略提示系统
```typescript
interface StrategyHint {
  level: 1 | 2 | 3 | 4
  scenario: string
  recommended: string[]
  avoid: string[]
  reasoning: string
  riskWarning?: string
}

const hints: Record<string, StrategyHint> = {
  bullRun2021: {
    level: 2,
    scenario: "2021牛市狂欢",
    recommended: ["Long Call", "Bull Call Spread", "Covered Call"],
    avoid: ["Long Put", "Bear Spread"],
    reasoning: "强烈上涨趋势，应选择看涨策略",
    riskWarning: "注意牛市中的贪婪情绪"
  }
}
```

这个扩展的策略库让游戏更具教育价值和挑战性，用户可以从基础策略逐步学习到专家级策略，在真实的历史场景中体验不同策略的效果。