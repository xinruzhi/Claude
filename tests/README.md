# 测试指南

本项目包含完整的单元测试和集成测试套件。

## 测试结构

```
tests/
├── conftest.py              # 测试 fixtures 和共享配置
├── unit/                    # 单元测试
│   ├── test_models.py       # 数据模型测试
│   ├── test_version_manager.py    # 版本管理器测试
│   ├── test_ats_optimizer.py      # ATS 优化器测试
│   ├── test_resume_parser.py      # 简历解析器测试
│   ├── test_template_generator.py # 模板生成器测试
│   ├── test_content_optimizer.py  # 内容优化器测试
│   └── test_job_matcher.py        # 职位匹配器测试
├── integration/              # 集成测试
│   └── test_api.py          # API 端点测试
└── README.md                # 本文档
```

## 运行测试

### 前置条件

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 运行所有测试

```bash
pytest
```

### 运行特定测试

```bash
# 只运行单元测试
pytest tests/unit/

# 只运行集成测试
pytest tests/integration/

# 运行特定测试文件
pytest tests/unit/test_models.py

# 运行特定测试类
pytest tests/unit/test_models.py::TestResume

# 运行特定测试方法
pytest tests/unit/test_models.py::TestResume::test_create_resume
```

### 显示详细输出

```bash
# 显示 print 输出
pytest -s

# 显示详细的测试信息
pytest -v

# 显示跳过的测试
pytest -rs
```

### 测试覆盖率

```bash
# 生成覆盖率报告
pytest --cov=backend --cov=api --cov=cli tests/

# 生成 HTML 覆盖率报告
pytest --cov=backend --cov=api --cov=cli --cov-report=html tests/
open htmlcov/index.html  # 查看报告
```

### 并行运行测试

```bash
# 使用 pytest-xdist 并行运行（需要先安装）
pip install pytest-xdist
pytest -n auto  # 使用所有可用 CPU 核心
```

## 测试标记

测试使用以下标记：

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.slow` - 慢速测试

可以使用标记过滤测试：

```bash
# 只运行单元测试
pytest -m unit

# 排除慢速测试
pytest -m "not slow"
```

## Fixtures

`conftest.py` 提供以下 fixtures：

- `sample_resume` - 完整的示例简历
- `minimal_resume` - 最简简历
- `sample_job_description` - 示例职位描述
- `temp_dir` - 临时目录
- `sample_markdown_resume` - Markdown 格式的简历示例

## 编写新测试

### 单元测试模板

```python
import pytest

class TestMyClass:
    def test_my_method(self, sample_resume):
        # 准备
        obj = MyClass()

        # 执行
        result = obj.my_method(sample_resume)

        # 断言
        assert result is not None
```

### API 测试模板

```python
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_api_endpoint():
    response = client.get("/api/endpoint")
    assert response.status_code == 200
```

## 常见问题

### 模块导入错误

确保项目根目录在 Python 路径中：

```bash
export PYTHONPATH=.
```

### 测试超时

某些测试可能需要更多时间，可以增加超时：

```bash
pytest --timeout=30
```

### Mock 外部依赖

使用 `unittest.mock` 来 mock 外部 API 调用：

```python
from unittest.mock import patch, Mock

@patch('module.ClassName')
def test_with_mock(mock_class):
    mock_instance = Mock()
    mock_instance.method.return_value = "mocked"
    mock_class.return_value = mock_instance
```
