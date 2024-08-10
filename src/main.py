from dotenv import load_dotenv
load_dotenv()

import asyncio
import signal
import time
import os
import sys
from src.api.bybit_api import BybitAPI
from src.strategies.rsi_bollinger_strategy import RSIBollingerStrategy
from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader
from src.utils.monitoring import monitor_system

def restart_program(logger):
    logger.info("Restarting the program...")
    time.sleep(5)
    os.execv(sys.executable, ['python'] + sys.argv)

async def main():
    logger = setup_logger()
    config_loader = ConfigLoader()

    # シャットダウンフラグ
    shutdown = asyncio.Event()

    async def shutdown_handler(sig, loop):
        logger.info(f"Received exit signal {sig.name}...")
        shutdown.set()

    # シグナルハンドラの設定
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown_handler(s, loop)))

    start_time = time.time()
    restart_interval = 24 * 60 * 60  # 24時間ごとに再起動

    monitoring_task = asyncio.create_task(monitor_system())

    while not shutdown.is_set():
        if time.time() - start_time > restart_interval:
            restart_program(logger)
        try:
            config = config_loader.load_config()
            secrets = config_loader.load_secrets()

            api = BybitAPI(secrets['bybit']['api_key'], secrets['bybit']['api_secret'])
            strategy = RSIBollingerStrategy(api, config['trading'])

            await strategy.execute()
            await asyncio.sleep(config['trading']['interval_seconds'])
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            await asyncio.sleep(60)  # エラー後の待機時間
        finally:
            # リソースのクリーンアップ
            if 'api' in locals():
                await api.close_session()

    logger.info("Shutting down gracefully...")

if __name__ == "__main__":
    asyncio.run(main())