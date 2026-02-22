# APP 体验自动化 Agent（先落地 Android 真机）

你提的目标是：先做到 **可执行环境**，能够操作手机打开 APP，并进行截图和内容识别。

本仓库现在提供了一个最小可运行方案：
- 一个本地网页控制台（Python 标准库 HTTP 服务）
- 基于 `adb` 的真机控制
- 能执行：
  1. 查询设备
  2. 启动 APP（按包名）
  3. 截图
  4. 读取当前界面 UI 树并提取文本（作为“识别内容”）

> 说明：此阶段的“识别”优先用 UI 树文本（`uiautomator dump`），不依赖 OCR，稳定且易落地。

---

## 1. 环境准备（电脑端）

### 1.1 安装 Android Platform Tools（必须）
确保本机能运行：

```bash
adb version
```

若报错，请安装 Android Platform Tools 并把 `adb` 加入 PATH。

### 1.2 安装 Python 依赖
在项目根目录执行：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## 2. 真机连接（Android）

### 2.1 手机打开开发者选项
1. 设置 -> 关于手机 -> 连续点击版本号 7 次
2. 回到设置 -> 开发者选项 -> 打开“USB 调试”

### 2.2 USB 连接
1. 手机通过 USB 接电脑
2. 第一次连接会弹框“是否允许 USB 调试”，选择允许
3. 电脑执行：

```bash
adb devices
```

预期看到：

```text
List of devices attached
xxxxxxx	device
```

如果是 `unauthorized`：
- 重插 USB
- 手机上重新点允许

如果看不到设备：
- 更换数据线（很多线只能充电不能传输）
- Windows 安装对应厂商 USB 驱动

### 2.3 （可选）无线调试
USB 首次授权后，可切到 Wi-Fi：

```bash
adb tcpip 5555
adb connect 手机IP:5555
adb devices
```

---

## 3. 启动网页控制台

```bash
PYTHONPATH=src python -m ux_agent.web
```

打开浏览器访问：

```text
http://127.0.0.1:8000
```

页面中你可以直接：
1. 刷新设备列表
2. 输入设备序列号 + 包名，点击“打开 APP”
3. 对该设备执行“截图 + 文本识别”

截图会保存到 `artifacts/` 目录。

---

## 4. 命令行直调（不走网页）

### 4.1 启动 APP

```bash
adb -s <serial> shell monkey -p <package_name> -c android.intent.category.LAUNCHER 1
```

### 4.2 截图

```bash
adb -s <serial> exec-out screencap -p > artifacts/screen.png
```

### 4.3 提取当前页面可读文本（UI 树）

```bash
adb -s <serial> shell uiautomator dump /sdcard/uidump.xml
adb -s <serial> shell cat /sdcard/uidump.xml
```

---

## 5. 下一步（你要的“进一步复杂引擎”）

在当前可执行环境基础上，按这个顺序升级：
1. 把自然语言任务映射为多步动作（点击、滑动、返回、等待）
2. 增加 OCR（用于识别 UI 树拿不到的海报文案）
3. 规则配置化（JSON/YAML）支持业务维护
4. 接入 iOS（同样架构，执行层换 XCUITest/Appium）

---

## 6. 当前代码结构

- `src/ux_agent/web.py`：网页控制台
- `src/ux_agent/android_device.py`：adb 真机控制 + 截图 + UI 文本提取
- `src/ux_agent/rules.py`：体验规则引擎（上一阶段）
- `tests/test_android_device.py`：UI XML 文本提取测试
- `tests/test_rule_engine.py`：规则引擎测试
