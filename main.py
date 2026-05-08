"""
Lovina Bot - Main Entry Point
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN, BOT_NAME, BOT_VERSION

# Import middleware
from middleware.ban_check import BanCheckMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.stats_tracker import StatsTrackerMiddleware

# Import handlers
from handlers import start, admin, ai_handler, osint_handlers, analysis_handlers, network_handlers, research_mode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def set_default_commands(bot: Bot):
    """Set bot commands"""
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Show available commands"),
        BotCommand(command="ai", description="Chat with Lovina AI"),
        BotCommand(command="ip", description="IP geolocation lookup"),
        BotCommand(command="dns", description="DNS record lookup"),
        BotCommand(command="scan", description="Port scanner"),
        BotCommand(command="ssl", description="SSL certificate analysis"),
        BotCommand(command="hash", description="Generate hashes"),
        BotCommand(command="encode", description="Encode text"),
        BotCommand(command="jwt", description="Analyze JWT token"),
        BotCommand(command="research", description="Activate research mode"),
        BotCommand(command="about", description="About this bot"),
    ]
    
    await bot.set_my_commands(commands)
    logger.info("Bot commands set")

async def main():
    """Main bot function"""
    
    # Validate token
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TOKEN_HERE":
        logger.error("❌ BOT_TOKEN not configured in .env")
        return
    
    # Create bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Register middleware (order matters)
    dp.message.middleware(BanCheckMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(StatsTrackerMiddleware())
    
    # Register routers (handlers)
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(ai_handler.router)
    dp.include_router(osint_handlers.router)
    dp.include_router(analysis_handlers.router)
    dp.include_router(network_handlers.router)
    dp.include_router(research_mode.router)
    
    # Set default commands
    await set_default_commands(bot)
    
    # Get bot info
    bot_info = await bot.get_me()
    logger.info(f"""
╔════════════════════════════════════════╗
║       🌙 LOVINA BOT STARTING 🌙        ║
╠════════════════════════════════════════╣
║ Bot Name:    {bot_info.first_name:<20}║
║ Username:    @{bot_info.username:<18}║
║ Bot Version: {BOT_VERSION:<20}║
║ Status:      ONLINE ✅                 ║
╚════════════════════════════════════════╝
    """)
    
    try:
        logger.info("Starting polling...")
        await dp.start_polling(bot)
    
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
