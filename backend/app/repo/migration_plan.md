# 仓储迁移计划

## 1. 现状（v1 in-memory）
- 当前后端所有服务只依赖 `Repository Protocol`。
- 运行时数据驻留在单进程内存中，重启即丢失。
- `GameSession`、`MetaProgress`、`PressArchive`、`AgentMemory` 都先按内存仓库跑通。
- 这一版的目标是冻结接口，不把持久化细节泄漏到 service。

## 2. v2 目标（PostgreSQL + Redis）
- PostgreSQL 持久化：
  - `GameSession`
  - `MetaProgress`
- Redis 承担短期态：
  - session 缓存
  - 限流计数
  - WS 在线会话索引
  - press transcript 访问控制与节流
- 切换仓库时，service 代码不改，只替换 repo 实现。

## 3. 数据模型映射
- `GameSessionORM` -> `GameSession`
  - `company_json` 对应 `Company`
  - `stats_json` 对应 `Stats`
  - `quarter_json` 对应 `Quarter`
  - 其余聚合成员在 JSON 中整体保存
- `MetaProgressORM` -> `MetaProgress`
  - `data_json` 保存完整跨局进度
- `PressArchiveORM` -> `PressBundle`
  - 以 `session_id` 归档单次 press 结果
- `AgentMemoryORM` -> `MemoryEntry`
  - 按 `player_id` 与 `session_id` 做查询与回放

## 4. 迁移步骤
1. 初始化 Alembic。
2. 创建三张主表与一张记忆表：
   - `game_sessions`
   - `meta_progress`
   - `press_archive`
   - `agent_memory`
3. 写一次性数据导入脚本，把 v1 内存快照导入 PostgreSQL。
4. 灰度切换：
   - 先让读走 PostgreSQL，写仍双写到内存与数据库。
   - 再把写切到 PostgreSQL，保留回退开关。
5. 回滚预案：
   - 保留内存实现作为紧急降级。
   - 通过环境变量切回 v1 repo。

## 5. Redis 用途
- 限流：按 `player_id`、IP、接口名做短窗计数。
- WS 在线会话索引：记录当前在线的 session / player 映射。
- press transcript 限流：避免同一局内重复提交过多 transcript。
- 短期缓存：缓存最近一次 session 读取结果，减少 PostgreSQL 热读。

## 6. 性能预算
- `v2` 单次 `session save` 目标：P99 < 50ms。
- `meta_progress.get` 目标：P99 < 20ms。
- 关键手段：
  - 读写分离的缓存策略
  - JSON 序列化保持轻量
  - 索引覆盖 `player_id`、`session_id`
  - 避免在仓库层做业务计算

## 7. 测试策略
- 单测继续覆盖内存实现与协议兼容性。
- CI 增加：
  - `testcontainers`
  - 或 `docker-compose`
- 重点验证：
  - 迁移脚本可重复执行
  - 回滚后 service 行为不变
  - 归档顺序与查询窗口稳定

## 8. 明确声明
- 本仓库当前不包含 ORM 迁移执行代码。
- 这里只声明 SQLAlchemy 骨架，不调用 `create_engine`。
- 不在运行时连接数据库，不在此文件中执行 Alembic。
- 真正的数据库落地放到 v2 阶段单独实现。
