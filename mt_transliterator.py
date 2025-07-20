import logging
import os
import re
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, InlineQueryHandler
from telegram.constants import ParseMode
import uuid
import asyncio

# Set up logging with less verbose output
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)
logger = logging.getLogger(__name__)

# Improved transliteration map with better accuracy
AMHARIC_MAP = {
    # ሀ Series
    "ሀ": "ha", "ሁ": "hu", "ሂ": "hi", "ሃ": "ha", "ሄ": "he", "ህ": "h", "ሆ": "ho", "ሇ": "hwa",
    
    # ለ Series  
    "ለ": "le", "ሉ": "lu", "ሊ": "li", "ላ": "la", "ሌ": "le", "ል": "l", "ሎ": "lo", "ሏ": "lwa",
    
    # ሐ Series (hammeru ha)
    "ሐ": "ha", "ሑ": "hu", "ሒ": "hi", "ሓ": "ha", "ሔ": "he", "ሕ": "h", "ሖ": "ho", "ሗ": "hwa",
    
    # መ Series
    "መ": "me", "ሙ": "mu", "ሚ": "mi", "ማ": "ma", "ሜ": "me", "ም": "m", "ሞ": "mo", "ሟ": "mwa",
    
    # ሠ Series
    "ሠ": "se", "ሡ": "su", "ሢ": "si", "ሣ": "sa", "ሤ": "se", "ሥ": "s", "ሦ": "so", "ሧ": "swa",
    
    # ረ Series
    "ረ": "re", "ሩ": "ru", "ሪ": "ri", "ራ": "ra", "ሬ": "re", "ር": "r", "ሮ": "ro", "ሯ": "rwa",
    
    # ሰ Series
    "ሰ": "se", "ሱ": "su", "ሲ": "si", "ሳ": "sa", "ሴ": "se", "ስ": "s", "ሶ": "so", "ሷ": "swa",
    
    # ሸ Series
    "ሸ": "she", "ሹ": "shu", "ሺ": "shi", "ሻ": "sha", "ሼ": "she", "ሽ": "sh", "ሾ": "sho", "ሿ": "shwa",
    
    # ቀ Series
    "ቀ": "qe", "ቁ": "qu", "ቂ": "qi", "ቃ": "qa", "ቄ": "qe", "ቅ": "q", "ቆ": "qo", "ቇ": "qwa",
    
    # በ Series
    "በ": "be", "ቡ": "bu", "ቢ": "bi", "ባ": "ba", "ቤ": "be", "ብ": "b", "ቦ": "bo", "ቧ": "bwa",
    
    # ቨ Series
    "ቨ": "ve", "ቩ": "vu", "ቪ": "vi", "ቫ": "va", "ቬ": "ve", "ቭ": "v", "ቮ": "vo", "ቯ": "vwa",
    
    # ተ Series
    "ተ": "te", "ቱ": "tu", "ቲ": "ti", "ታ": "ta", "ቴ": "te", "ት": "t", "ቶ": "to", "ቷ": "twa",
    
    # ቸ Series
    "ቸ": "che", "ቹ": "chu", "ቺ": "chi", "ቻ": "cha", "ቼ": "che", "ች": "ch", "ቾ": "cho", "ቿ": "chwa",
    
    # ኀ Series (same as ሀ)
    "ኀ": "ha", "ኁ": "hu", "ኂ": "hi", "ኃ": "ha", "ኄ": "he", "ኅ": "h", "ኆ": "ho", "ኇ": "hwa",
    
    # ነ Series
    "ነ": "ne", "ኑ": "nu", "ኒ": "ni", "ና": "na", "ኔ": "ne", "ን": "n", "ኖ": "no", "ኗ": "nwa",
    
    # ኘ Series
    "ኘ": "gne", "ኙ": "gnu", "ኚ": "gni", "ኛ": "gna", "ኜ": "gne", "ኝ": "gn", "ኞ": "gno", "ኟ": "gnwa",
    
    # Vowels (independent)
    "አ": "a", "ኡ": "u", "ኢ": "i", "ኣ": "a", "ኤ": "e", "እ": "", "ኦ": "o", "ኧ": "wa",
    
    # ከ Series
    "ከ": "ke", "ኩ": "ku", "ኪ": "ki", "ካ": "ka", "ኬ": "ke", "ክ": "k", "ኮ": "ko", "ኯ": "kwa",
    
    # ኸ Series
    "ኸ": "khe", "ኹ": "khu", "ኺ": "khi", "ኻ": "kha", "ኼ": "khe", "ኽ": "kh", "ኾ": "kho", "ዀ": "khwa",
    
    # ወ Series
    "ወ": "we", "ዉ": "wu", "ዊ": "wi", "ዋ": "wa", "ዌ": "we", "ው": "w", "ዎ": "wo", "ዏ": "wwa",
    
    # ዐ Series (glottal)
    "ዐ": "a", "ዑ": "u", "ዒ": "i", "ዓ": "a", "ዔ": "e", "ዕ": "", "ዖ": "o", "዗": "wa",
    
    # ዘ Series
    "ዘ": "ze", "ዙ": "zu", "ዚ": "zi", "ዛ": "za", "ዜ": "ze", "ዝ": "z", "ዞ": "zo", "ዟ": "zwa",
    
    # ዠ Series
    "ዠ": "zhe", "ዡ": "zhu", "ዢ": "zhi", "ዣ": "zha", "ዤ": "zhe", "ዥ": "zh", "ዦ": "zho", "ዧ": "zhwa",
    
    # የ Series
    "የ": "ye", "ዩ": "yu", "ዪ": "yi", "ያ": "ya", "ዬ": "ye", "ይ": "y", "ዮ": "yo", "ዯ": "ywa",
    
    # ደ Series
    "ደ": "de", "ዱ": "du", "ዲ": "di", "ዳ": "da", "ዴ": "de", "ድ": "d", "ዶ": "do", "ዷ": "dwa",
    
    # ጀ Series
    "ጀ": "je", "ጁ": "ju", "ጂ": "ji", "ጃ": "ja", "ጄ": "je", "ጅ": "j", "ጆ": "jo", "ጇ": "jwa",
    
    # ገ Series
    "ገ": "ge", "ጉ": "gu", "ጊ": "gi", "ጋ": "ga", "ጌ": "ge", "ግ": "g", "ጎ": "go", "ጏ": "gwa",
    
    # ጠ Series
    "ጠ": "te", "ጡ": "tu", "ጢ": "ti", "ጣ": "ta", "ጤ": "te", "ጥ": "t", "ጦ": "to", "ጧ": "twa",
    
    # ጨ Series
    "ጨ": "che", "ጩ": "chu", "ጪ": "chi", "ጫ": "cha", "ጬ": "che", "ጭ": "ch", "ጮ": "cho", "ጯ": "chwa",
    
    # ጰ Series
    "ጰ": "pe", "ጱ": "pu", "ጲ": "pi", "ጳ": "pa", "ጴ": "pe", "ጵ": "p", "ጶ": "po", "ጷ": "pwa",
    
    # ጸ Series
    "ጸ": "tse", "ጹ": "tsu", "ጺ": "tsi", "ጻ": "tsa", "ጼ": "tse", "ጽ": "ts", "ጾ": "tso", "ጿ": "tswa",
    
    # ፀ Series  
    "ፀ": "tse", "ፁ": "tsu", "ፂ": "tsi", "ፃ": "tsa", "ፄ": "tse", "ፅ": "ts", "ፆ": "tso", "ፇ": "tswa",
    
    # ፈ Series
    "ፈ": "fe", "ፉ": "fu", "ፊ": "fi", "ፋ": "fa", "ፌ": "fe", "ፍ": "f", "ፎ": "fo", "ፏ": "fwa",
    
    # ፐ Series
    "ፐ": "pe", "ፑ": "pu", "ፒ": "pi", "ፓ": "pa", "ፔ": "pe", "ፕ": "p", "ፖ": "po", "ፗ": "pwa",
    
    # Punctuation and special characters
    "።": ".", "፣": ",", "፤": ";", "፥": ":", "፦": "::", "፧": "?", "፨": "!", "፠": " ",
    " ": " ", "\n": "\n", "\r": "\n", "\r\n": "\n", "\t": " ",
    # Rare jawns
    "ኵ":"kwi", "ኧ": "e","ቋ": "qwa", "ቓ": "qwa", "ጓ": "gwa", "ጕ": "gwi", "ኋ": "hwa", "ዃ": "hwa", "ቒ": "qwi", "ኊ": "khwi", "ጚ": "jji",

    # Numbers
    "፩": "1", "፪": "2", "፫": "3", "፬": "4", "፭": "5", "፮": "6", "፯": "7", "፰": "8", "፱": "9", "፲": "10",
}

