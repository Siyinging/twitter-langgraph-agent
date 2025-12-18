# Design tech-implementation

## Requirements

### 技术实现方案总览
为加密期权大富翁游戏制定完整的技术实现方案，涵盖前端架构、后端集成、数据管理、性能优化和部署策略。

**核心技术要求：**
- React 19 + TypeScript 现代化前端架构
- 实时数据同步和多人游戏支持
- SignalPlus深度集成和数据可视化
- 高性能状态管理和缓存策略
- 响应式设计和多设备支持
- 可扩展的微服务架构

**性能指标：**
- 页面加载时间 < 3秒
- 游戏操作响应时间 < 100ms
- 支持同时在线玩家 > 1000人
- 99.9% 服务可用性
- 移动端流畅运行 (60fps)

### 开发规范和最佳实践
- TypeScript严格模式
- ESLint + Prettier代码规范
- Git Flow工作流程
- 测试驱动开发(TDD)
- 持续集成/部署(CI/CD)

## Solution

### 1. 前端技术架构

#### 1.1 核心技术栈
```typescript
interface TechStack {
  // 基础框架
  framework: 'React 19';
  language: 'TypeScript 5.0+';
  bundler: 'Vite 5.0';
  
  // 状态管理
  stateManagement: 'Zustand';
  
  // UI组件库
  styling: 'Tailwind CSS';
  animations: 'Framer Motion';
  charts: 'Chart.js + React-Chartjs-2';
  
  // 实时通信
  websocket: 'Socket.IO Client';
  
  // 数据获取
  httpClient: 'Axios';
  reactQuery: '@tanstack/react-query';
  
  // 路由
  router: 'React Router v6';
  
  // 表单处理
  forms: 'React Hook Form + Zod';
  
  // 测试
  unitTest: 'Vitest + Testing Library';
  e2eTest: 'Playwright';
  
  // 代码质量
  linter: 'ESLint + TypeScript-ESLint';
  formatter: 'Prettier';
  precommit: 'Husky + lint-staged';
}
```

#### 1.2 项目结构设计
```
src/
├── components/           # 通用组件
│   ├── ui/              # 基础UI组件
│   ├── game/            # 游戏专用组件
│   │   ├── GameBoard.tsx
│   │   ├── PlayerCard.tsx
│   │   ├── TradingCard.tsx
│   │   └── SignalPlusPanel.tsx
│   ├── charts/          # 图表组件
│   └── layout/          # 布局组件
├── pages/               # 页面组件
│   ├── GameLobby.tsx
│   ├── GameRoom.tsx
│   ├── LeaderBoard.tsx
│   └── Profile.tsx
├── hooks/               # 自定义Hook
│   ├── useGameEngine.ts
│   ├── useSignalPlus.ts
│   ├── useWebSocket.ts
│   └── useLocalStorage.ts
├── stores/              # Zustand状态管理
│   ├── gameStore.ts
│   ├── playerStore.ts
│   ├── uiStore.ts
│   └── signalPlusStore.ts
├── types/               # TypeScript类型定义
│   ├── game.ts
│   ├── api.ts
│   └── signalplus.ts
├── utils/               # 工具函数
│   ├── gameLogic.ts
│   ├── calculations.ts
│   ├── formatters.ts
│   └── validators.ts
├── services/            # API服务
│   ├── gameApi.ts
│   ├── signalPlusApi.ts
│   └── websocketService.ts
├── assets/              # 静态资源
│   ├── images/
│   ├── icons/
│   └── sounds/
└── styles/              # 样式文件
    ├── globals.css
    └── components.css
```

