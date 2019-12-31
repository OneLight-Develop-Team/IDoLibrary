﻿# 工具说明
> Maya Houdini 灯光互导插件
\
# 插件原理
> 通过json的格式输出灯光信息

# 使用方法
## Maya 版本
> 将install.mel 扔进Maya的视窗，工具加上面会增加一个图标，点击图标即可使用

## Houdini 版本
> 请执行下面的 `Python` 代码,加载路径改为插件的路径。
```python
import sys
sys.path.append("C:\Users\liangwt\Desktop\MH_LightRebuild\Houdini_LightRebuild")
import Houdini_LightRebuild
reload(Houdini_LightRebuild)

ui = Houdini_LightRebuild.main()
```

## Todo
> + 添加CheckBox来控制输出的属性

---
---

# 更新记录
> 版本： ver 1.0.0
> 
> 更新时间： 2019-1-10
> 
> 制作者： 梁伟添
 
## ver 1.0.0 - 2019-1-10
> + 输出灯光信息
> + Maya 插件制作
> + Houdin 插件制作
