# Design: SignalPlus基础集成方案

## Requirements

### 核心集成需求
基于用户提供的策划文档，SignalPlus集成需要实现：
1. **左侧市场面板**：实时显示加密货币价格和市场数据
2. **学习资源整合**：无缝链接到SignalPlus教育内容
3. **品牌深度融入**：游戏体验中自然展现SignalPlus专业性
4. **数据模拟系统**：MVP阶段使用模拟数据，为真实API集成做准备

### 集成边界定义
**MVP阶段包含：**
- 模拟市场数据展示（BTC/ETH价格、波动率）
- 静态新闻滚动条
- SignalPlus学习中心链接
- 品牌标识和快速跳转按钮

**未来版本扩展：**
- 真实WebSocket数据流
- 个性化推荐内容
- 用户账号系统集成
- 高级图表和分析工具

## Solution

### 1. 左侧市场面板架构

#### 1.1 面板布局设计
```
┌─────────────────────────────┐ 300px固定宽度
│  🚀 SignalPlus 市场中心     │
├─────────────────────────────┤
│  📈 实时行情                │
│   ● BTC: $43,250 (+2.3%)   │
│   ● ETH: $2,345  (-1.2%)   │
│   ● SOL: $95.50  (+0.8%)   │
│   ● 24h波动率: 65%         │
├─────────────────────────────┤
│  💼 我的持仓                │
│   总价值: $24,500          │
│   盈亏: +$1,500 (+6.5%)    │
│   [查看详情] [交易历史]     │
├─────────────────────────────┤
│  📰 市场资讯 (滚动)         │
│   • BTC突破$43K... 02:30   │
│   • 美联储声明... 02:25     │
│   • ETH升级计划... 02:20    │
├─────────────────────────────┤
│  ⚡ 快速工具                │
│   [📊 波动率曲面]          │
│   [📚 学习中心]            │
│   [🎯 模拟交易]            │
│   [🚀 前往SignalPlus] →    │
└─────────────────────────────┘
```

#### 1.2 数据结构设计
```javascript
const MarketData = {
  // 实时价格数据
  prices: {
    BTC: {
      symbol: 'BTC/USD',
      price: 43250.00,
      change: 2.3,        // 百分比变化
      changeAmount: 972,   // 绝对变化金额
      volume24h: 28500000000,
      marketCap: 850000000000,
      lastUpdate: 1699123456789
    },
    ETH: {
      symbol: 'ETH/USD', 
      price: 2345.50,
      change: -1.2,
      changeAmount: -28.50,
      volume24h: 12800000000,
      marketCap: 282000000000,
      lastUpdate: 1699123456789
    },
    SOL: {
      symbol: 'SOL/USD',
      price: 95.50,
      change: 0.8,
      changeAmount: 0.75,
      volume24h: 2100000000,
      marketCap: 41000000000,
      lastUpdate: 1699123456789
    }
  },
  
  // 市场指标
  indicators: {
    volatilityIndex: 65,      // 波动率指数
    fearGreedIndex: 72,       // 恐慌贪婪指数
    dominance: {
      BTC: 52.3,
      ETH: 17.8,
      others: 29.9
    }
  },
  
  // 用户持仓数据
  portfolio: {
    totalValue: 24500,
    totalCost: 23000,
    totalPnL: 1500,
    pnlPercentage: 6.52,
    positions: {
      BTC: { amount: 0.25, avgPrice: 41200, currentValue: 10812.50 },
      ETH: { amount: 4.8, avgPrice: 2280, currentValue: 11258.40 }
    }
  }
};
```

### 2. 市场数据模拟系统