#### 1.3 状态管理架构
```typescript
// 游戏状态管理
interface GameStore {
  // 基础游戏状态
  gameState: GameState;
  currentPlayer: Player | null;
  gameBoard: GameBoardState;
  
  // 行动状态
  isRolling: boolean;
  isProcessingTurn: boolean;
  pendingActions: GameAction[];
  
  // Actions
  initializeGame: (players: Player[]) => void;
  rollDice: () => Promise<void>;
  movePlayer: (playerId: string, steps: number) => void;
  processSpaceEffect: (spaceId: number) => Promise<void>;
  endTurn: () => void;
  
  // 实时数据同步
  syncGameState: (remoteState: GameState) => void;
  publishAction: (action: GameAction) => void;
}

// SignalPlus数据管理
interface SignalPlusStore {
  // 市场数据
  marketData: MarketDataState;
  newsFeeds: NewsItem[];
  chartConfigs: ChartConfiguration[];
  
  // 实时更新
  lastUpdate: Date;
  isConnected: boolean;
  
  // Actions
  fetchMarketData: (symbols: string[]) => Promise<void>;
  subscribeToRealTimeData: (callback: DataCallback) => void;
  updateChartData: (symbol: string, data: ChartData) => void;
  
  // 缓存管理
  clearCache: () => void;
  getCachedData: (key: string) => any;
}
```

### 2. 后端服务架构

#### 2.1 微服务设计
```typescript
interface MicroservicesArchitecture {
  services: {
    // 游戏引擎服务
    gameEngine: {
      responsibilities: [
        '游戏逻辑处理',
        '回合制管理',
        '规则验证',
        '状态同步'
      ];
      technology: 'Node.js + Express + TypeScript';
      database: 'MongoDB (游戏状态) + Redis (缓存)';
    };
    
    // 用户管理服务
    userService: {
      responsibilities: [
        '用户认证授权',
        '个人资料管理',
        '成就系统',
        '社交功能'
      ];
      technology: 'Node.js + Express + TypeScript';
      database: 'PostgreSQL + Redis';
    };
    
    // SignalPlus集成服务
    signalPlusProxy: {
      responsibilities: [
        'SignalPlus API代理',
        '数据转换和缓存',
        '实时数据推送',
        '市场数据分析'
      ];
      technology: 'Node.js + Express + TypeScript';
      database: 'TimescaleDB + Redis';
    };
    
    // 实时通信服务
    websocketService: {
      responsibilities: [
        'WebSocket连接管理',
        '多人游戏同步',
        '实时消息推送',
        '房间管理'
      ];
      technology: 'Node.js + Socket.IO + TypeScript';
      database: 'Redis (会话管理)';
    };
    
    // 数据分析服务
    analyticsService: {
      responsibilities: [
        '游戏数据分析',
        '用户行为追踪',
        '性能监控',
        '商业智能'
      ];
      technology: 'Python + FastAPI';
      database: 'ClickHouse + Elasticsearch';
    };
  };
}
```

#### 2.2 API网关设计
```typescript
interface APIGateway {
  // 路由配置
  routes: {
    '/api/v1/auth/*': 'userService';
    '/api/v1/game/*': 'gameEngine';
    '/api/v1/signalplus/*': 'signalPlusProxy';
    '/api/v1/analytics/*': 'analyticsService';
    '/ws/*': 'websocketService';
  };
  
  // 中间件
  middleware: [
    'rateLimiting',    // 频率限制
    'authentication', // 认证
    'authorization',  // 授权
    'logging',        // 日志
    'caching',        // 缓存
    'compression',    // 压缩
    'cors'           // 跨域
  ];
  
  // 负载均衡
  loadBalancing: {
    algorithm: 'round-robin';
    healthCheck: true;
    circuit: true;
  };
}
```

### 3. 数据库设计

