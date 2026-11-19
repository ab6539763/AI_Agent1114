# 星辰智脑 70 天课程与企业级 Agent 平台 Makefile
PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest
UVICORN := .venv/bin/uvicorn

.PHONY: help test test-platform test-versions test-notebooks verify run clean

help:
	@echo "星辰智脑 (StarMind) 70天实战课程与企业级 Agent 平台"
	@echo "  make run             - 启动企业级 Agent 平台 (http://127.0.0.1:8000)"
	@echo "  make test-platform   - 运行企业级平台全链路单元测试"
	@echo "  make test-versions   - 运行 70 天所有版本迭代验证测试"
	@echo "  make test-notebooks  - 校验 70 天 Jupyter Notebook 结构与可执行性"
	@echo "  make verify          - 运行全量质量审计(字数、代码行数、测试、接口)"

run:
	$(UVICORN) starmind_platform.app.main:app --host 0.0.0.0 --port 8000 --reload

test-platform:
	$(PYTEST) starmind_platform/tests -v

test-versions:
	$(PYTHON) scripts/verify_all.py --check-versions

test-notebooks:
	$(PYTHON) scripts/verify_all.py --check-notebooks

verify:
	$(PYTHON) scripts/verify_all.py --all

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