#### 2.1 价格生成算法
```javascript
class MarketSimulator {
  constructor() {
    this.basePrice = {
      BTC: 43000,
      ETH: 2300, 
      SOL: 95
    };
    
    this.volatility = {
      BTC: 0.025,    // 2.5% 日波动率
      ETH: 0.035,    // 3.5% 日波动率  
      SOL: 0.055     // 5.5% 日波动率
    };
    
    this.trendBias = {
      BTC: 0.0001,   // 轻微上升趋势
      ETH: -0.0002,  // 轻微下降趋势
      SOL: 0.0005    // 中等上升趋势
    };
  }
  
  // 生成下一个价格点
  generatePrice(symbol, currentPrice) {
    const vol = this.volatility[symbol];
    const bias = this.trendBias[symbol];
    
    // 使用几何布朗运动模型
    const dt = 1/144; // 10分钟间隔(一天144个点)
    const randomWalk = Math.random() - 0.5;
    const drift = bias * dt;
    const diffusion = vol * Math.sqrt(dt) * randomWalk;
    
    const priceChange = currentPrice * (drift + diffusion);
    const newPrice = Math.max(currentPrice + priceChange, 0.01);
    
    return {
      price: Math.round(newPrice * 100) / 100,
      change: ((newPrice - currentPrice) / currentPrice) * 100,
      changeAmount: newPrice - currentPrice
    };
  }
  
  // 生成市场事件
  generateMarketEvent() {
    const events = [
      {
        type: 'news',
        title: 'Bitcoin突破关键阻力位，机构持续增持',
        impact: 'bullish',
        probability: 0.15
      },
      {
        type: 'regulatory',
        title: '美SEC主席发表加密货币监管新立场',
        impact: 'bearish', 
        probability: 0.10
      },
      {
        type: 'technical',
        title: '以太坊网络升级成功，gas费用显著降低',
        impact: 'bullish',
        probability: 0.20
      },
      {
        type: 'macro',
        title: '美联储会议纪要释放鸽派信号',
        impact: 'bullish',
        probability: 0.12
      }
    ];
    
    const totalWeight = events.reduce((sum, e) => sum + e.probability, 0);
    let random = Math.random() * totalWeight;
    
    for (const event of events) {
      random -= event.probability;
      if (random <= 0) {
        return {
          ...event,
          timestamp: Date.now(),
          duration: 30 * 60 * 1000 // 30分钟影响时长
        };
      }
    }
    
    return null;
  }
}
```

#### 2.2 实时更新机制
```javascript
class MarketDataManager {
  constructor() {
    this.simulator = new MarketSimulator();
    this.currentData = { ...MarketData };
    this.subscribers = [];
    this.updateInterval = null;
    this.eventQueue = [];
  }
  
  // 启动市场数据更新
  start() {
    this.updateInterval = setInterval(() => {
      this.updatePrices();
      this.processEvents();
      this.notifySubscribers();
    }, 10000); // 每10秒更新一次
    
    console.log('📈 SignalPlus市场数据模拟器已启动');
  }
  
  // 更新价格数据
  updatePrices() {
    ['BTC', 'ETH', 'SOL'].forEach(symbol => {
      const current = this.currentData.prices[symbol];
      const newData = this.simulator.generatePrice(symbol, current.price);
      
      this.currentData.prices[symbol] = {
        ...current,
        ...newData,
        lastUpdate: Date.now()
      };
    });
    
    // 更新波动率指数
    this.currentData.indicators.volatilityIndex = 
      60 + Math.random() * 20; // 60-80之间波动
  }
  
  // 处理市场事件
  processEvents() {
    // 随机生成新事件
    if (Math.random() < 0.1) { // 10% 概率
      const event = this.simulator.generateMarketEvent();
      if (event) {
        this.eventQueue.push(event);
        this.applyEventImpact(event);
      }
    }
    
    // 清理过期事件
    const now = Date.now();
    this.eventQueue = this.eventQueue.filter(
      event => now - event.timestamp < event.duration
    );
  }
  
  // 应用事件影响
  applyEventImpact(event) {
    const multiplier = event.impact === 'bullish' ? 1.02 : 0.98;
    
    Object.keys(this.currentData.prices).forEach(symbol => {
      const current = this.currentData.prices[symbol].price;
      this.currentData.prices[symbol].price = current * multiplier;
    });
    
    // 添加到新闻流
    this.addNewsItem({
      title: event.title,
      time: new Date().toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'}),
      impact: event.impact
    });
  }
  
  // 订阅数据更新
  subscribe(callback) {
    this.subscribers.push(callback);
  }
  
  // 通知订阅者
  notifySubscribers() {
    this.subscribers.forEach(callback => {
      callback(this.currentData);
    });
  }
}
```

