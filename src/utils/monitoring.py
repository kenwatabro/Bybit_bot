import psutil
import asyncio
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def monitor_system():
    while True:
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage("/").percent

        logger.info(
            f"System stats - CPU: {cpu_percent}%, Memory: {memory_percent}%, Disk: {disk_percent}%"
        )

        if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
            logger.warning("System resources are running low!")

        await asyncio.sleep(300)  # 5分ごとに監視
