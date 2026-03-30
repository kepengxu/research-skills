# research-skills

一个面向 Claude Code 的小型 research skill 仓库，当前主要用于科研图片生成与编辑。

## 当前内容

目前仓库中包含一个 skill：

- `research-figure-edit/`
  - `SKILL.md`：定义 Claude Code 如何调用这个 skill，包括模式选择、prompt 预处理、图类别识别、venue 风格预设，以及返回结果时应包含的信息。
  - `research_figure_edit.py`：后端 Python 命令行脚本，负责向远程图像生成 API 发起请求，并将生成图片或原始 JSON 响应保存到本地。

## 这个 skill 能做什么

`research-figure-edit` 支持两类工作流：

- `text2image`：仅基于文本 prompt 生成科研/论文风格图片
- `image2image`：基于文本 prompt 和本地输入图片生成新的图片

后端脚本负责：
- 校验命令行参数
- 从环境变量读取 API 配置
- 在 `image2image` 模式下对本地图片做 base64 编码
- 调用远程模型接口
- 从响应中提取 inline image 数据
- 保存生成图片，以及可选保存原始 JSON 响应

## 运行要求

- Python 3
- 已配置可用的 API 认证环境变量

该脚本只依赖 Python 标准库。

## 环境变量

认证相关：
- `NANOBANANA_API_KEY`
- `NANOBANANA_BEARER_TOKEN`

两者至少设置一个，否则脚本会报错。

可选覆盖项：
- `NANOBANANA_HOST`：默认值为 `api.vectorengine.ai`
- `NANOBANANA_MODEL`：默认值为 `gemini-3-pro-image-preview`

## 使用方法

### 查看命令行帮助

```bash
python research-figure-edit/research_figure_edit.py --help
```

### 文生图

```bash
python research-figure-edit/research_figure_edit.py \
  --mode text2image \
  --prompt "A clean paper-ready workflow figure for multimodal reasoning" \
  --output-dir outputs/research-figure-edit \
  --save-raw-response
```

### 图生图

```bash
python research-figure-edit/research_figure_edit.py \
  --mode image2image \
  --prompt "Preserve the structure and convert this into a clean Nature-style scientific figure" \
  --input path/to/input.png \
  --output-dir outputs/research-figure-edit \
  --save-raw-response
```

### 本地快速语法检查

```bash
python -m py_compile research-figure-edit/research_figure_edit.py
```

## 说明

- 支持的输入图片类型：PNG、JPG、JPEG
- `--clarity` 仅适用于 `text2image`
- 如果 API 没有返回 inline image，脚本仍可保存原始 JSON 响应，便于排查问题
- 更丰富的 prompt 工程逻辑主要写在 `research-figure-edit/SKILL.md` 中；Python 脚本本身主要负责请求执行和文件输出

## 当前仓库状态

当前仓库还没有：
- 测试套件
- lint / format 配置
- `pyproject.toml`、`requirements.txt` 这类包管理清单
