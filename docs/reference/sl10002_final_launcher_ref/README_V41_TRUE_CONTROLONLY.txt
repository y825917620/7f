SL10002 V41 TRUE CONTROLONLY LOWPORT

本版修复 V40 的关键误差：
1. V40 名义上是 ControlOnly，但 start_10002.bat 实际传入的是 -ProtocolVariant TurnStream。
2. V41 已改为真正传入 -ProtocolVariant ControlOnly。
3. PowerShell 参数默认也改为 ControlOnly，并允许 ControlOnly 作为合法值。
4. 继续使用低端口 29002，避免 hostaddr 端口符号扩展。
5. 保留 0x0261/0x025F 完整加载后再启动 session。
6. 保留 0x025D token echo，用于延时 UI。
7. 只发一次 game_start first-turn 0x0138；不再持续发送 fake 0x0138 type=2 turnstream。
8. ModRuntime 继续关闭，不 AddCha，不刷怪，不改 VIP/赞助。

测试目标：
- 验证没有连续 fake turnstream 时，frame:5 是否仍然触发。
- 看右上角延时/游戏时长是否开始显示。
- 看是否仍然收到 0x0265 退出。
