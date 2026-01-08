# 游戏状态管理和数据流设计

## 数据流架构

### 前端数据流设计
```
用户操作 → Zustand Store → React组件更新 → UI反馈
    ↓
后端API调用 ← SignalPlus数据 ← 缓存层(Redis)
    ↓
策略计算结果 → 游戏状态更新 → 持久化存储
```

### Zustand Store分层设计

```typescript
// 1. 游戏核心状态
interface GameStore {
  gameState: GameState
  gameActions: {
    initGame: () => void
    rollDice: () => Promise<number>
    movePlayer: (steps: number) => void
    endTurn: () => void
  }
}

// 2. 策略选择和计算
interface StrategyStore {
  availableStrategies: OptionStrategy[]
  currentStrategy?: OptionStrategy
  lastResult?: StrategyResult
  strategyActions: {
    selectStrategy: (id: string) => Promise<StrategyResult>
    calculatePnL: (strategy: OptionStrategy) => number
    getStrategyExplanation: (id: string) => string
  }
}

// 3. 市场数据管理
interface MarketStore {
  currentPrices: Record<string, number>
  marketScenarios: MarketScenario[]
  lastUpdate: Date
  marketActions: {
    fetchPrices: () => Promise<void>
    updateScenario: (scenario: MarketScenario) => void
  }
}

// 4. UI状态管理
interface UIStore {
  isLoading: boolean
  showModal: boolean
  modalContent?: ModalContent
  notifications: Notification[]
  uiActions: {
    showNotification: (message: string, type: 'success' | 'error') => void
    openModal: (content: ModalContent) => void
    closeModal: () => void
  }
}
```

### 实时数据同步策略

```typescript
// 市场数据自动同步
export const useMarketDataSync = () => {
  const { fetchPrices } = useMarketStore()
  
  useEffect(() => {
    const interval = setInterval(fetchPrices, 30000) // 30秒更新
    return () => clearInterval(interval)
  }, [])
}

// 游戏状态持久化
export const useGameStatePersistence = () => {
  const gameState = useGameStore(state => state.gameState)
  
  useEffect(() => {
    localStorage.setItem('game-state', JSON.stringify(gameState))
  }, [gameState])
}

// 离线模式处理
export const useOfflineMode = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  
  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)
    
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])
  
  return isOnline
}
```

## 组件通信架构

### 1. 游戏主界面组件层次

```typescript
<GameApp>
  ├── <GameHeader>           # 游戏信息和设置
  │   ├── <PlayerInfo>       # 玩家资金、回合数
  │   └── <GameControls>     # 暂停、设置、帮助
  │
  ├── <GameBoard>            # 核心游戏区域
  │   ├── <BoardSpaces>      # 12个格子
  │   ├── <PlayerAvatar>     # 玩家位置
  │   └── <DiceArea>         # 掷骰子区域
  │
  ├── <GamePanel>            # 侧边信息面板
  │   ├── <CurrentTurnInfo>  # 当前回合信息
  │   ├── <StrategySelector> # 策略选择
  │   └── <ProgressTracker>  # 学习进度
  │
  └── <GameModals>           # 弹窗组件
      ├── <MarketEventModal> # 市场事件
      ├── <StrategyResultModal> # 策略结果
      └── <SignalPlusModal>  # 引流弹窗
</GameApp>
```

### 2. 事件驱动的游戏流程

```typescript
// 游戏回合流程控制
export const useGameTurnFlow = () => {
  const { gameState, rollDice, movePlayer, endTurn } = useGameStore()
  const { showModal } = useUIStore()
  
  const executeTurn = useCallback(async () => {
    try {
      // 1. 掷骰子
      const steps = await rollDice()
      
      // 2. 移动玩家
      await movePlayer(steps)
      
      // 3. 触发格子事件
      const currentSpace = BOARD_SPACES[gameState.player.position]
      if (currentSpace.marketScenario) {
        showModal({
          type: 'market-event',
          data: currentSpace.marketScenario
        })
      }
      
      // 4. 等待用户策略选择
      // (在Modal中处理)
      
    } catch (error) {
      console.error('Turn execution error:', error)
    }
  }, [gameState.player.position])
  
  return { executeTurn }
}

// 策略选择流程
export const useStrategySelection = () => {
  const { selectStrategy } = useStrategyStore()
  const { updatePlayerFunds } = useGameStore()
  const { showNotification, closeModal } = useUIStore()
  
  const handleStrategyChoice = useCallback(async (strategyId: string) => {
    try {
      const result = await selectStrategy(strategyId)
      
      // 更新玩家资金
      updatePlayerFunds(result.profit)
      
      // 显示结果
      showModal({
        type: 'strategy-result',
        data: result
      })
      
      // 教学反馈
      const feedbackType = result.profit > 0 ? 'success' : 'error'
      showNotification(
        `${result.profit > 0 ? '盈利' : '亏损'} $${Math.abs(result.profit)}`,
        feedbackType
      )
      
    } catch (error) {
      showNotification('策略计算失败，请重试', 'error')
    } finally {
      closeModal()
    }
  }, [])
  
  return { handleStrategyChoice }
}
```

