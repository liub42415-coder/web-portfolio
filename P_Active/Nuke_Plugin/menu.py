import nuke
import render_assist

# 这里用于 Nuke 启动时的 GUI 相关初始化配置
# 例如：在顶部菜单栏、节点工具栏中添加自定义菜单和按钮

def setup_menu():
    # 示例：在顶部菜单栏添加一个名为 "MyCustomPlugin" 的菜单
    custom_menu = nuke.menu("Nuke").addMenu("MyCustomPlugin")
    
    # 添加 Render Assistant 菜单项
    custom_menu.addCommand("Render Assistant", "render_assist.show_dialog()", "Ctrl+Shift+R")

setup_menu()
nuke.tprint("Nuke Plugin: menu.py loaded successfully.")