# Enhanced consonant cluster rules
CONSONANT_CLUSTERS = {
    # Common patterns
    'mgb': 'migib',     # ምግብ
    'lj': 'lij',        # ልጅ  
    'nkb': 'nikib',     # እንክብ
    'str': 'sitir',     # ስትር
    'bst': 'bist',      # በስት
    'shr': 'shir',      # ሽር
}

# Prefixes that should get apostrophes
PREFIXES_WITH_APOSTROPHE = ['le', 'ye', 'be', 'ke', 'ma', 'me', 'e', 'a', 'te', 's', 'en', 'ya', 'y']

def has_amharic_content(text):
    """Check if text contains Amharic characters."""
    if not text:
        return False
    
    # Check for any Amharic Unicode ranges
    for char in text:
        # Ethiopic script Unicode range (U+1200–U+137F)
        if '\u1200' <= char <= '\u137F':
            return True
    return False

def transliterate_amharic(amharic_text):
    """Transliterate Amharic text while preserving original formatting (spacing, indentation, line breaks)."""
    if not amharic_text:
        return ""

    result = []
    for char in amharic_text:
        transliterated_char = AMHARIC_MAP.get(char, char)
        result.append(transliterated_char)

    # Don't join with ' '.join — just join directly to preserve spacing
    transliterated = ''.join(result)

    # Now apply post-processing rules, but avoid stripping formatting
    return apply_post_processing_rules_preserving_formatting(transliterated)