#### 3.1 数据模型
```typescript
// MongoDB - 游戏数据模型
interface GameDocument {
  _id: ObjectId;
  gameId: string;
  createdAt: Date;
  updatedAt: Date;
  status: 'waiting' | 'playing' | 'finished';
  
  // 游戏配置
  config: {
    maxPlayers: number;
    boardType: '12-spaces' | '28-spaces';
    timeLimit: number;
    signalPlusEnabled: boolean;
  };
  
  // 玩家数据
  players: {
    playerId: string;
    position: number;
    portfolio: Portfolio;
    achievements: string[];
    stats: GameStats;
  }[];
  
  // 游戏状态
  currentState: {
    turn: number;
    currentPlayer: string;
    marketCycle: MarketCycle;
    events: GameEvent[];
    board: BoardState;
  };
  
  // 历史记录
  history: GameAction[];
}

// PostgreSQL - 用户数据模型
interface UserModel {
  id: string;
  email: string;
  username: string;
  avatar?: string;
  createdAt: Date;
  updatedAt: Date;
  
  // 游戏统计
  gameStats: {
    gamesPlayed: number;
    gamesWon: number;
    totalXP: number;
    level: number;
    achievements: Achievement[];
  };
  
  // 学习进度
  learningProgress: {
    completedModules: string[];
    currentPath: string;
    xpEarned: number;
    skillLevel: SkillLevel;
  };
  
  // 社交数据
  social: {
    friends: string[];
    blockedUsers: string[];
    preferences: UserPreferences;
  };
}

// TimescaleDB - 市场数据模型
interface MarketDataModel {
  time: Date;
  symbol: string;
  price: number;
  volume: number;
  volatility: number;
  
  // 期权数据
  optionChain: {
    strike: number;
    expiry: Date;
    callPrice: number;
    putPrice: number;
    impliedVolatility: number;
  }[];
  
  // 技术指标
  technicalIndicators: {
    rsi: number;
    macd: number;
    bollinger: {
      upper: number;
      middle: number;
      lower: number;
    };
  };
}
```

#### 3.2 缓存策略
```typescript
interface CacheStrategy {
  // Redis缓存分层
  layers: {
    // L1: 应用层缓存 (内存)
    application: {
      ttl: 30; // 秒
      data: ['game-state', 'player-positions', 'ui-state'];
    };
    
    // L2: Redis缓存
    redis: {
      ttl: 300; // 秒
      data: ['market-data', 'user-sessions', 'leaderboards'];
    };
    
    // L3: CDN缓存
    cdn: {
      ttl: 3600; // 秒
      data: ['static-assets', 'game-configs', 'achievement-icons'];
    };
  };
  
  // 缓存策略
  strategies: {
    writeThrough: ['user-data', 'game-results'];
    writeBack: ['game-actions', 'market-ticks'];
    readThrough: ['historical-data', 'analytics'];
  };
}
```

### 4. 实时数据同步

#### 4.1 WebSocket架构
```typescript
interface WebSocketArchitecture {
  // 连接管理
  connectionManager: {
    maxConnections: 10000;
    heartbeat: 30000; // ms
    reconnectStrategy: 'exponential-backoff';
    
    // 房间管理
    rooms: {
      gameRooms: Map<string, GameRoom>;
      privateRooms: Map<string, PrivateRoom>;
      globalRoom: GlobalRoom;
    };
  };
  
  // 消息类型
  messageTypes: {
    // 游戏消息
    GAME_STATE_UPDATE: GameStateMessage;
    PLAYER_ACTION: PlayerActionMessage;
    TURN_START: TurnStartMessage;
    TURN_END: TurnEndMessage;
    
    // SignalPlus消息
    MARKET_DATA_UPDATE: MarketDataMessage;
    PRICE_ALERT: PriceAlertMessage;
    NEWS_UPDATE: NewsMessage;
    
    // 系统消息
    USER_JOIN: UserJoinMessage;
    USER_LEAVE: UserLeaveMessage;
    ERROR: ErrorMessage;
  };
  
  // 数据同步策略
  syncStrategy: {
    // 乐观锁机制
    optimisticLocking: true;
    conflictResolution: 'last-write-wins';
    
    // 批量更新
    batchUpdates: {
      maxSize: 100;
      interval: 50; // ms
    };
  };
}
```

