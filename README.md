# AitoResume - AI智能简历生成器

![AitoResume Logo](https://img.shields.io/badge/AitoResume-智能简历生成器-blue)

## 📝 项目简介

AitoResume是一个基于AI技术的在线简历生成系统，可以根据您粘贴的岗位描述自动生成针对性的简历内容。您只需提供基本个人信息和目标岗位描述，系统将自动优化简历内容，使其更符合招聘需求，提高面试机会。

## ✨ 主要功能

- **智能内容生成**：根据岗位描述自动生成匹配的简历内容
- **项目经验优化**：针对岗位要求自动优化您的项目经验描述
- **照片上传与裁剪**：支持上传个人照片并进行自定义裁剪
- **即时预览**：生成后可立即预览简历效果
- **简历下载**：将生成的简历保存为HTML格式，可用浏览器直接打印为PDF
- **多种AI模型支持**：支持在线API和本地Ollama模型
- **隐私保护**：关键个人信息仅在本地处理，支持使用本地Ollama模型实现完全隐私

## 🛠 安装指南

### 前提条件

- Python 3.7或更高版本
- 基本的命令行操作能力

### 步骤1：下载项目

**方法1：使用Git**

```bash
git clone https://github.com/buynonsense/AitoResume.git
cd AitoResume
```


**方法2：直接下载**

- 从发布页面下载最新版本
- 解压到本地文件夹
- 打开命令行，进入该文件夹

### 步骤2：创建虚拟环境（可选但推荐）

**Windows系统**:
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux系统**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 步骤3：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤4：配置API密钥

创建一个名为`.env`的文件在项目根目录下，内容如下：

```
# AI提供商: openai 或 ollama
AI_PROVIDER=openai

# OpenAI兼容API配置
AI_API_BASE=https://api.chatanywhere.tech
AI_API_KEY=sk-xxxxxxxxxxxxxxxx
AI_MODEL=gpt-4o-mini

# Ollama配置(如果使用Ollama)
# AI_MODEL=gemma3:12b

----------------------------------------------------

# AI提供商: openai 或 ollama
AI_PROVIDER=ollama

# OpenAI兼容API配置
# AI_API_BASE=https://api.chatanywhere.tech
# AI_API_KEY=sk-xxxxxxxxxxxxxxxx
# AI_MODEL=gpt-4o-mini

# Ollama配置(如果使用Ollama)
AI_MODEL=gemma3:12b
```

您需要使用自己的API密钥替换上述内容。如果没有API密钥，可以：
1. 注册OpenAI账号获取API密钥
2. 使用兼容OpenAI接口的其他服务提供商[推荐这个项目的免费次数API](https://github.com/chatanywhether/GPT_API_free)
3. 使用本地的Ollama模型（详见下方说明）
  
### 步骤5：配置个人信息

编辑`personal_info.yaml`文件，填入您的个人信息：


### 步骤6：启动应用

在cmd或终端中运行：
```bash
python app.py
```

启动后，您会看到类似以下内容：
```
 * Running on http://127.0.0.1:5000
```

### 步骤7：访问应用

打开浏览器，访问`http://127.0.0.1:5000`即可使用系统。

## 📖 使用指南

### 1. 生成简历

1. 打开应用后，您会看到简历生成界面
2. 可以选择上传个人照片（可选）
   - 上传照片后会自动弹出交互式裁剪窗口
   - 可拖动照片调整位置、缩放大小
   - 支持90°旋转照片以获得最佳角度
   - 预览窗口实时显示裁剪效果
   - 确认裁剪后照片自动嵌入到简历中
3. 在文本框中粘贴完整的岗位描述
4. 点击"生成简历"按钮
5. 等待10-30秒（取决于网络状况和AI模型响应时间）
6. 生成完成后，可以点击"预览简历"查看效果


### 2. 查看和下载简历

1. 点击"预览简历"按钮在新标签页中查看生成的简历
2. 点击"下载HTML"按钮下载简历文件
3. 生成的简历会自动保存在系统中

### 3. 将HTML转为PDF

1. 在浏览器中打开下载的HTML文件
2. 按下`Ctrl+P`(Windows/Linux)或`Command+P`(Mac)打开打印对话框
3. 选择"另存为PDF"选项
4. 设置纸张大小为A4，边距为"无"或"最小"
5. 点击保存，选择保存位置

## ❓ 常见问题

### 应用无法启动

**问题**: 运行`python app.py`后出现错误。

**解决方案**:
1. 确认已正确安装所有依赖：`pip install -r requirements.txt`
2. 检查Python版本是否为3.7或更高：`python --version`
3. 确保`.env`文件配置正确

### 生成简历失败

**问题**: 点击生成按钮后显示错误或长时间无响应。

**解决方案**:
1. 检查网络连接是否正常
2. 确认API密钥配置是否正确
3. API余额可能不足，请检查您的账户状态
4. 尝试减少岗位描述的长度，过长的文本可能导致API超时

### 照片无法正常裁剪

**问题**: 照片裁剪窗口无法操作或照片无法正常显示在简历中。

**解决方案**:
1. 确保照片格式为常见图片格式(JPG、PNG等)
2. 照片大小不应超过10MB
3. 尝试使用Chrome或Firefox等现代浏览器
4. 如无法拖动照片，可尝试刷新页面后重新上传

### 个人数据隐私与安全

**问题**: 系统如何处理我的个人信息？我的隐私是否安全？

**说明**:
1. AitoResume通过`personal_info.yaml`文件管理您的个人信息
2. **会发送给AI服务提供商的信息**:
   - 教育经历 (如学校名称、专业、学位、时间段)
   - 证书信息 (如证书名称、获取时间、分数)
   - 项目经验 (项目名称、时间段、描述等)
   
3. **不会发送给AI服务提供商的信息**:
   - 个人照片 (仅在本地处理，以Base64格式嵌入HTML)
   - 联系方式 (电话、邮箱)
   - 个人姓名和出生日期等标识信息
   
4. **增强隐私保护的方法**:
   - 使用Ollama本地模型 (所有数据完全在本地处理，不发送至任何外部服务)
   - 在`personal_info.yaml`文件中使用泛化描述 (如"某知名大学"代替具体校名)
   - 修改项目经验中的敏感信息 (如公司名称、项目名称等)

5. **注意**: 如果对隐私要求极高，强烈建议使用本地Ollama模型运行，这样所有处理都在您的设备上完成，不会有任何数据传输到外部。

## 📁 项目结构

```
AitoResume/
├── app.py                # Flask应用入口
├── resume_generator.py   # 简历生成核心代码
├── static/               # 静态资源
│   ├── css/              # 样式表
│   │   └── style.css
│   ├── js/               # JavaScript脚本
│   │   └── script.js
│   ├── uploads/          # 上传的照片临时存储位置
│   └── resumes/          # 生成的简历存储位置
├── templates/            # HTML模板
│   ├── index.html        # 主页面
│   └── resume_template.html  # 简历模板
├── personal_info.yaml    # 个人信息配置
├── .env                  # 环境变量配置
└── requirements.txt      # 依赖项列表
```

## AI提供商支持

AitoResume 支持两种 AI 提供商：

1. **OpenAI 兼容 API**：默认选项，适用于 OpenAI、Microsoft、Anthropic、SenseTime 等提供兼容 OpenAI 接口的服务商
2. **Ollama**：本地运行开源大语言模型，无需联网调用云端 API

### 配置 Ollama

1. 首先安装 [Ollama](https://ollama.ai)
2. 拉取所需模型：`ollama pull llama3`（或其他支持的模型，如`gemma:7b`、`mistral:7b`等）
3. 修改 .env 文件：
   ```
   AI_PROVIDER=ollama
   OLLAMA_HOST=http://localhost:11434
   AI_MODEL=llama3
   ```
4. 启动应用即可使用本地模型生成简历，所有数据处理都在本地完成，不会发送至外部服务器

## 🔄 更新和维护

要更新应用到最新版本：

1. 如果使用Git:
   ```bash
   git pull origin main
   pip install -r requirements.txt
   ```

2. 如果直接下载:
   - 下载最新版本
   - 保留您的`.env`和`personal_info.yaml`文件
   - 替换其他所有文件

## 💡 技术支持与贡献

如果您遇到任何问题或有改进建议，请:
- 提交Issue到项目GitHub页面
- 发送邮件至[support@example.com]

## 📜 开源协议

本项目采用MIT协议开源

---

祝您使用愉快！如果这个工具帮助您获得了心仪的工作机会，我们将感到非常高兴！