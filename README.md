# Resume Optimizer - 智能简历优化系统

基于 Python + LangChain 的智能简历优化系统，使用 Claude AI 提供专业的简历优化服务。

## 功能特性

- 📄 **多格式简历解析** - 支持 PDF、DOCX、Markdown、TXT 格式
- ✨ **AI 内容优化** - 基于 Claude 的智能内容润色和关键词优化
- 🎯 **职位匹配分析** - 分析简历与职位的匹配度，提供改进建议
- 📝 **多版本管理** - 管理简历的多个版本，追踪变更历史
- 🎨 **美观模板** - 提供 Modern、Classic、Minimalist 三种风格模板
- 📤 **多格式导出** - 支持导出为 PDF、Markdown 格式
- 🌐 **Web 界面** - 友好的图形化界面
- 💻 **命令行工具** - 强大的 CLI 工具
- 🔌 **RESTful API** - 完整的 API 服务

## 技术栈

**后端**
- Python 3.11+
- FastAPI - Web API 框架
- LangChain - LLM 应用开发框架
- Claude API - AI 大语言模型
- Typer - 命令行工具
- Pydantic - 数据验证

**前端**
- React + TypeScript
- Tailwind CSS
- shadcn/ui

## 快速开始

### 1. 环境配置

```bash
# 克隆项目
git clone https://github.com/xinruzhi/Claude.git
cd Claude

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 ANTHROPIC_API_KEY
```

### 2. 获取 API Key

访问 [Anthropic Console](https://console.anthropic.com/) 获取 API Key。

### 3. 运行方式

#### API 服务

```bash
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档。

#### 命令行工具

```bash
# 解析简历
python -m cli.main parse resume.pdf

# 优化简历
python -m cli.main optimize <resume_id> --role "软件工程师"

# 匹配职位
python -m cli.main match <resume_id> job_description.txt

# 导出简历
python -m cli.main export <resume_id> --style modern --format pdf
```

## 项目结构

```
resume-optimizer/
├── backend/                    # 后端核心服务
│   ├── agents/                # LangChain 智能体
│   │   ├── content_optimizer.py    # 内容优化智能体
│   │   ├── job_matcher.py          # 职位匹配智能体
│   │   └── template_generator.py   # 模板生成智能体
│   ├── core/                  # 核心业务逻辑
│   │   ├── resume_parser.py        # 简历解析器
│   │   └── version_manager.py      # 版本管理器
│   ├── models/                # 数据模型
│   │   ├── resume.py               # 简历数据模型
│   │   └── job_description.py      # 职位描述模型
│   ├── templates/             # 简历模板
│   └── utils/                 # 工具函数
├── api/                       # API 服务层
│   ├── app.py                 # FastAPI 应用
│   └── routes/                # API 路由
├── cli/                       # 命令行工具
│   └── main.py
├── web/                       # Web 前端
├── config/                    # 配置文件
├── tests/                     # 测试
├── requirements.txt
└── README.md
```

## 使用示例

### 作为 API 使用

```python
import requests

# 上传简历
with open('resume.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/api/resume/upload', files=files)
    resume_id = response.json()['resume_id']

# 优化简历
response = requests.post(
    f'http://localhost:8000/api/optimize/{resume_id}',
    data={'target_role': '软件工程师'}
)

# 下载优化后的简历
response = requests.get(
    f'http://localhost:8000/api/resume/{resume_id}/download',
    params={'style': 'modern', 'format': 'pdf'}
)
```

### 作为库使用

```python
from backend.core.resume_parser import ResumeParser
from backend.agents.content_optimizer import ContentOptimizer
from backend.utils.pdf_generator import PDFGenerator

# 解析简历
parser = ResumeParser()
resume = parser.parse_file('resume.pdf')

# 优化简历
optimizer = ContentOptimizer()
result = optimizer.optimize_resume(resume, target_role="软件工程师")

# 导出 PDF
pdf_generator = PDFGenerator()
pdf_generator.generate_pdf(result.optimized_resume, 'output.pdf', style='modern')
```

## 开发指南

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black .
ruff check --fix
```

## License

MIT License
