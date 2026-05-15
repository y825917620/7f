# 神龙地图启动器 - 任务规划

## 项目目标
将启动器从"硬编码调用游戏"升级为"资源控制平台"，建立完整的地图资源接入层。

## 总体阶段

### 阶段 1：资源格式研究产物落地 ✅
- [x] 1.1 完善 `docs/map_resource_format.md`
- [x] 1.2 完善 `docs/game_launch_contract.md`
- [x] 1.3 新建 `docs/map_mounting_decisions.md`

### 阶段 2：实现只读索引与分析层 ✅
- [x] 2.1 MapCatalog：扫描地图库，输出资源完整性状态
- [x] 2.2 MapPackageAnalyzer：只读解包并验证 LuaRDGTM 头
- [x] 2.3 异常地图诊断 + batch_analyze 批量分析

### 阶段 3：建立资源可控化工作区 ✅
- [x] 3.1 ResourceWorkspace：maps/source、maps/workspace、mods、cache/launch
- [x] 3.2 导入地图时自动生成 map_manifest.json
- [x] 3.3 解包写入 workspace，不污染游戏运行目录
- [x] 3.4 公共资源只读 base 索引 + mod 覆盖层预留

### 阶段 4：实现 manifest 驱动的启动 ✅
- [x] 4.1 MapLaunchManifest 替代散乱参数传递
- [x] 4.2 manifest 作为唯一来源驱动启动全链路
- [x] 4.3 GameBridge 只消费 manifest，不自行判断资源

### 阶段 5：接入挂载策略
- [x] 5.1 实现文件挂载策略（已证实有效，默认策略）
- [ ] 5.2 实验验证 /mapfile= 参数策略
- [ ] 5.3 实验验证 MemoryMapName=sanguo 策略
- [x] 5.4 ResourceMountManager 支持策略选择 + dry_run

### 阶段 6：启动链路统一注入 ✅
- [x] 6.1 GameBridge 统一写入命令行/共享内存/管道
- [x] 6.2 彻底移除 mid_val = 10002 硬编码
- [x] 6.3 资源准备失败时不创建游戏进程

### 阶段 7：日志闭环验证 ✅
- [x] 7.1 启动前记录 manifest 到 launcher_logs/
- [x] 7.2 LogVerifier 自动解析日志
- [x] 7.3 UI 集成 verify_launch() 显示真实地图加载状态

### 阶段 8：资源编辑与重打包能力（待启动）
- [ ] 8.1 只读浏览和引用索引
- [ ] 8.2 diff / 回滚 / 校验
- [ ] 8.3 重打包并通过 manifest 接入启动

---

## 验收标准
- [ ] AC1: 选择任意地图，日志中地图名与 UI 一致（需运行验证）
- [x] AC2: 启动器能解释本次使用的源文件、解包文件、挂载策略（manifest）
- [x] AC3: 资源处理集中在接入层，无散落逻辑
- [x] AC4: 所有失败场景有明确错误信息
- [x] AC5: 原始资源只读，修改进入 workspace 或 mod
- [x] AC6: 能生成 launch_manifest / map_manifest
- [ ] AC7: 至少 1 张地图完成"导入→解包→工作区→重新挂载启动"闭环（需运行验证）
- [ ] AC8: 至少 1 个 mod 覆盖可被 manifest 挂载且可禁用恢复（阶段8）
- [ ] AC9: 至少 3 张地图（含 10002 和 2 张非 10002）启动验证通过（需运行验证）
- [ ] AC10: 至少 10 张地图完成离线解包与 manifest 生成验证（需运行验证）

## 不纳入本轮
- 联机功能
- 赞助/VIP
- 外部服务模拟
- 权限绕过
- 界面大改