def apply_post_processing_rules_preserving_formatting(text):
    """Post-process text while preserving all original spacing and line breaks."""
    # Do NOT collapse whitespace
    # Instead process word-by-word while keeping spacing/indentation

    tokens = re.split(r'(\s+)', text)  # Keeps all spaces/newlines/tabs as separate tokens
    processed_tokens = []

    for token in tokens:
        if not token.strip():  # It's just whitespace (space, tab, newline), preserve as is
            processed_tokens.append(token)
        else:
            word = process_word_structure(token)
            word = apply_prefix_apostrophe_rules(word)
            processed_tokens.append(word)

    return ''.join(processed_tokens)


def apply_post_processing_rules(text):
    """Apply post-processing rules for better transliteration."""
    # Remove extra spaces
    text = ' '.join(text.split())
    
    # Apply consonant cluster rules
    for pattern, replacement in CONSONANT_CLUSTERS.items():
        text = text.replace(pattern, replacement)
    
    # Split text more carefully - handle compound words
    # Look for word boundaries (spaces, punctuation, numbers)
    import re
    words = re.split(r'(\s+|[.,;:!?/\d]+)', text)
    processed_words = []
    
    for word in words:
        # Skip whitespace and punctuation
        if not word or word.isspace() or not any(c.isalpha() for c in word):
            processed_words.append(word)
            continue
            
        # Process the word
        processed_word = process_word_structure(word)
        # Apply prefix apostrophe rules only to actual words
        if len(processed_word) > 1 and any(c.isalpha() for c in processed_word):
            processed_word = apply_prefix_apostrophe_rules(processed_word)
        processed_words.append(processed_word)
    
    return ''.join(processed_words)

