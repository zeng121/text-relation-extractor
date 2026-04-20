# 文本关系图谱生成器 MVP

一个很轻量的全栈玩具项目：输入一段文本，后端提取人物/组织/项目及其关系，前端用 Cytoscape.js 把它画出来。

## 目录结构

```text
text-graph-mvp/
├── backend/
│   ├── main.py
│   ├── extractor.py
│   ├── schemas.py
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── .gitignore
└── README.md
```

## 运行方式

### 1. 启动后端（uv）

```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

后端地址：
- http://127.0.0.1:8000
- 文档：http://127.0.0.1:8000/docs

### 2. 启动前端

```bash
cd frontend
python -m http.server 5500
```

然后打开：
- http://127.0.0.1:5500

## Git 初始化

```bash
git init
git add .
git commit -m "Initial commit"
```

## 依赖管理

这个项目的 Python 后端现在只用 `uv` 管理依赖，不再维护 `requirements.txt`。

## 已完成的升级

1. 节点点击详情面板
2. 时间线事件展示
3. 前端示例文本切换
4. 更丰富一点的规则抽取（就职于 / 同事 / 参与 / 负责）
5. 后端优先走 OpenAI 兼容 LLM 抽取，失败时自动回退到规则抽取

## 抽取策略

- 默认优先调用可用的 OpenAI 兼容接口（按环境变量优先级自动选择）
- 当前后端支持的环境变量来源包括：`OPENAI_API_KEY`、`OPENROUTER_API_KEY`、`GEMINI_API_KEY` / `GOOGLE_API_KEY`、`GLM_API_KEY`、`KIMI_API_KEY`、`MINIMAX_API_KEY`、`OPENCODE_ZEN_API_KEY`、`OPENCODE_GO_API_KEY`、`HF_TOKEN`
- LLM 返回必须是结构化 JSON，后端会校验节点/边/时间线引用是否合法
- 如果 LLM 调用失败、返回非法 JSON，或者没有抽出有效节点，会自动回退到本地规则抽取
- 响应里的 `extraction_mode` 会标记当前结果来自 `llm`、`rules` 或默认 `fallback`

## 下一步可以怎么升级

1. 支持在前端显示当前 `extraction_mode` 和错误提示
2. 支持群组视图 / 按组织或项目聚类
3. 支持上传 txt / md 文件
4. 给时间线增加节点高亮联动
5. 增加导出 JSON / PNG 图谱
