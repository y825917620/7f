# SL10002 启动器改造计划 (v2 — 基于参考包)

## 目标
完全对齐 `SL10002 FinalLauncher V45` C# 参考实现，实现单机/局域网联机启动器。

## 核心架构（来自参考包）
```
启动器 → 文件准备 (.sl拆包+Blowfish解密 → map/{id}/+.o)
       → 启动 HostService (TCP 29002)
       → 构建 PlatformBlock (0x435 bytes SHM)
       → CreateProcess(game.exe /mapfile={id} MemoryMapName={custom})
       → HostService 响应游戏会话协议
       → 退出时生成 SL10002_ONE_LOG.txt
```

## 实施阶段

### 阶段 1: 文件准备 (已验证)
- [x] .sl 拆包: LZMA_ALONE 解压
- [x] Payload 解密: Blowfish/ECB, key="DEFAULT_KEY\0"
- [x] 写入 map/{id}/{id}.map + map/{id}/{id}.o + map/sanguo/
- [x] config.lua 生成 (SrvScriptInfo/load_rolesdk hooks)
- [x] edt2.o + map.o 编译
- [ ] 修复: 所有地图 (非仅10002) 的加载方式统一

### 阶段 2: HostService (已验证)
- [x] TCP 29002 监听
- [x] 0x013A 登录响应
- [x] 0x015A/0x017A 玩家列表
- [x] 0x0138 控制帧/心跳
- [ ] 修复: 客户端模式连接到远程主机

### 阶段 3: 进程启动 (已验证)
- [x] PlatformBlock SHM (0x435 bytes)
- [x] 双 SHM: "10002" + 自定义名
- [x] 命令行: /mapfile={id} MemoryMapName={custom}
- [x] CreateProcess: no pipe, no NUL, bInheritHandles=False
- [x] 互斥体 7fxx_dgtm

### 阶段 4: UI
- [x] 暗色工业风
- [x] 地图列表 (名称+作者)
- [x] 每地图独立选项解析
- [x] 模式选择: 单机/主机/客户端
- [ ] 修复: 启动按钮在 GUI 模式下实际生效
- [ ] 修复: 日志输出到文件

### 阶段 5: LAN 房间
- [ ] 主机创建房间: HostService 启动 + 广播/等待
- [ ] 客户端加入: 连接主机 IP:29002
- [ ] 主机控制地图设置
- [ ] 客户端只可选玩家槽位

### 阶段 6: 验证
- [ ] 终端测试启动成功
- [ ] GUI exe 启动成功
- [ ] AfterRun > 5 帧
- [ ] sanguo.o 加载成功
- [ ] 多地图测试 (非10002)
