# 修复记录

多人坦克大战客户端「运行十几秒后越来越卡 / 一移动就变 PPT」，以及联机后白屏的问题排查与修复。

## 一、卡顿（越跑越卡，移动时掉到约 1fps）

根因是多个问题叠加，**不是 Tkinter 本身的性能问题**：

| # | 问题 | 文件 | 修复 |
|---|------|------|------|
| 1 | 热路径里有调试 `print`（发送/接收/帧延迟），全跑在主线程；IDE 控制台保留全部历史文本，越打越慢，移动时还会翻倍 → 单次 print 阻塞主线程几十毫秒 | `client_connector.py`、`client_win.py` | 删除 3 处 `print` |
| 2 | 主循环把「上一帧渲染耗时」直接当「下一帧延迟」，是个正反馈：一帧变慢→下一帧推后→追不回来→锁死在 1fps | `client_win.py` `_game` | 改为固定 30ms 间隔调度 |
| 3 | 线程间通信误用 `multiprocessing.Queue`（要 pickle + 管道 + 额外线程，抢 GIL），服务器端却用对了 `queue.Queue` | `client_connector.py` | 改成 `from queue import Queue` |
| 4 | 每帧都从磁盘重新加载字体 `ImageFont.truetype(...)` | `ClientDisplay.py` | 移到 `__init__` 只加载一次 |
| 5 | 游戏开始后 TCP 监听线程对已关闭/未连接的 socket 空转抢 GIL | `client_connector.py` | 加 `tcp_listening` 开关，非握手期休眠 |

> 已确认客户端跑在 IDE，所以 **#1（控制台被 print 刷爆）是这次卡顿的主因**，#2 是会把卡顿锁死的放大器。

## 二、联机后白屏（进了游戏页但画面全空）

| # | 问题 | 文件 | 修复 |
|---|------|------|------|
| 6 | 坦克出生点判断用了 `or`：`abs(x-bx)<2 or abs(y-by)<2`。地图 1396 个障碍物占满全部 98 列，任意随机点都被判定「太近」→ `while` 死循环 → 服务器卡死在 `game_init`，永远不发游戏帧 → 客户端白屏 | `GameCore.py` `game_init` | `or` 改 `and`（x、y 都贴近才算近）|
| 7 | `hp` 在安全区外会扣 `poison=0.01` 变成浮点，而打包按整型 `i`，约 10 秒安全区收缩后必触发 `struct.error` → 服务器停发帧 → 冻屏 | `GameCore.py` `refresh_output` | 打包前 `int(tank.hp)` 取整 |

> 实测：出生点用 `or` 跑 20 万次随机都找不到合法点（死循环），改 `and` 后 2 次即成功；400 帧含收缩/扣毒血/吃道具的模拟打包 0 失败。

## 三、环境/兼容性附带修复

| # | 问题 | 文件 | 修复 |
|---|------|------|------|
| 8 | UDP socket 从不 `bind`，Windows 上发首包前 `recvfrom` 直接抛 `WinError 10022` | `client_connector.py` | `__init__` 里 `udpsocket.bind(('', 0))` |
| 9 | socket 异常判断用 `e.errno != 10022`，但新版 Python 在 Windows 上把 WSA 码放在 `e.winerror`、`e.errno` 是映射后的 POSIX 值（22），判断失效 → 监听线程崩溃 | `client_connector.py` | 新增 `_is_benign_sockerr()`，同时认 `winerror` 和 `errno`，并容错 10054 等 |
| 10 | 服务器 IP 写死为局域网地址 | `client_connector.py` | 同机测试改为 `127.0.0.1` |

## 验证方式
1. 服务器：黑窗口 `python server_monitor.py` → 输入 `begin server`（改了 `GameCore` 后**必须重启服务器**）。
2. 客户端：IDE 里跑两个 `client_win.py`，各填不同正整数 ID → 登录 → 开始游戏（服务器需 2 人才开局）。
3. 进游戏后长按移动 1–2 分钟，确认画面正常且不再随时间卡顿。
