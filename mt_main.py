from mt_transliterator import transliterate

sample = "አድርገህልኛልና በቸርነትህ " \
"አመሰግንሃለሁ እልል"
sampled = "እግዚአብሔር ከእኛ ጋር ነው።"
print("Original:", sample)
print("Phonetic:", transliterate(sample))