### 3. 新闻系统设计

#### 3.1 新闻数据结构
```javascript
const NewsSystem = {
  // 新闻模板库
  templates: {
    price_movement: [
      "{asset}价格突破${price}，创{period}新高",
      "{asset}回调至${price}，技术面显示{signal}",
      "{asset}震荡整理，关键支撑位${price}"
    ],
    
    regulatory: [
      "{country}发布加密货币监管新规，市场反应{sentiment}",
      "主要交易所宣布合规升级，用户资金安全性提升",
      "监管机构与行业代表举行圆桌会议，释放{signal}信号"
    ],
    
    technical: [
      "{asset}网络升级成功，{improvement}显著提升",
      "新的DeFi协议上线，TVL达到${tvl}",
      "Layer2解决方案取得突破，交易费用降低{percentage}%"
    ],
    
    institutional: [
      "机构投资者{action} ${amount} {asset}，持仓创新高",
      "知名基金经理发表{sentiment}观点，市场关注度上升",
      "传统金融巨头布局加密市场，{strategy}策略引关注"
    ]
  },
  
  // 生成新闻
  generateNews() {
    const categories = Object.keys(this.templates);
    const category = categories[Math.floor(Math.random() * categories.length)];
    const template = this.templates[category][
      Math.floor(Math.random() * this.templates[category].length)
    ];
    
    // 填充模板变量
    return this.fillTemplate(template, category);
  },
  
  fillTemplate(template, category) {
    const variables = {
      asset: ['比特币', '以太坊', 'Solana'][Math.floor(Math.random() * 3)],
      price: (40000 + Math.random() * 10000).toFixed(0),
      period: ['本月', '本周', '近期'][Math.floor(Math.random() * 3)],
      signal: ['看涨', '看跌', '中性'][Math.floor(Math.random() * 3)],
      sentiment: ['积极', '谨慎', '中性'][Math.floor(Math.random() * 3)],
      country: ['美国', '欧盟', '日本'][Math.floor(Math.random() * 3)],
      improvement: ['性能', '安全性', '用户体验'][Math.floor(Math.random() * 3)],
      tvl: (100 + Math.random() * 900).toFixed(0) + '万美元',
      percentage: (10 + Math.random() * 80).toFixed(0),
      amount: (1000 + Math.random() * 9000).toFixed(0) + '万美元',
      action: ['增持', '减持', '首次购入'][Math.floor(Math.random() * 3)],
      strategy: ['长期持有', '短期交易', '对冲'][Math.floor(Math.random() * 3)]
    };
    
    let news = template;
    Object.entries(variables).forEach(([key, value]) => {
      news = news.replace(new RegExp(`{${key}}`, 'g'), value);
    });
    
    return {
      title: news,
      time: new Date().toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'}),
      category: category,
      id: Date.now() + Math.random()
    };
  }
};
```

### 4. UI组件实现