def apply_prefix_apostrophe_rules(word):
    """Apply prefix apostrophe rules to a word."""
    if not word:
        return word
    
    # Check if word starts with any of the specified prefixes
    # Sort prefixes by length (longest first) to avoid partial matches
    sorted_prefixes = sorted(PREFIXES_WITH_APOSTROPHE, key=len, reverse=True)
    
    for prefix in sorted_prefixes:
        if word.startswith(prefix) and len(word) > len(prefix):
            # Make sure the prefix is actually a complete prefix (not part of a longer word)
            rest_of_word = word[len(prefix):]
            if rest_of_word:  # There must be something after the prefix
                # Add apostrophe after the prefix
                new_word = prefix + "'" + rest_of_word
                
                # Check if there's an 'i' right after the apostrophe that should be deleted
                # The 'i' should be deleted if it's not the first letter in the original word
                if (len(rest_of_word) > 0 and 
                    rest_of_word[0] == 'i' and 
                    len(prefix) > 0):  # Ensure the 'i' is not the first letter
                    # Delete the 'i'
                    new_word = prefix + "'" + rest_of_word[1:]
                
                return new_word
    
    return word

def process_word_structure(word):
    """Process individual word structure for better readability."""
    if len(word) <= 1:
        return word
        
    # Handle specific patterns
    processed = word
    
    # Don't remove 'e' from እ at the beginning - it's important
    # Only remove it in specific contexts
    
    # Handle consonant-vowel patterns more carefully
    if len(processed) >= 3:
        # Insert vowels in consonant clusters if needed, but be more conservative
        new_word = ""
        i = 0
        while i < len(processed):
            new_word += processed[i]
            
            # Look ahead for consonant clusters, but be more selective
            if (i < len(processed) - 2 and 
                processed[i] not in 'aeiou\'' and 
                processed[i+1] not in 'aeiou\'' and 
                processed[i+2] not in 'aeiou\''):
                # Only insert 'i' for specific patterns, not all clusters
                cluster = processed[i:i+3]
                if cluster not in ['ndr', 'mpl', 'str', 'shr', 'nkb', 'mgb', 'lnk']:
                    # Be even more conservative - only add 'i' for very specific cases
                    pass  # Skip automatic 'i' insertion for now
            i += 1
        processed = new_word
    
    return processed

def create_inline_results(original_query, transliterated, has_amharic):
    """Create comprehensive inline results with multiple options."""
    results = []
    
    if has_amharic and transliterated != original_query:
        # Primary result - clean transliteration
        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"✅ {transliterated}",
                description=f"Transliterated: {original_query}",
                input_message_content=InputTextMessageContent(
                    message_text=transliterated
                )
            )
        )
        
        # Alternative result - with original text
        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"📝 With Original",
                description=f"{original_query} → {transliterated}",
                input_message_content=InputTextMessageContent(
                    message_text=f"{original_query} → {transliterated}"
                )
            )
        )
        
        # Code format result (useful for sharing)
        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"💻 Code Format",
                description=f"`{transliterated}`",
                input_message_content=InputTextMessageContent(
                    message_text=f"`{transliterated}`",
                    parse_mode=ParseMode.MARKDOWN
                )
            )
        )
        
        # If the transliterated text is long, offer a shortened preview
        if len(transliterated) > 50:
            preview = transliterated[:47] + "..."
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title=f"📄 Preview",
                    description=f"Short preview: {preview}",
                    input_message_content=InputTextMessageContent(
                        message_text=preview
                    )
                )
            )
    
    else:
        # No Amharic detected
        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="⚠️ No Amharic Detected",
                description="Please type some Amharic text to transliterate",
                input_message_content=InputTextMessageContent(
                    message_text="Please type some Amharic text to transliterate. Example: ሰላም"
                )
            )
        )
        
        # Provide example
        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="📚 Example: ሰላም",
                description="Try typing: ሰላም",
                input_message_content=InputTextMessageContent(
                    message_text="s'elam"
                )
            )
        )
    
    return results

# Bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = """
🇪🇹 *Welcome to Amharic Transliterator Bot!* 🇪🇹

I can help you transliterate Amharic text to Latin script.

