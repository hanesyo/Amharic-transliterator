def transliterate_amharic(amharic_text):
    amharic_map = {
    
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
    # ኸ Series (H‘)
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
    #Specials
    "።": ".", "፣": ",", "፤": ";", "፥": ":", "፦": ":", " ": " ", "\n": "\n",
     
 
    

    "ዷ": "dwa", "ቧ": "bwa", "ጧ": "t'wa",


}
    transliterated = ""
    for char in amharic_text:
        if char in amharic_map:
                    transliterated += amharic_map[char]
        else:
                transliterated += char  # Keep unknown characters as-is
            
            # Step 2: Apply post-processing rules
    result = apply_post_processing_rules(transliterated)
            
    return result

def apply_post_processing_rules(text):
    """
    Apply various post-processing rules to improve transliteration quality.
    """
    text = apply_final_i_rule(text)
    
    # Rule 2: Insert vowels in consonant clusters (based on user preferences)
    text = insert_vowels_in_clusters(text)
    
    return text

def apply_final_i_rule(text):
    """
    Rule: If a word ends with a transliterated fidel that is longer than 1 letter 
    and ends in 'i', remove the final 'i'.
    """
    words = text.split()
    processed_words = []
    
    for word in words:
        # Handle punctuation
        punctuation = ""
        clean_word = word
        
        # Check if word ends with punctuation
        if word and word[-1] in ".,;:!?":
            punctuation = word[-1]
            clean_word = word[:-1]
        
        # Apply the rule: if word ends with 'i' and the part before 'i' is longer than 1 letter
        if len(clean_word) > 2 and clean_word.endswith('i'):
            clean_word = clean_word[:-1]
        
        processed_words.append(clean_word + punctuation)
    
    return ' '.join(processed_words)

def insert_vowels_in_clusters(text):
    """
    Insert vowels in consonant clusters based on user preferences.
    Examples: mgb -> migib, lj -> lij
    """
    # Define consonant patterns that need vowel insertion
    consonant_patterns = {
        'mgb': 'migib',   # ምግብ
        'lj': 'lij',      # ልጅ
        # Add more patterns as needed based on user feedback
    }
    
    words = text.split()
    processed_words = []
    
    for word in words:
        # Handle punctuation
        punctuation = ""
        clean_word = word
        
        if word and word[-1] in ".,;:!?":
            punctuation = word[-1]
            clean_word = word[:-1]
        
        # Apply consonant cluster rules
        for pattern, replacement in consonant_patterns.items():
            clean_word = clean_word.replace(pattern, replacement)
        
        processed_words.append(clean_word + punctuation)
    
    return ' '.join(processed_words)

# Test the complete function
if __name__ == "__main__":
    # Test cases
    test_texts = [
        "ምንድነው",               # selam
        "እንደአት ነው",            # lij (should apply vowel insertion)
        "በጸጋው አድርጎልኛል",       # migib (should apply vowel insertion)
        "ውሀ",           # wiha
        "ቤት",            # bet -> beti -> bet (final i rule)
        "ሰላም ልጅ",       # selam lij
        "ምን ነው",        # min new
        "ጥሩ ሰው",        # t'iru sew
        "ደስ ይላል",        # desi yilali -> des yilal
        "ቤተሰብ",          # beteseb
    ]
    
    print("Testing complete Amharic transliteration:")
    print("=" * 50)
    
    for amharic in test_texts:
        result = transliterate_amharic(amharic)
        print(f"'{amharic}' -> '{result}'")