#### 4.2 SignalPlus集成
```typescript
interface SignalPlusIntegration {
  // API配置
  apiConfig: {
    baseUrl: 'https://api.signalplus.com';
    websocketUrl: 'wss://ws.signalplus.com';
    apiKey: string;
    rateLimits: {
      requests: 1000; // per minute
      websocket: 10; // connections
    };
  };
  
  // 数据流管理
  dataStreams: {
    // 实时价格流
    priceStream: {
      symbols: string[];
      updateInterval: 1000; // ms
      bufferSize: 1000;
    };
    
    // 新闻流
    newsStream: {
      categories: ['crypto', 'defi', 'options'];
      language: 'en' | 'zh';
      updateInterval: 5000; // ms
    };
    
    // 市场深度
    orderBookStream: {
      symbols: string[];
      depth: 20;
      updateInterval: 500; // ms
    };
  };
  
  // 数据处理管道
  processingPipeline: {
    // 数据清洗
    cleaning: {
      removeOutliers: true;
      validateRanges: true;
      handleMissingData: 'interpolation';
    };
    
    // 数据转换
    transformation: {
      normalization: true;
      aggregation: 'ohlcv';
      timeframes: ['1m', '5m', '15m', '1h', '1d'];
    };
    
    // 数据存储
    storage: {
      realtime: 'Redis';
      historical: 'TimescaleDB';
      analytics: 'ClickHouse';
    };
  };
}
```

### 5. 性能优化策略

#### 5.1 前端优化
```typescript
interface FrontendOptimization {
  // 代码分割
  codeSplitting: {
    routeBased: true;
    componentBased: true;
    vendorSeparation: true;
    
    // 动态导入
    lazyLoading: [
      'GameBoard', 'SignalPlusCharts', 
      'AdvancedSettings', 'Analytics'
    ];
  };
  
  // 资源优化
  assetOptimization: {
    // 图片优化
    images: {
      format: 'WebP + fallback';
      compression: 'lossy-80%';
      lazyLoading: true;
      responsiveImages: true;
    };
    
    // 字体优化
    fonts: {
      preload: ['primary-font.woff2'];
      display: 'swap';
      subset: 'unicode-range';
    };
  };
  
  // 渲染优化
  renderOptimization: {
    // React优化
    reactOptimization: {
      memo: 'selective-components';
      useMemo: 'expensive-calculations';
      useCallback: 'event-handlers';
      virtualization: 'long-lists';
    };
    
    // 动画优化
    animationOptimization: {
      will-change: 'transform-properties';
      gpu-acceleration: true;
      reduced-motion: 'respect-preference';
    };
  };
}
```

#### 5.2 后端优化
```typescript
interface BackendOptimization {
  // 数据库优化
  databaseOptimization: {
    // 索引策略
    indexing: {
      primary: ['gameId', 'userId', 'timestamp'];
      composite: ['gameId-turn', 'userId-gameId'];
      partial: 'active-games-only';
    };
    
    // 查询优化
    queryOptimization: {
      connectionPooling: {
        min: 10;
        max: 100;
        idle: 30000; // ms
      };
      batchOperations: true;
      preparedStatements: true;
    };
    
    // 分片策略
    sharding: {
      strategy: 'consistent-hashing';
      shardKey: 'userId';
      replication: 3;
    };
  };
  
  // API优化
  apiOptimization: {
    // 缓存策略
    caching: {
      redis: {
        strategy: 'cache-aside';
        ttl: 300; // 秒
        compression: true;
      };
      cdn: {
        static: 'max-age=31536000';
        dynamic: 'max-age=300';
      };
    };
    
    // 压缩策略
    compression: {
      gzip: true;
      brotli: true;
      threshold: 1024; // bytes
    };
  };
}
```

### 6. 安全策略

