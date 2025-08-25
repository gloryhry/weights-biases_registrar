import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.registration_service import RegistrationOrchestrator
from utils.logger import setup_logger

def main():
    """主程序入口"""
    logger = setup_logger('main')
    logger.info("Wandb.ai自动注册工具启动")
    
    # 创建注册协调器
    orchestrator = RegistrationOrchestrator()
    
    try:
        # 执行注册（使用非headless模式以便观察）
        success = orchestrator.execute_registration(headless=False)
        
        if success:
            logger.info("注册流程完成")
            print("注册成功！账户信息已保存到auth.txt")
        else:
            logger.error("注册流程失败")
            print("注册失败，请查看日志了解详细信息")
    except Exception as e:
        logger.error(f"程序执行过程中发生错误: {str(e)}")
        print(f"程序执行失败: {str(e)}")
    # 注意：不再需要在finally块中手动关闭浏览器，因为浏览器服务现在有更完善的资源管理

if __name__ == "__main__":
    main()