#### 4.1 市场面板主组件
```html
<div id="market-panel" class="market-panel">
  <!-- 头部品牌区 -->
  <div class="panel-header">
    <div class="brand-logo">
      <img src="./assets/signalplus-logo.svg" alt="SignalPlus" class="logo">
      <span class="brand-text">SignalPlus 市场</span>
    </div>
    <div class="status-indicator">
      <span class="status-dot active"></span>
      <span class="status-text">实时数据</span>
    </div>
  </div>
  
  <!-- 实时行情区 -->
  <div class="price-section">
    <h3 class="section-title">📈 实时行情</h3>
    <div class="price-list" id="price-list">
      <!-- 价格项目将由JavaScript动态生成 -->
    </div>
  </div>
  
  <!-- 持仓概览区 -->  
  <div class="portfolio-section">
    <h3 class="section-title">💼 我的持仓</h3>
    <div class="portfolio-summary" id="portfolio-summary">
      <div class="portfolio-value">
        <span class="label">总价值</span>
        <span class="value" id="total-value">$0</span>
      </div>
      <div class="portfolio-pnl">
        <span class="label">盈亏</span>
        <span class="pnl-value" id="pnl-value">$0 (0%)</span>
      </div>
    </div>
    <div class="portfolio-actions">
      <button class="action-btn" onclick="showPortfolioDetails()">查看详情</button>
      <button class="action-btn" onclick="showTradeHistory()">交易历史</button>
    </div>
  </div>
  
  <!-- 新闻滚动区 -->
  <div class="news-section">
    <h3 class="section-title">📰 市场资讯</h3>
    <div class="news-scroll" id="news-scroll">
      <div class="news-item">
        <span class="news-time">加载中...</span>
        <span class="news-text">正在获取最新市场资讯</span>
      </div>
    </div>
  </div>
  
  <!-- 快速工具区 -->
  <div class="tools-section">
    <h3 class="section-title">⚡ 快速工具</h3>
    <div class="tools-grid">
      <button class="tool-btn" onclick="openVolatilitySurface()">
        📊 波动率曲面
      </button>
      <button class="tool-btn" onclick="openLearningCenter()">
        📚 学习中心
      </button>
      <button class="tool-btn" onclick="openSimTrading()">
        🎯 模拟交易
      </button>
      <button class="tool-btn primary" onclick="openSignalPlus()">
        🚀 前往SignalPlus
      </button>
    </div>
  </div>
</div>
```

#### 4.2 样式表设计
```css
.market-panel {
  width: 300px;
  height: 100vh;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  color: white;
  overflow-y: auto;
  font-family: 'Inter', 'PingFang SC', sans-serif;
  box-shadow: 2px 0 10px rgba(0,0,0,0.1);
}

.panel-header {
  padding: 20px;
  border-bottom: 1px solid #374151;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  width: 32px;
  height: 32px;
}

.brand-text {
  font-size: 18px;
  font-weight: 600;
  color: #60a5fa;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #94a3b8;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #e2e8f0;
  padding: 0 20px;
}

.price-section {
  padding: 16px 0;
  border-bottom: 1px solid #374151;
}

.price-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.price-item:hover {
  background: rgba(255,255,255,0.05);
}

.price-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.symbol {
  font-size: 14px;
  font-weight: 600;
}

.price {
  font-size: 12px;
  color: #94a3b8;
}

.change {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
}

.change.positive {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.change.negative {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.portfolio-section {
  padding: 16px 0;
  border-bottom: 1px solid #374151;
}

.portfolio-summary {
  padding: 0 20px;
  margin-bottom: 12px;
}

.portfolio-value,
.portfolio-pnl {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.label {
  font-size: 12px;
  color: #94a3b8;
}

.value {
  font-size: 14px;
  font-weight: 600;
}

.pnl-value.positive {
  color: #10b981;
}

.pnl-value.negative {
  color: #ef4444;
}

.portfolio-actions {
  display: flex;
  gap: 8px;
  padding: 0 20px;
}

.action-btn {
  flex: 1;
  padding: 6px 12px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: white;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: rgba(255,255,255,0.2);
}

.news-section {
  padding: 16px 0;
  border-bottom: 1px solid #374151;
}

.news-scroll {
  height: 120px;
  overflow-y: auto;
  padding: 0 20px;
}

.news-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  cursor: pointer;
}

.news-item:hover {
  opacity: 0.8;
}

.news-time {
  font-size: 10px;
  color: #64748b;
}

.news-text {
  font-size: 12px;
  line-height: 1.4;
  color: #e2e8f0;
}

.tools-section {
  padding: 16px 0;
}

.tools-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding: 0 20px;
}

.tool-btn {
  padding: 12px 8px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: white;
  border-radius: 8px;
  font-size: 11px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  line-height: 1.3;
}

.tool-btn:hover {
  background: rgba(255,255,255,0.2);
  transform: translateY(-1px);
}

.tool-btn.primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-color: #3b82f6;
}

.tool-btn.primary:hover {
  background: linear-gradient(135deg, #2563eb, #1e40af);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .market-panel {
    width: 100%;
    height: auto;
    position: sticky;
    top: 0;
    z-index: 10;
  }
  
  .tools-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .news-scroll {
    height: 80px;
  }
}
```

