# coding: utf-8


def parseIt(text):
    """
        This function is taking a string as parameter that will filter by
        replacing punctuation by a white space and then delete stop words and
        words of less than 2 characters.
        Return a string.
    """
    outputText = ""
    text_filtered = text
    characters_to_replace = ["\"", "!", "?", ",", ";", ".", "\'", "-"]
    for elt in characters_to_replace:
        text_filtered = text_filtered.replace(elt, " ")
    words_numbers = text_filtered.split()
    file_stop_words = open('stop_words.txt', 'r')
    stop_words = file_stop_words.read().split()
    deleted = 0
    for i in range(len(words_numbers)):
        if words_numbers[i - deleted].lower() in stop_words:
            words_numbers.pop(i - deleted)
            deleted += 1
    deleted = 0
    for j in range(len(words_numbers)):
        if len(words_numbers[j - deleted]) < 2:
            words_numbers.pop(j - deleted)
            deleted += 1
    outputText = " ".join(words_numbers)
    if outputText.islower():
        return outputText.title()
    else:
        return outputText