*How to use:*
• Send me any Amharic text and I'll transliterate it
• Use inline mode: type `@amharic_transliterator_bot` followed by Amharic text in any chat
• Send /help for more information

*Example:*
Send: `ሰላም`
Get: `s'elam`

Send: `ልጅ`  
Get: `l'j`

*Enhanced Features:*
• Improved Grammar
• Formatting Support
• Multiple inline result options
• Better error handling

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
2. *Inline mode*: Type `@amharic_transliterator_bot` in any chat followed by Amharic text.

*Inline Features:*
• Multiple result options (clean, with original, code format)
• Better error handling for non-Amharic text
• Preview options for long text
• Examples when no Amharic is detected

*Examples:*
• `ለሰላም` → `le'salam`
• `በዓል` → `be'al`
• `የሰላም` → `ye'salam`

Happy transliterating! 🎉
    """
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send information about the bot."""
    about_text = """
ℹ️ *About Amharic Transliterator Bot*

This bot transliterates Amharic (አማርኛ) text to Latin script(a'margna), making it easier to read and share Amharic content across different platforms.

*Enhanced inline mode features:*
• Multiple result options
• Better Amharic detection
• Formatting preservation
• Smart error handling

🙏 *Thank you for using my bot!*
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
        has_amharic = has_amharic_content(original_text)
        
        if has_amharic and transliterated != original_text:
            # Edit the processing message with the result
            await processing_message.edit_text(transliterated)
        else:
            # Edit the processing message with a helpful message
            await processing_message.edit_text(
                "I didn't detect any Amharic text to transliterate. "
                "Please send me some Amharic text! Example: ሰላም"
            )
    except Exception as e:
        logger.error(f"Error transliterating message: {e}")
        try:
            await processing_message.edit_text(
                "Sorry, I encountered an error while transliterating. Please try again."
            )
        except:
            await update.message.reply_text(
                "Sorry, I encountered an error while transliterating. Please try again."
            )

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enhanced inline query handler with better transliteration and multiple result options."""
    query = update.inline_query.query.strip()
    
    # If query is empty, show helpful instructions
    if not query:
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="🇪🇹 Amharic Transliterator",
                description="Type Amharic text to transliterate...",
                input_message_content=InputTextMessageContent(
                    message_text="Type some Amharic text after @amharic_transliterator_bot to transliterate it!\n\nExample: @amharic_transliterator_bot ሰላም"
                )
            ),
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="📝 Example: ሰላም",
                description="Example transliteration",
                input_message_content=InputTextMessageContent(
                    message_text="s'elam"
                )
            )
        ]
        
        await update.inline_query.answer(results, cache_time=300, is_personal=True)
        return
    
    try:
        # Check if the query contains Amharic
        has_amharic = has_amharic_content(query)
        
        # Transliterate the query using the same enhanced method as direct messages
        transliterated = transliterate_amharic(query)
        
        # Create comprehensive results
        results = create_inline_results(query, transliterated, has_amharic)
        
        # Answer the inline query with enhanced options
        await update.inline_query.answer(
            results, 
            cache_time=300, 
            is_personal=True,
            switch_pm_text="💬 Chat with bot",
            switch_pm_parameter="inline_help"
        )
        
    except Exception as e:
        logger.error(f"Error in inline query: {e}")
        # Fallback error result
        error_results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="❌ Error",
                description="Something went wrong. Please try again.",
                input_message_content=InputTextMessageContent(
                    message_text="Sorry, there was an error processing your request. Please try again or contact support."
                )
            )
        ]
        
        try:
            await update.inline_query.answer(error_results, cache_time=30)
        except:
            pass  # If we can't even send the error, just log it

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
        .concurrent_updates(True)
        .build()
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(InlineQueryHandler(inline_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, transliterate_message))

    # Run the bot with optimized settings
    print("🚀 Starting Enhanced Amharic Transliterator Bot...")
    print("Bot is running! Send /start to begin.")
    
    # Start the bot with faster polling
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        poll_interval=0.5,
        timeout=30,
        bootstrap_retries=5,
        read_timeout=10,
        write_timeout=10
    )

if __name__ == '__main__':
    main()