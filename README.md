# ai-journey

一个小白从零搭建 AI 系统的真实记录。

## Day 1 · 本地大模型
- 在 M2 Pro (32G) 上跑通 qwen3:14b，断网可用
- 踩坑：Ollama 官方源限速 400KB/s，换 ModelScope 镜像后 5–15MB/s

## Day 2 · 第一个 Function Calling
- 手写 get_weather 函数，让模型自己判断"要不要查、查哪个城市"
- 同一个问题，本地模型（qwen3:14b）调 1 次工具、耗时 30s+；
  云端模型（deepseek-chat）连调 2 次、3 秒出对比表格
- 结论：工具代码不变，模型越强行为越聪明——大脑和手脚是分开的
