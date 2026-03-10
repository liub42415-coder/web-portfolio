# 🤖 AI 编码约定 (AI Context) - Nuke 插件开发

> 💡 **CodeBuddy 指南**：在阅读和修改本项目代码时，请严格遵守以下规则：

1. **技术栈**：Python (Nuke 13+ 使用 Python 3, 旧版使用 Python 2), Nuke Python API (`import nuke`, `import nukescripts`), PySide2/PySide6 (用于自定义 UI)。
2. **代码风格**：
   - 遵循 PEP 8 规范。
   - 核心逻辑与 UI 绑定分离。
3. **架构规范**：
   - `init.py`：用于 Nuke 启动时非 GUI 相关的初始化（如添加插件路径 `nuke.pluginAddPath()`）。
   - `menu.py`：用于 Nuke 启动时 GUI 相关的初始化（如在顶部菜单栏或节点栏创建菜单项）。
   - 具体的插件逻辑应作为独立的 Python 模块存放在 `python/` 目录下，并在 `menu.py` 中被按需调用。
4. **特别提醒**：
   - 所有对 Nuke 节点图的修改必须在 Nuke 主线程中运行（或使用 `nuke.executeInMainThread`）。
   - 注意不要在 Nuke 启动期执行耗时操作，以免拖慢软件启动速度。