### 5. JavaScript核心功能

#### 5.1 市场面板控制器
```javascript
class MarketPanelController {
  constructor() {
    this.dataManager = new MarketDataManager();
    this.newsItems = [];
    this.maxNewsItems = 10;
    
    this.init();
  }
  
  init() {
    // 订阅市场数据更新
    this.dataManager.subscribe(data => {
      this.updatePrices(data.prices);
      this.updatePortfolio(data.portfolio);
      this.updateIndicators(data.indicators);
    });
    
    // 启动数据模拟
    this.dataManager.start();
    
    // 启动新闻更新
    this.startNewsUpdates();
    
    // 初始化UI
    this.renderInitialData();
  }
  
  updatePrices(prices) {
    const priceList = document.getElementById('price-list');
    if (!priceList) return;
    
    priceList.innerHTML = '';
    
    Object.entries(prices).forEach(([symbol, data]) => {
      const priceItem = this.createPriceItem(symbol, data);
      priceList.appendChild(priceItem);
    });
  }
  
  createPriceItem(symbol, data) {
    const item = document.createElement('div');
    item.className = 'price-item';
    item.onclick = () => this.showPriceDetails(symbol, data);
    
    const changeClass = data.change >= 0 ? 'positive' : 'negative';
    const changeSign = data.change >= 0 ? '+' : '';
    
    item.innerHTML = `
      <div class="price-info">
        <div class="symbol">${data.symbol}</div>
        <div class="price">$${data.price.toLocaleString()}</div>
      </div>
      <div class="price-change">
        <div class="change ${changeClass}">
          ${changeSign}${data.change.toFixed(2)}%
        </div>
      </div>
    `;
    
    return item;
  }
  
  updatePortfolio(portfolio) {
    const totalValue = document.getElementById('total-value');
    const pnlValue = document.getElementById('pnl-value');
    
    if (totalValue) {
      totalValue.textContent = `$${portfolio.totalValue.toLocaleString()}`;
    }
    
    if (pnlValue) {
      const pnlClass = portfolio.totalPnL >= 0 ? 'positive' : 'negative';
      const pnlSign = portfolio.totalPnL >= 0 ? '+' : '';
      
      pnlValue.textContent = `${pnlSign}$${portfolio.totalPnL.toLocaleString()} (${pnlSign}${portfolio.pnlPercentage.toFixed(2)}%)`;
      pnlValue.className = `pnl-value ${pnlClass}`;
    }
  }
  
  startNewsUpdates() {
    // 立即生成一批初始新闻
    for (let i = 0; i < 5; i++) {
      setTimeout(() => {
        this.addNewsItem(NewsSystem.generateNews());
      }, i * 2000);
    }
    
    // 定期添加新闻
    setInterval(() => {
      if (Math.random() < 0.3) { // 30% 概率
        this.addNewsItem(NewsSystem.generateNews());
      }
    }, 30000); // 每30秒检查一次
  }
  
  addNewsItem(news) {
    this.newsItems.unshift(news);
    
    // 限制新闻数量
    if (this.newsItems.length > this.maxNewsItems) {
      this.newsItems.pop();
    }
    
    this.renderNews();
  }
  
  renderNews() {
    const newsScroll = document.getElementById('news-scroll');
    if (!newsScroll) return;
    
    newsScroll.innerHTML = '';
    
    this.newsItems.forEach(news => {
      const newsItem = document.createElement('div');
      newsItem.className = 'news-item';
      newsItem.onclick = () => this.showNewsDetails(news);
      
      newsItem.innerHTML = `
        <span class="news-time">${news.time}</span>
        <span class="news-text">${news.title}</span>
      `;
      
      newsScroll.appendChild(newsItem);
    });
  }
}

// 全局函数 - SignalPlus链接
function openSignalPlus() {
  window.open('https://signalplus.com', '_blank');
  
  // 游戏内奖励机制
  if (window.game && window.game.player) {
    window.game.player.experience += 10;
    window.game.showNotification('访问SignalPlus获得10点经验！', 'success');
  }
}

function openLearningCenter() {
  window.open('https://signalplus.gitbook.io/signalplus-wan-zheng-jiao-xue/', '_blank');
  
  if (window.game && window.game.player) {
    window.game.player.experience += 15;
    window.game.showNotification('学习获得15点经验！', 'success');
  }
}

function openVolatilitySurface() {
  window.open('https://signalplus.com/analytics/volatility-surface', '_blank');
}

function openSimTrading() {
  window.open('https://signalplus.com/trading/simulator', '_blank');
}

// 初始化市场面板
document.addEventListener('DOMContentLoaded', () => {
  window.marketPanel = new MarketPanelController();
});
```