### 3. 性能优化策略

```typescript
// 组件优化
export const GameBoard = React.memo(() => {
  const gameState = useGameStore(state => state.gameState)
  const playerPosition = useMemo(() => gameState.player.position, [gameState])
  
  return (
    <div className="game-board">
      {BOARD_SPACES.map((space, index) => (
        <BoardSpace 
          key={space.id}
          space={space}
          isActive={index === playerPosition}
        />
      ))}
    </div>
  )
})

// 状态选择优化
export const PlayerInfo = () => {
  // 只订阅需要的状态切片
  const playerFunds = useGameStore(state => state.gameState.player.funds)
  const currentTurn = useGameStore(state => state.gameState.currentTurn)
  
  return (
    <div>
      <div>资金: ${playerFunds.toLocaleString()}</div>
      <div>回合: {currentTurn}/20</div>
    </div>
  )
}

// 异步操作优化
export const useAsyncOperation = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const execute = useCallback(async (operation: () => Promise<any>) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const result = await operation()
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])
  
  return { isLoading, error, execute }
}
```

## 缓存和同步策略

### 本地存储策略

```typescript
// 游戏进度自动保存
export const GameProgressManager = {
  save: (gameState: GameState) => {
    try {
      localStorage.setItem('options-monopoly-progress', JSON.stringify({
        gameState,
        timestamp: Date.now(),
        version: '1.0.0'
      }))
    } catch (error) {
      console.warn('Failed to save game progress:', error)
    }
  },
  
  load: (): GameState | null => {
    try {
      const saved = localStorage.getItem('options-monopoly-progress')
      if (!saved) return null
      
      const { gameState, timestamp } = JSON.parse(saved)
      
      // 检查数据是否过期（7天）
      const isExpired = Date.now() - timestamp > 7 * 24 * 60 * 60 * 1000
      if (isExpired) {
        localStorage.removeItem('options-monopoly-progress')
        return null
      }
      
      return gameState
    } catch (error) {
      console.warn('Failed to load game progress:', error)
      return null
    }
  },
  
  clear: () => {
    localStorage.removeItem('options-monopoly-progress')
  }
}

// 用户设置管理
export const UserSettingsManager = {
  save: (settings: UserSettings) => {
    localStorage.setItem('options-monopoly-settings', JSON.stringify(settings))
  },
  
  load: (): UserSettings => {
    try {
      const saved = localStorage.getItem('options-monopoly-settings')
      return saved ? JSON.parse(saved) : DEFAULT_SETTINGS
    } catch {
      return DEFAULT_SETTINGS
    }
  }
}
```

### 数据同步和容错处理

```typescript
// 网络状态管理
export const NetworkManager = {
  async fetchWithRetry<T>(
    operation: () => Promise<T>,
    maxRetries = 3,
    delay = 1000
  ): Promise<T> {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await operation()
      } catch (error) {
        if (attempt === maxRetries) {
          throw error
        }
        
        console.warn(`Attempt ${attempt} failed, retrying in ${delay}ms...`)
        await new Promise(resolve => setTimeout(resolve, delay))
        delay *= 2 // 指数退避
      }
    }
    throw new Error('Should not reach here')
  },
  
  async fetchMarketDataWithFallback(): Promise<MarketData> {
    try {
      // 尝试获取实时数据
      return await this.fetchWithRetry(() => 
        fetch('/api/market/current').then(r => r.json())
      )
    } catch (error) {
      console.warn('Real-time data unavailable, using cached data')
      // 降级到缓存数据
      return CacheManager.getMarketData() || FALLBACK_MARKET_DATA
    }
  }
}

// 错误边界和恢复策略
export class GameErrorBoundary extends React.Component {
  constructor(props: any) {
    super(props)
    this.state = { hasError: false, error: null }
  }
  
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }
  
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Game error:', error, errorInfo)
    
    // 发送错误报告
    this.reportError(error, errorInfo)
  }
  
  reportError(error: Error, errorInfo: React.ErrorInfo) {
    // 可以发送到错误监控服务
    console.error('Error reported:', { error, errorInfo })
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback">
          <h2>游戏遇到了错误</h2>
          <details>
            <summary>错误详情</summary>
            <pre>{this.state.error?.toString()}</pre>
          </details>
          <button onClick={() => window.location.reload()}>
            重新开始游戏
          </button>
        </div>
      )
    }
    
    return this.props.children
  }
}
```

这个状态管理和数据流设计确保了：

1. **清晰的数据流向**：单向数据流，状态变化可预测
2. **性能优化**：组件级优化，按需订阅状态切片
3. **容错处理**：网络错误、数据错误的优雅降级
4. **用户体验**：游戏进度自动保存，离线可用
5. **可维护性**：模块化设计，职责分离明确