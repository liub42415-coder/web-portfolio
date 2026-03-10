# ⏱️ 工作状态断点 (Work In Progress)

> 💡 **使用说明**：每次离开电脑前，花 1 分钟更新此文件。换电脑打开 CodeBuddy 时，直接说：“阅读当前项目的 WIP.md，继续帮我干活。”

## 📅 更新时间：[插件开发完成]

### 🎯 当前目标 (Current Goal)
- [x] 开发辅助渲染面板插件 (Render Assistant)

### ✅ 已完成 (Done)
- [x] 创建 Nuke 插件项目文件夹 `Nuke_Plugin`
- [x] 编写核心逻辑 `python/render_assist.py`
  - 支持自定义帧范围输入
  - 支持完整渲染后额外导出首尾单帧图片
  - 支持倒放渲染 (TimeWarp 自动插入与清理)
  - 原始 `Write` 节点只作为渲染来源，不会被插件改写输出设置
  - 新增 `Video Output`：主渲染默认跟随原 `Write`，也可手动切换到其他视频格式
  - 新增 `Still Output`：仅控制首尾单帧图片导出格式
  - 新增 `Folder Mode` / `Custom Folder`：支持自动命名目录或手动自定义目录
  - 输出目录自动按帧范围命名，例如 `12-35`；倒放时为 `R12-35`
  - 默认输出文件名会附加本次渲染帧范围，例如 `R06G_V1-0802_10-15.mov`
  - 当未勾选首尾单帧导出时，`Still Output` 下拉框自动灰显禁用
  - 面板会记住上一次使用的选项，下次打开自动恢复



- [x] 修改 `init.py` 启用 `./python` 模块搜索路径
- [x] 修改 `menu.py` 注册菜单项 "Render Assistant" (Ctrl+Shift+R)


### ⏳ 下一步 / 待办 (Next Steps / TODO)
- [ ] 启动 Nuke 测试插件功能是否正常
- [ ] 收集用户反馈，进行细节优化

### 🔍 聚焦文件与报错线索 (Focus & Context)
- **当前聚焦**：插件功能验证
- **遗留报错**：暂无