#### 6.1 认证和授权
```typescript
interface SecurityStrategy {
  // 认证机制
  authentication: {
    // JWT配置
    jwt: {
      algorithm: 'RS256';
      expirationTime: '1h';
      refreshTokenTTL: '7d';
      issuer: 'crypto-monopoly-game';
    };
    
    // OAuth集成
    oauth: {
      providers: ['Google', 'GitHub', 'Discord'];
      scopes: ['profile', 'email'];
    };
    
    // 多因子认证
    mfa: {
      enabled: true;
      methods: ['TOTP', 'SMS', 'Email'];
    };
  };
  
  // 授权模型
  authorization: {
    // RBAC权限模型
    rbac: {
      roles: ['guest', 'player', 'moderator', 'admin'];
      permissions: [
        'game:play', 'game:create', 'game:moderate',
        'user:view', 'user:edit', 'admin:access'
      ];
    };
    
    // 资源保护
    resourceProtection: {
      gameData: 'owner-or-participant';
      userData: 'owner-only';
      systemData: 'admin-only';
    };
  };
  
  // 数据安全
  dataSecurity: {
    // 加密策略
    encryption: {
      atRest: 'AES-256-GCM';
      inTransit: 'TLS-1.3';
      keyRotation: '30-days';
    };
    
    // 输入验证
    inputValidation: {
      sanitization: true;
      whitelisting: true;
      typeChecking: true;
      lengthLimits: true;
    };
  };
}
```

### 7. 监控和运维

#### 7.1 监控体系
```typescript
interface MonitoringSystem {
  // 应用监控
  applicationMonitoring: {
    // 性能指标
    performance: {
      responseTime: 'p50, p95, p99';
      throughput: 'requests-per-second';
      errorRate: 'percentage';
      availability: 'uptime-percentage';
    };
    
    // 业务指标
    businessMetrics: {
      activeUsers: 'concurrent-count';
      gameCreations: 'per-hour';
      signalPlusRequests: 'per-minute';
      userEngagement: 'session-duration';
    };
  };
  
  // 基础设施监控
  infrastructureMonitoring: {
    // 系统资源
    systemResources: {
      cpu: 'usage-percentage';
      memory: 'usage-mb';
      disk: 'io-operations';
      network: 'bandwidth-utilization';
    };
    
    // 数据库监控
    database: {
      connections: 'active-count';
      queryPerformance: 'execution-time';
      lockWait: 'wait-duration';
      replicationLag: 'seconds';
    };
  };
  
  // 告警策略
  alerting: {
    // 严重告警
    critical: {
      triggers: ['service-down', 'database-failure', 'high-error-rate'];
      channels: ['PagerDuty', 'Slack', 'SMS'];
      escalation: '5-minutes';
    };
    
    // 警告告警
    warning: {
      triggers: ['high-latency', 'resource-usage', 'slow-queries'];
      channels: ['Slack', 'Email'];
      escalation: '15-minutes';
    };
  };
}
```

#### 7.2 部署策略
```typescript
interface DeploymentStrategy {
  // 容器化
  containerization: {
    // Docker配置
    docker: {
      baseImage: 'node:18-alpine';
      multiStage: true;
      healthcheck: true;
      secrets: 'buildkit-secrets';
    };
    
    // Kubernetes配置
    kubernetes: {
      orchestration: 'K8s-1.27+';
      ingress: 'NGINX-Ingress';
      serviceMesh: 'Istio';
      autoscaling: 'HPA + VPA';
    };
  };
  
  // CI/CD管道
  cicd: {
    // 构建阶段
    build: {
      trigger: 'git-push';
      stages: ['test', 'security-scan', 'build', 'package'];
      parallelization: true;
    };
    
    // 部署阶段
    deployment: {
      strategy: 'blue-green';
      environments: ['dev', 'staging', 'production'];
      rollback: 'automatic-on-failure';
      canary: '10%-50%-100%';
    };
  };
  
  // 环境配置
  environments: {
    development: {
      replicas: 1;
      resources: 'minimal';
      features: 'all-enabled';
    };
    
    staging: {
      replicas: 2;
      resources: 'production-like';
      features: 'production-subset';
    };
    
    production: {
      replicas: 3;
      resources: 'optimized';
      features: 'stable-only';
    };
  };
}
```

