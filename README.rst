Lumache 项目说明
=================

这个仓库是一个基于 Python 的示例项目，用来演示如何创建一个
简单的 Python 库，并配套 Sphinx 文档站点。

项目包含以下内容：

- 一个名为 ``lumache`` 的示例模块
- 简单的 API 说明和使用示例
- 可直接部署到 Read the Docs 的文档结构

如果你想了解更多，可以查看文档目录中的说明内容。

Example: Read the Docs API
-------------------------

Do NOT hardcode API tokens in code. See `examples/readthedocs_fetch.py` for a
minimal example that reads the `READTHEDOCS_TOKEN` environment variable and
performs a safe request to the Read the Docs API.

Run:

```
export READTHEDOCS_TOKEN="<your-token>"
python examples/readthedocs_fetch.py
```
