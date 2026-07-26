#啊昊你怎么这么

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

File System Access API 示例
--------------------------

如果你的项目在浏览器中需要比较两个文件/目录句柄是否指向相同项，建议使用原生方法 `isSameEntry`（更可靠）。仓库中包含示例脚本 `examples/fs_isSameEntry.js`：

- 它首先做特性检测并调用 `handleA.isSameEntry(handleB)`。
- 如果 API 不可用，示例提供了基于 `name` 和 `kind` 的退回比较，但这不是完全可靠的替代方法。

浏览器示例用法：

```
const [h1] = await window.showOpenFilePicker();
const [h2] = await window.showOpenFilePicker();
const same = await isSameHandle(h1, h2);
console.log('Same entry?', same);
```

Server / Node.js helper
-----------------------

For environments without native `FileSystemHandle` (Node.js), this repo
includes a pragmatic implementation that applies the same-entry semantics
using filesystem identity (stat dev+ino when available).

See `examples/fs_isSameEntry_node.js`. Example CLI usage:

```
node examples/fs_isSameEntry_node.js path/to/fileA path/to/fileB
```

The helper returns `true` when the underlying filesystem identifies the two
paths as the same inode (POSIX) or when resolved paths match as fallback.

