# Word Counter

# Import the Counter class from the collections module
from collections import Counter

# Open the file in read mode
text = open('text.txt', 'r')

# Use the read method to read the file contents
allWords = text.read()

# Use split method to create a list of words from the text
words = allWords.split()

# Create a Counter object
counter = Counter(words)

# Use the most_common method to print the 10 most common words
print(counter.most_common(10))

# Close the file
text.close()