## Tests

### 单元测试策略

#### 1. 前端单元测试
```typescript
describe('GameEngine Tests', () => {
  let gameEngine: GameEngine;
  let mockSignalPlusAPI: jest.Mocked<SignalPlusAPI>;
  
  beforeEach(() => {
    mockSignalPlusAPI = createMockSignalPlusAPI();
    gameEngine = new GameEngine({ signalPlusAPI: mockSignalPlusAPI });
  });
  
  describe('processTurn', () => {
    test('should process dice roll correctly', async () => {
      const playerId = 'player-123';
      const diceResult = [3, 4];
      
      const result = await gameEngine.processTurn(playerId, {
        type: 'roll_dice',
        data: diceResult
      });
      
      expect(result.success).toBe(true);
      expect(result.newPosition).toBe(7);
      expect(result.spaceEffect).toBeDefined();
    });
    
    test('should handle market events', async () => {
      const playerId = 'player-123';
      const marketEvent = createMockMarketEvent('bull_market');
      
      const result = await gameEngine.processMarketEvent(playerId, marketEvent);
      
      expect(result.portfolioChange).toBeGreaterThan(0);
      expect(mockSignalPlusAPI.getMarketData).toHaveBeenCalled();
    });
  });
  
  describe('SignalPlus Integration', () => {
    test('should fetch real-time market data', async () => {
      const symbols = ['BTC', 'ETH', 'SOL'];
      
      const data = await gameEngine.getMarketData(symbols);
      
      expect(data.length).toBe(3);
      expect(data[0].symbol).toBe('BTC');
      expect(data[0].price).toBeGreaterThan(0);
    });
  });
});
```

#### 2. 后端单元测试
```typescript
describe('Game Service Tests', () => {
  let gameService: GameService;
  let mockGameRepository: jest.Mocked<GameRepository>;
  
  beforeEach(() => {
    mockGameRepository = createMockGameRepository();
    gameService = new GameService(mockGameRepository);
  });
  
  describe('createGame', () => {
    test('should create new game with valid configuration', async () => {
      const gameConfig = {
        maxPlayers: 4,
        boardType: '28-spaces' as const,
        signalPlusEnabled: true
      };
      
      const game = await gameService.createGame(gameConfig);
      
      expect(game.id).toBeDefined();
      expect(game.status).toBe('waiting');
      expect(game.config.maxPlayers).toBe(4);
    });
    
    test('should validate game configuration', async () => {
      const invalidConfig = {
        maxPlayers: 0,
        boardType: 'invalid' as any
      };
      
      await expect(gameService.createGame(invalidConfig))
        .rejects.toThrow('Invalid game configuration');
    });
  });
});
```

### 集成测试

#### 1. API集成测试
```typescript
describe('Game API Integration', () => {
  let app: Express;
  let testDb: TestDatabase;
  
  beforeAll(async () => {
    testDb = await setupTestDatabase();
    app = createTestApp({ database: testDb });
  });
  
  afterAll(async () => {
    await teardownTestDatabase(testDb);
  });
  
  describe('POST /api/v1/games', () => {
    test('should create game successfully', async () => {
      const response = await request(app)
        .post('/api/v1/games')
        .set('Authorization', `Bearer ${validJWT}`)
        .send({
          maxPlayers: 4,
          boardType: '28-spaces'
        })
        .expect(201);
      
      expect(response.body.gameId).toBeDefined();
      expect(response.body.status).toBe('waiting');
    });
  });
  
  describe('WebSocket Game Events', () => {
    test('should broadcast game state updates', async (done) => {
      const client1 = io('http://localhost:3000', {
        auth: { token: validJWT1 }
      });
      
      const client2 = io('http://localhost:3000', {
        auth: { token: validJWT2 }
      });
      
      client1.on('game-state-update', (data) => {
        expect(data.currentPlayer).toBeDefined();
        expect(data.turn).toBeGreaterThan(0);
        done();
      });
      
      // 触发游戏状态更新
      client2.emit('player-action', {
        gameId: testGameId,
        action: { type: 'roll_dice' }
      });
    });
  });
});
```

