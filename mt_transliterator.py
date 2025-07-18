import logging
import os
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, InlineQueryHandler
from telegram.constants import ParseMode
import uuid
from dotenv import load_dotenv
import asyncio

# Load environment variables first
load_dotenv()

# Set up logging with less verbose output
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING  # Changed from INFO to WARNING to reduce log noise
)
logger = logging.getLogger(__name__)

# Pre-compiled transliteration map for faster lookup
AMHARIC_MAP = {
    # ሀ Series
    "ሀ": "ha", "ሁ": "hu", "ሂ": "hee", "ሃ": "ha", "ሄ": "hay","ህ": "hi", "ሆ": "ho",
    # ለ Series
    "ለ": "le", "ሉ": "lu", "ሊ": "lee", "ላ": "la", "ሌ": "lay","ል": "li", "ሎ": "lo",
    # ሐ Series (hammeru ha)
    "ሐ": "ḥa", "ሑ": "ḥu","ሒ": "ḥee","ሓ": "ḥa","ሔ": "ḥay","ሕ": "ḥi","ሖ": "ḥo","ሗ": "ḥwa",
    # መ Series
    "መ": "me", "ሙ": "mu", "ሚ": "mi", "ማ": "ma", "ሜ": "may","ም": "mi", "ሞ": "mo",
    # ሠ Series
    "ሠ": "se", "ሡ": "su", "ሢ": "si", "ሣ": "sa", "ሤ": "say","ሥ": "si", "ሦ": "so",
    # ረ Series (r)
    "ረ": "re", "ሩ": "ru", "ሪ": "ree", "ራ": "ra", "ሬ": "ray","ር": "ri", "ሮ": "ro",
    # ሰ Series (s)
    "ሰ": "se", "ሱ": "su", "ሲ": "see", "ሳ": "sa", "ሴ": "say","ስ": "si", "ሶ": "so", "ሷ": "swa",
    # ሸ Series (sh)
    "ሸ": "she", "ሹ": "shu", "ሺ": "shee", "ሻ": "sha", "ሼ": "shay","ሽ": "shih", "ሾ": "sho", "ሿ": "shwa",
    # ቀ Series
    "ቀ": "q'e", "ቁ": "q'u", "ቂ": "q'i", "ቃ": "q'a", "ቄ": "q'ay","ቅ": "q'", "ቆ": "q'o",
    # በ Series
    "በ": "be", "ቡ": "bu", "ቢ": "bi", "ባ": "ba", "ቤ": "bay","ብ": "bi", "ቦ": "bo",
    # ቨ Series
    "ቨ": "ve", "ቩ": "vu", "ቪ": "vee", "ቫ": "va", "ቬ": "vay","ቭ": "vi", "ቮ": "vo",
    # ተ Series
    "ተ": "te", "ቱ": "tu", "ቲ": "tee", "ታ": "ta", "ቴ": "tay","ት": "ti", "ቶ": "to",
    # ቸ Series
    "ቸ": "che", "ቹ": "chu", "ቺ": "chee", "ቻ": "cha", "ቼ": "chay","ች": "chi", "ቾ": "cho",
    # ኀ/Virgin ሀ (same as ሀ series by site)
    "ኀ": "ha", "ኁ": "hu", "ኂ": "hee", "ኃ": "ha", "ኄ": "hay","ኅ": "hi", "ኆ": "ho",
    # ነ Series
    "ነ": "ne", "ኑ": "nu", "ኒ": "ni", "ና": "na", "ኔ": "nay","ን": "ni", "ኖ": "no",
    # ኘ Series
    "ኘ": "ñe", "ኙ": "ñu", "ኚ": "ñee", "ኛ": "ña", "ኜ": "ñay","ኝ": "ñi", "ኞ": "ño",
    # Vowels (independent)
    "አ": "a", "ኡ": "u", "ኢ": "ee", "ኣ": "a", "ኤ": "ay","እ": "i", "ኦ": "o",
    # ከ Series
    "ከ": "ke", "ኩ": "ku", "ኪ": "ki", "ካ": "ka", "ኬ": "kay","ክ": "ki", "ኮ": "ko",
    # ኸ Series (H')
    "ኸ": "he", "ኹ": "hu", "ኺ": "hee", "ኻ": "ha", "ኼ": "hay","ኽ": "hi", "ኾ": "ho",
    # ወ Series
    "ወ": "we", "ዉ": "wu", "ዊ": "wee", "ዋ": "wa", "ዌ": "way","ው": "wi", "ዎ": "wo",
    # ዐ Series (glottal)
    "ዐ": "a", "ዑ": "u", "ዒ": "ee", "ዓ": "a", "ዔ": "ay","ዕ": "i", "ዖ": "o",
    # ዘ Series
    "ዘ": "ze", "ዙ": "zu", "ዚ": "zi", "ዛ": "za", "ዜ": "zay","ዝ": "zi", "ዞ": "zo",
    # ዠ Series
    "ዠ": "zje", "ዡ": "zju", "ዢ": "zji", "ዣ": "zja", "ዤ": "zjay","ዥ": "zji", "ዦ": "zjo",
    # የ Series
    "የ": "ye", "ዩ": "yu", "ዪ": "yee", "ያ": "ya", "ዬ": "yay","ይ": "yi", "ዮ": "yo",
    # ደ Series
    "ደ": "de", "ዱ": "du", "ዲ": "dee", "ዳ": "da", "ዴ": "day","ድ": "di", "ዶ": "do",
    # ጀ Series
    "ጀ": "je", "ጁ": "ju", "ጂ": "ji", "ጃ": "ja", "ጄ": "jay","ጅ": "ji", "ጆ": "jo",
    # ገ Series
    "ገ": "ge", "ጉ": "gu", "ጊ": "gee", "ጋ": "ga", "ጌ": "gay","ግ": "gi", "ጎ": "go",
    # ጠ Series (T')
    "ጠ": "t'e", "ጡ": "t'u", "ጢ": "t'ee", "ጣ": "t'a", "ጤ": "t'ay","ጥ": "t'i", "ጦ": "t'o",
    # ጨ Series (Ch')
    "ጨ": "ch'e", "ጩ": "ch'u", "ጪ": "ch'ee", "ጫ": "ch'a", "ጬ": "ch'ay","ጭ": "chi'", "ጮ": "ch'o",
    # ጰ Series (P')
    "ጰ": "p'e", "ጱ": "p'u", "ጲ": "p'ee", "ጳ": "p'a", "ጴ": "p'ay","ጵ": "p'i", "ጶ": "p'o",
    # ጸ Series
    "ጸ": "tse", "ጹ": "tsu", "ጺ": "tsee", "ጻ": "tsa", "ጼ": "tsay","ጽ": "tsi", "ጾ": "tso",
    # ፀ Series
    "ፀ": "tse", "ፁ": "tsu", "ፂ": "tsee", "ፃ": "tsa", "ፄ": "tsay","ፅ": "tsi", "ፆ": "tso",
    # ፈ Series
    "ፈ": "fe", "ፉ": "fu", "ፊ": "fee", "ፋ": "fa", "ፌ": "fay","ፍ": "fi", "ፎ": "fo",
    # ፐ Series
    "ፐ": "pe", "ፑ": "pu", "ፒ": "pee", "ፓ": "pa", "ፔ": "pay","ፕ": "pi", "ፖ": "po",
    # Specials - Added proper newline handling
    "።": ".", "፣": ",", "፤": ";", "፥": ":", "፦": ":", " ": " ", "\n": "\n", "\r": "\n", "\r\n": "\n",
    # W-series additions
    "ዷ": "dwa", "ቧ": "bwa", "ጧ": "t'wa",
}

