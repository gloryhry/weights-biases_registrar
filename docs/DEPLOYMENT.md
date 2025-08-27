# 多环境部署指南

## 本地环境部署

### Windows 系统

#### 方案1：Docker部署（推荐）

1. **安装Docker Desktop**
    ```bash
    # 确保已安装Docker Desktop
    docker --version
    ```

2. **构建镜像**
    ```bash
    # 项目根目录执行
    docker build -t wandb-registrar .
    ```

3. **运行容器**
    ```bash
    # 直接运行
    docker run -v $(pwd)/output:/app/output wandb-registrar

    # 或使用环境变量
    docker run -e REGISTRATION_COUNT=5 -v $(pwd)/output:/app/output wandb-registrar
    ```

#### 方案2：WSL2部署

1. **启用WSL2**
    ```powershell
    # 管理员PowerShell
    wsl --install
    ```

2. **在WSL2中运行**
    ```bash
    # 切换到Linux环境
    wsl
    cd /mnt/c/path/to/wandb-registrar
    ./run.sh
    ```

### Linux 系统

#### Ubuntu/Debian

1. **安装依赖**
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip xvfb
    ```

2. **安装并使用**
    ```bash
    chmod +x run.sh
    ./run.sh
    ```

#### CentOS/RHEL

1. **安装依赖**
    ```bash
    sudo yum install python3 python3-pip xorg-x11-server-Xvfb
    yum install -y xorg-x11-server-Xvfb
    ```

## 云服务部署

### AWS EC2

```bash
# 启动EC2实例（Amazon Linux 2）
ssh -i your-key.pem ec2-user@your-instance-ip

# 安装依赖
sudo yum update -y
sudo yum install git python3 python3-pip -y

# 克隆并运行
git clone <repo-url>
cd wandb-registrar
./run.sh
```

### 阿里云ECS

```bash
# 使用CentOS镜像
sudo yum install epel-release -y
sudo yum install git python3 xorg-x11-server-Xvfb -y

# 安装后运行
git clone <repo-url>
cd wandb-registrar
./run.sh
```

## Docker Compose配置

创建 `docker-compose.yml`：

```yaml
version: '3.8'
services:
  wandb-registrar:
    build: .
    environment:
      - REGISTRATION_COUNT=1
      - HEADLESS_MODE=true
    volumes:
      - ./output:/app/output
    restart: unless-stopped
```

## 健康监控

### 监控脚本

创建 `monitor.py`：

```python
import subprocess
import json
import os
from datetime import datetime

def check_service_health():
    """检查服务健康状态"""
    try:
        # 检查日志文件
        if os.path.exists('logs/app.log'):
            with open('logs/app.log', 'r') as f:
                last_line = f.readlines()[-1]
                
        # 检查必需文件
        required_files = ['requirements.txt', 'run.sh', 'main.py']
        for file in required_files:
            if not os.path.exists(file):
                return False, f"Missing {file}"
                
        return True, "Service healthy"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    healthy, message = check_service_health()
    status = {
        'timestamp': datetime.now().isoformat(),
        'healthy': healthy,
        'message': message
    }
    print(json.dumps(status, indent=2))
```

## 日志管理

### 使用systemd（Linux）

创建 `/etc/systemd/system/wandb-registrar.service`：

```ini
[Unit]
Description=Wandb.ai Registration Tool
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/opt/wandb-registrar
ExecStart=/opt/wandb-registrar/run.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable wandb-registrar
sudo systemctl start wandb-registrar
```

### Windows服务

使用nssm创建Windows服务：

```powershell
# 下载nssm
wget https://nssm.cc/release/nssm-2.24.zip

# 创建服务
nssm install WandbRegistrar "C:\Python38\python.exe" "C:\app\wandb-registrar\main.py"
nssm set WandbRegistrar Description "Automated wandb.ai registration service"
nssm start WandbRegistrar
```