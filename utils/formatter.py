"""
Output formatter for clean Telegram messages
"""
from typing import Dict, List

class Formatter:
    """Format tool outputs for Telegram"""
    
    @staticmethod
    def section_header(emoji: str, title: str, target: str = "") -> str:
        """Create header for section"""
        if target:
            return f"{emoji} <b>{title}</b> — {target}\n{'─' * 40}"
        return f"{emoji} <b>{title}</b>\n{'─' * 40}"
    
    @staticmethod
    def section_divider() -> str:
        """Divider line"""
        return "─" * 40
    
    @staticmethod
    def format_key_value(key: str, value: str) -> str:
        """Format key-value pair"""
        return f"<b>{key}</b> : {value}"
    
    @staticmethod
    def format_list_item(emoji: str, text: str, status: str = "") -> str:
        """Format list item"""
        if status:
            return f"{emoji} {text} <code>{status}</code>"
        return f"{emoji} {text}"
    
    @staticmethod
    def format_result(data: Dict) -> str:
        """Format result dictionary"""
        result = ""
        for key, value in data.items():
            result += f"<b>{key}</b>: {value}\n"
        return result
    
    @staticmethod
    def truncate(text: str, max_length: int = 4000) -> List[str]:
        """Split long text into multiple messages (Telegram limit: 4000 chars)"""
        if len(text) <= max_length:
            return [text]
        
        messages = []
        while text:
            if len(text) <= max_length:
                messages.append(text)
                break
            
            # Find last newline before limit
            chunk = text[:max_length]
            last_newline = chunk.rfind('\n')
            
            if last_newline > 0:
                messages.append(text[:last_newline])
                text = text[last_newline+1:]
            else:
                messages.append(chunk)
                text = text[max_length:]
        
        return messages
    
    @staticmethod
    def format_ip_result(ip: str, location: str, asn: str, isp: str, timezone: str, coords: str, hostname: str = "") -> str:
        """Format IP lookup result"""
        result = Formatter.section_header("🌐", "IP INTELLIGENCE", ip)
        result += f"\n{Formatter.format_key_value('📍 Location', location)}"
        result += f"\n{Formatter.format_key_value('🏢 ASN', asn)}"
        result += f"\n{Formatter.format_key_value('🔌 ISP', isp)}"
        result += f"\n{Formatter.format_key_value('🌍 Timezone', timezone)}"
        result += f"\n{Formatter.format_key_value('📊 Coordinates', coords)}"
        
        if hostname:
            result += f"\n{Formatter.format_key_value('🖥️ Hostname', hostname)}"
        
        result += f"\n\n{Formatter.section_divider()}\n"
        result += "⚠️ <i>For educational and authorised use only</i>"
        
        return result
    
    @staticmethod
    def format_dns_result(domain: str, records: Dict) -> str:
        """Format DNS lookup result"""
        result = Formatter.section_header("🔍", "DNS RECORDS", domain)
        
        for record_type, values in records.items():
            result += f"\n<b>{record_type}</b>:\n"
            for value in values:
                result += f"  • <code>{value}</code>\n"
        
        result += f"\n{Formatter.section_divider()}\n"
        result += "⚠️ <i>For educational and authorised use only</i>"
        
        return result
    
    @staticmethod
    def format_hash_result(text: str, hashes: Dict) -> str:
        """Format hash generation result"""
        result = Formatter.section_header("🔐", "HASH GENERATION")
        result += f"\n<b>Input:</b> <code>{text}</code>\n"
        result += f"{Formatter.section_divider()}\n"
        
        for hash_type, hash_value in hashes.items():
            result += f"\n<b>{hash_type}</b>:\n<code>{hash_value}</code>"
        
        result += f"\n\n{Formatter.section_divider()}\n"
        result += "⚠️ <i>For educational and authorised use only</i>"
        
        return result
    
    @staticmethod
    def error_message(error: str) -> str:
        """Format error message"""
        return f"❌ <b>Error</b>\n\n<i>{error}</i>"
    
    @staticmethod
    def info_message(title: str, text: str) -> str:
        """Format info message"""
        return f"ℹ️ <b>{title}</b>\n\n{text}"
    
    @staticmethod
    def loading_message(action: str, target: str = "") -> str:
        """Loading message"""
        if target:
            return f"🔍 {action} <b>{target}</b>..."
        return f"🔍 {action}..."
