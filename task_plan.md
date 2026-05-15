# 神龙地图启动器 - 任务规划

## 项目目标
将启动器从"硬编码调用游戏"升级为"资源控制平台"，建立完整的地图资源接入层。

## 总体阶段

### 阶段 1：资源格式研究产物落地
- [ ] 1.1 完善 `docs/map_resource_format.md`（记录 .map / .sl / LuaRDGTM 已知结构）
- [ ] 1.2 完善 `docs/game_launch_contract.md`（记录启动参数、共享内存、管道、日志阶段）
- [ ] 1.3 新建 `docs/map_mounting_decisions.md`（每个挂载策略的证据和结论）

### 阶段 2：实现只读索引与分析层
- [ ] 2.1 MapCatalog：扫描地图库，输出资源完整性状态
- [ ] 2.2 MapPackageAnalyzer：只读解包并验证 LuaRDGTM 头
- [ ] 2.3 异常地图诊断信息生成

### 阶段 3：建立资源可控化工作区
- [ ] 3.1 实现目录规范：maps/source、maps/workspace、mods、cache/launch
- [ ] 3.2 导入地图时自动生成 map_manifest.json
- [ ] 3.3 解包写入 workspace，不污染游戏运行目录
- [ ] 3.4 公共资源只读 base 索引 + mod 覆盖层预留

### 阶段 4：实现 manifest 驱动的启动
- [ ] 4.1 MapLaunchManifest 替代散乱参数传递
- [ ] 4.2 manifest 作为唯一来源驱动启动全链路
- [ ] 4.3 launch_game 只消费 manifest，不自行判断资源

### 阶段 5：接入挂载策略
- [ ] 5.1 实现文件挂载策略（已验证）
- [ ] 5.2 实验验证 /mapfile= 参数策略
- [ ] 5.3 实验验证 MemoryMapName=sanguo 策略
- [ ] 5.4 完善 ResourceMountManager

### 阶段 6：启动链路统一注入
- [ ] 6.1 GameBridge 统一写入命令行/共享内存/管道
- [ ] 6.2 彻底移除 mid_val = 10002 硬编码
- [ ] 6.3 资源准备失败时不创建游戏进程

### 阶段 7：日志闭环验证
- [ ] 7.1 启动前记录 manifest
- [ ] 7.2 LogVerifier 自动解析日志
- [ ] 7.3 UI 显示真实地图加载状态

### 阶段 8：资源编辑与重打包能力
- [ ] 8.1 只读浏览和引用索引
- [ ] 8.2 diff / 回滚 / 校验
- [ ] 8.3 重打包并通过 manifest 接入启动

---

## 验收标准
- [ ] AC1: 选择任意地图，日志中地图名与 UI 一致
- [ ] AC2: 启动器能解释本次使用的源文件、解包文件、挂载策略
- [ ] AC3: 资源处理集中在接入层，无散落逻辑
- [ ] AC4: 所有失败场景有明确错误信息
- [ ] AC5: 原始资源只读，修改进入 workspace 或 mod
- [ ] AC6: 能生成 game_manifest / map_manifest / launch_manifest
- [ ] AC7: 至少 1 张地图完成"导入→解包→工作区→重新挂载启动"闭环
- [ ] AC8: 至少 1 个 mod 覆盖可被 manifest 挂载且可禁用恢复
- [ ] AC9: 至少 3 张地图（含 10002 和 2 张非 10002）启动验证通过
- [ ] AC10: 至少 10 张地图完成离线解包与 manifest 生成验证

## 不纳入本轮
- 联机功能
- 赞助/VIP
- 外部服务模拟
- 权限绕过
- 界面大改
