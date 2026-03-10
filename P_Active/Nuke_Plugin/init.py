import nuke

# 这里用于 Nuke 启动时的非 GUI 初始化配置
# 例如：添加自定义的 Python 模块路径、Gizmo 路径等
nuke.pluginAddPath('./python')
# nuke.pluginAddPath('./gizmos')
# nuke.pluginAddPath('./icons')

nuke.tprint("Nuke Plugin: init.py loaded successfully.")