# Pre-compiled consonant patterns for faster processing
CONSONANT_PATTERNS = {
    'mgb': 'migib',   # ምግብ
    'lj': 'lij',      # ልጅ
}

def transliterate_amharic(amharic_text):
    """Optimized transliteration function using pre-compiled maps."""
    # Use list comprehension for faster processing
    transliterated = ''.join(AMHARIC_MAP.get(char, char) for char in amharic_text)
    
    # Apply post-processing rules
    return apply_post_processing_rules(transliterated)

def apply_post_processing_rules(text):
    """Apply various post-processing rules to improve transliteration quality."""
    # Apply rules in sequence for better performance
    text = apply_final_i_rule(text)
    text = insert_vowels_in_clusters(text)
    return text

def apply_final_i_rule(text):
    """Remove final 'i' from words longer than 2 characters that end in 'i'."""
    words = text.split()
    processed_words = []
    
    for word in words:
        punctuation = ""
        clean_word = word
        
        # Check for punctuation at the end
        if word and word[-1] in ".,;:!?":
            punctuation = word[-1]
            clean_word = word[:-1]
        
        # Remove final 'i' if word is longer than 2 characters
        if len(clean_word) > 2 and clean_word.endswith('i'):
            clean_word = clean_word[:-1]
        
        processed_words.append(clean_word + punctuation)
    
    return ' '.join(processed_words)