### 性能测试

#### 1. 负载测试
```typescript
describe('Load Testing', () => {
  test('should handle concurrent game sessions', async () => {
    const concurrentGames = 100;
    const playersPerGame = 4;
    
    const gamePromises = Array.from({ length: concurrentGames }, () =>
      createAndPlayGame(playersPerGame)
    );
    
    const results = await Promise.all(gamePromises);
    
    // 验证所有游戏都成功完成
    results.forEach(result => {
      expect(result.completed).toBe(true);
      expect(result.duration).toBeLessThan(300000); // <5分钟
    });
    
    // 验证服务器性能指标
    const serverMetrics = await getServerMetrics();
    expect(serverMetrics.cpuUsage).toBeLessThan(80);
    expect(serverMetrics.memoryUsage).toBeLessThan(2048); // <2GB
    expect(serverMetrics.responseTime.p95).toBeLessThan(200); // <200ms
  });
  
  test('should handle SignalPlus API rate limits', async () => {
    const requests = 1000;
    const timeWindow = 60000; // 1分钟
    
    const startTime = Date.now();
    const promises = Array.from({ length: requests }, () =>
      signalPlusAPI.getMarketData(['BTC'])
    );
    
    const results = await Promise.allSettled(promises);
    const duration = Date.now() - startTime;
    
    // 验证在时间窗口内完成
    expect(duration).toBeLessThan(timeWindow * 2);
    
    // 验证成功率
    const successCount = results.filter(r => r.status === 'fulfilled').length;
    expect(successCount / requests).toBeGreaterThan(0.95); // >95%成功率
  });
});
```

### 安全测试

#### 1. 认证授权测试
```typescript
describe('Security Tests', () => {
  describe('Authentication', () => {
    test('should reject invalid JWT tokens', async () => {
      const invalidToken = 'invalid.jwt.token';
      
      const response = await request(app)
        .get('/api/v1/games')
        .set('Authorization', `Bearer ${invalidToken}`)
        .expect(401);
      
      expect(response.body.error).toBe('Invalid token');
    });
    
    test('should enforce rate limiting', async () => {
      const requests = 101; // 超过限制
      const promises = Array.from({ length: requests }, () =>
        request(app)
          .post('/api/v1/auth/login')
          .send({ email: 'test@example.com', password: 'password' })
      );
      
      const results = await Promise.all(promises);
      const rateLimitedCount = results.filter(r => r.status === 429).length;
      
      expect(rateLimitedCount).toBeGreaterThan(0);
    });
  });
  
  describe('Input Validation', () => {
    test('should sanitize user input', async () => {
      const maliciousInput = '<script>alert("xss")</script>';
      
      const response = await request(app)
        .post('/api/v1/games')
        .set('Authorization', `Bearer ${validJWT}`)
        .send({
          name: maliciousInput,
          description: maliciousInput
        })
        .expect(400);
      
      expect(response.body.error).toContain('Invalid input');
    });
  });
});
```

## 实施计划

### 第一阶段：基础架构 (2-3周)
1. 搭建开发环境和CI/CD管道
2. 实现基础的前后端架构
3. 集成基本的SignalPlus API
4. 建立数据库和缓存系统

### 第二阶段：核心功能 (3-4周)
1. 实现游戏引擎核心逻辑
2. 开发WebSocket实时通信
3. 集成完整的SignalPlus功能
4. 实现用户认证和授权

### 第三阶段：高级功能 (2-3周)
1. 实现多人游戏和房间管理
2. 开发数据分析和监控系统
3. 优化性能和用户体验
4. 完善安全和运维体系

### 第四阶段：测试和上线 (1-2周)
1. 完整的测试覆盖
2. 性能和安全测试
3. 生产环境部署
4. 监控和运维上线