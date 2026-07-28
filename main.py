"""
Lovina Bot - Main Entry Point
"""
import asyncio
import logging
import time
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, BOT_NAME, BOT_VERSION

# Import middleware
from middleware.ban_check import BanCheckMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.stats_tracker import StatsTrackerMiddleware

# Import handlers
from handlers import start, admin, ai_handler, osint_handlers, analysis_handlers, network_handlers, research_mode
from handlers.scraper_handlers import router as scraper_router
from handlers.tools_handlers import router as tools_router
from handlers.help_handler import router as help_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BOT_START_TIME = time.time()


async def set_default_commands(bot: Bot):
    """Set bot commands"""
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Show all commands by category"),
        BotCommand(command="commands", description="Quick command reference"),
        BotCommand(command="ai", description="Chat with Lovina AI"),
        BotCommand(command="scrape", description="Crawl and extract data from a website"),
        BotCommand(command="extract", description="Single-page AI extraction"),
        BotCommand(command="schemas", description="List extraction schemas"),
        BotCommand(command="portscan", description="Scan TCP ports on a host"),
        BotCommand(command="ping", description="Ping a host"),
        BotCommand(command="dns", description="DNS record lookup"),
        BotCommand(command="whois", description="WHOIS domain lookup"),
        BotCommand(command="ssl", description="Analyse SSL certificate"),
        BotCommand(command="headers", description="Security headers grade"),
        BotCommand(command="cors", description="CORS misconfiguration check"),
        BotCommand(command="techstack", description="Detect tech stack"),
        BotCommand(command="wayback", description="Wayback Machine lookup"),
        BotCommand(command="ip", description="IP geolocation lookup"),
        BotCommand(command="subdomain", description="Subdomain discovery"),
        BotCommand(command="username", description="Username hunt across platforms"),
        BotCommand(command="gitosint", description="GitHub profile OSINT"),
        BotCommand(command="emailcheck", description="Email validation and MX check"),
        BotCommand(command="hash", description="Generate multiple hash types"),
        BotCommand(command="encode", description="Encode text in various formats"),
        BotCommand(command="decode", description="Decode encoded text"),
        BotCommand(command="passgen", description="Generate secure password"),
        BotCommand(command="caesar", description="Caesar cipher"),
        BotCommand(command="rotbrute", description="Brute force ROT ciphers"),
        BotCommand(command="morse", description="Morse code encode and decode"),
        BotCommand(command="jwt", description="Decode and analyse JWT token"),
        BotCommand(command="owasp", description="OWASP Top 10 reference"),
        BotCommand(command="revshell", description="Generate reverse shell payload"),
        BotCommand(command="sqli", description="SQL injection payload library"),
        BotCommand(command="xss", description="XSS payload library"),
        BotCommand(command="lfi", description="LFI payload list"),
        BotCommand(command="ipcalc", description="Subnet calculator"),
        BotCommand(command="save", description="Save a value to personal store"),
        BotCommand(command="get", description="Retrieve a saved value"),
        BotCommand(command="note", description="Save an encrypted note"),
        BotCommand(command="tl", description="Investigation timeline"),
        BotCommand(command="scope", description="Manage engagement scope"),
        BotCommand(command="spiderjobs", description="View crawl job history"),
        BotCommand(command="spiderexport", description="Download crawl results"),
        BotCommand(command="research", description="Activate research mode"),
        BotCommand(command="status", description="Bot status and uptime"),
        BotCommand(command="clear", description="Clear AI conversation history"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    logger.info("Bot commands set")


async def main():
    """Main bot function"""
    from config import validate_config
    validate_config()

    # Validate token
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TOKEN_HERE":
        logger.error("❌ BOT_TOKEN not configured in .env")
        return

    # Create bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

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
    dp.include_router(scraper_router)
    dp.include_router(tools_router)
    dp.include_router(help_router)

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