def insert_vowels_in_clusters(text):
    """Insert vowels in consonant clusters based on user preferences."""
    words = text.split()
    processed_words = []
    
    for word in words:
        punctuation = ""
        clean_word = word
        
        # Check for punctuation at the end
        if word and word[-1] in ".,;:!?":
            punctuation = word[-1]
            clean_word = word[:-1]
        
        # Apply consonant pattern replacements
        for pattern, replacement in CONSONANT_PATTERNS.items():
            clean_word = clean_word.replace(pattern, replacement)
        
        processed_words.append(clean_word + punctuation)
    
    return ' '.join(processed_words)

# Bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = """
🇪🇹 *Welcome to Amharic Transliterator Bot!* 🇪🇹

I can help you transliterate Amharic text to Latin script.

*How to use:*
• Send me any Amharic text and I'll transliterate it
• Use inline mode: type `@yourbotname` followed by Amharic text in any chat
• Send /help for more information

*Example:*
Send: `ሰላም`
Get: `selam`

Send: `ልጅ`
Get: `lij`

Try it now! Send me some Amharic text 👇
    """
    await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
🔤 *Amharic Transliterator Bot Help*

*Commands:*
• `/start` - Start the bot
• `/help` - Show this help message
• `/about` - About this bot

*How to use:*
1. *Direct message*: Send Amharic text directly to this bot
2. *Inline mode*: Type `@yourbotname` in any chat followed by Amharic text

*Features:*
• Transliterates all Amharic characters (ፊደል)
• Handles punctuation and special characters
• Works with long texts and multiple words
• Supports both direct messages and inline queries

*Examples:*
• `ሰላም` → `selam`
• `ምንድነው` → `mindinew`
• `ለመሳተፍ` → `lemesatef`

Happy transliterating! 🎉
    """
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send information about the bot."""
    about_text = """
ℹ️ *About Amharic Transliterator Bot*

This bot transliterates Amharic (አማርኛ) text to Latin script, making it easier to read and share Amharic content across different platforms.

*Features:*
• Accurate transliteration using custom rules
• Support for all Amharic characters
• Post-processing for better readability
• Inline mode for use in any chat

🙏 *Thank you for using our bot!*
    """
    await update.message.reply_text(about_text, parse_mode=ParseMode.MARKDOWN)

async def transliterate_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages and transliterate them."""
    if not update.message.text:
        return
    
    try:
        # Send immediate "processing" message
        processing_message = await update.message.reply_text("⏳ Transliterating...")
        
        # Transliterate the message
        original_text = update.message.text
        transliterated = transliterate_amharic(original_text)
        
        # Check if there's any actual Amharic content to transliterate
        if transliterated != original_text:
            # Edit the processing message with the result (no original text included)
            await processing_message.edit_text(transliterated)
        else:
            # Edit the processing message with a helpful message
            await processing_message.edit_text(
                "I didn't detect any Amharic text to transliterate. "
                "Please send me some Amharic text!"
            )
    except Exception as e:
        logger.error(f"Error transliterating message: {e}")
        # Try to edit the processing message if it exists
        try:
            await processing_message.edit_text(
                "Sorry, I encountered an error while transliterating. Please try again."
            )
        except:
            # If editing fails, send a new message
            await update.message.reply_text(
                "Sorry, I encountered an error while transliterating. Please try again."
            )

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline queries for transliteration."""
    query = update.inline_query.query
    
    if not query:
        return
    
    try:
        # Transliterate the query
        transliterated = transliterate_amharic(query)
        
        # Create inline result
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"Transliterate: {query}",
                description=f"Result: {transliterated}",
                input_message_content=InputTextMessageContent(
                    message_text=transliterated
                )
            )
        ]
        
        await update.inline_query.answer(results, cache_time=300)  # Cache for 5 minutes
    except Exception as e:
        logger.error(f"Error in inline query: {e}")

def main() -> None:
    """Start the bot."""
    # Get the bot token from environment variables
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        BOT_TOKEN = "7998740397:AAG1i0cY0B_gWdBDCY1sdZW4dJZVTEtX5ck"
        print("⚠️ Using hardcoded token for testing. Please set up .env file properly!")
    
    if not BOT_TOKEN:
        print("❌ Please set your BOT_TOKEN environment variable!")
        return
    
    # Create the Application with optimized settings
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)  # Enable concurrent processing
        .build()
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(InlineQueryHandler(inline_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, transliterate_message))

    # Run the bot with optimized settings
    print("🚀 Starting Amharic Transliterator Bot...")
    print("Bot is running! Send /start to begin.")
    
    # Start the bot with faster polling
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        poll_interval=0.5,  # Faster polling (default is 1.0)
        timeout=30,  # Shorter timeout for faster response
        bootstrap_retries=5,
        read_timeout=10,
        write_timeout=10
    )

if __name__ == '__main__':
    main()