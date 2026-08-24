# =============================================
# AI Agent 实战手册 - 开发环境镜像
# 新手无需安装 Python 环境，一条命令跑通所有示例
# =============================================

FROM python:3.11-slim

# 设置工作目录
WORKDIR /workspace

# 安装系统依赖（用于编译部分包）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件（利用 Docker 缓存加速构建）
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 设置环境变量默认值（用户可通过 docker run -e 覆盖）
ENV OPENAI_API_KEY=""
ENV OPENAI_BASE_URL="https://api.openai.com/v1"

# 默认命令：进入交互式 shell
CMD ["bash"]