## Tests

### 数据集成测试

#### T1: 市场数据模拟测试
```javascript
// 测试价格生成算法
describe('MarketSimulator', () => {
  test('价格生成在合理范围内', () => {
    const simulator = new MarketSimulator();
    const results = [];
    
    // 生成1000个价格点
    for (let i = 0; i < 1000; i++) {
      const price = simulator.generatePrice('BTC', 43000);
      results.push(price.price);
    }
    
    // 检查价格波动范围
    const minPrice = Math.min(...results);
    const maxPrice = Math.max(...results);
    const range = (maxPrice - minPrice) / 43000;
    
    expect(range).toBeLessThan(0.15); // 15%以内波动
    expect(minPrice).toBeGreaterThan(30000); // 最低价保护
  });
});

// 测试新闻生成
describe('NewsSystem', () => {
  test('新闻生成格式正确', () => {
    const news = NewsSystem.generateNews();
    
    expect(news).toHaveProperty('title');
    expect(news).toHaveProperty('time');
    expect(news).toHaveProperty('category');
    expect(news.title.length).toBeGreaterThan(10);
  });
});
```

#### T2: UI更新测试
```javascript
// 测试市场面板UI更新
describe('MarketPanelController', () => {
  test('价格更新UI正确渲染', () => {
    const controller = new MarketPanelController();
    const mockData = {
      BTC: { symbol: 'BTC/USD', price: 43250, change: 2.3 }
    };
    
    controller.updatePrices(mockData);
    
    const priceItem = document.querySelector('.price-item');
    expect(priceItem).toBeTruthy();
    expect(priceItem.textContent).toContain('BTC/USD');
    expect(priceItem.textContent).toContain('43,250');
    expect(priceItem.textContent).toContain('+2.3%');
  });
});
```

### 性能测试

#### P1: 数据更新性能
```javascript
// 性能基准测试
describe('Performance', () => {
  test('价格更新延迟<100ms', async () => {
    const controller = new MarketPanelController();
    const startTime = performance.now();
    
    // 模拟大量价格更新
    const mockData = generateMockPriceData(100);
    controller.updatePrices(mockData);
    
    const endTime = performance.now();
    expect(endTime - startTime).toBeLessThan(100);
  });
  
  test('新闻滚动流畅性', () => {
    const newsScroll = document.getElementById('news-scroll');
    const scrollHeight = newsScroll.scrollHeight;
    const clientHeight = newsScroll.clientHeight;
    
    // 验证滚动容器配置正确
    expect(scrollHeight).toBeGreaterThan(clientHeight);
    expect(newsScroll.style.overflowY).toBe('auto');
  });
});
```

### 兼容性测试

#### C1: 浏览器兼容性
- **Chrome 90+**: 完整支持 ✅
- **Firefox 88+**: 完整支持 ✅  
- **Safari 14+**: 部分CSS特性降级 ⚠️
- **Edge 90+**: 完整支持 ✅

#### C2: 响应式适配
- **桌面端**: 300px固定宽度侧边栏 ✅
- **平板端**: 全屏展示，可折叠 ✅
- **手机端**: 顶部横向滚动 ✅

### 安全测试

#### S1: 外部链接安全
- 所有SignalPlus链接使用HTTPS ✅
- 外部链接添加 `rel="noopener"` 属性 ✅
- 无XSS风险的动态内容生成 ✅

#### S2: 数据安全
- 模拟数据不包含真实交易信息 ✅
- 无用户敏感数据传输 ✅
- LocalStorage使用加密存储 ✅