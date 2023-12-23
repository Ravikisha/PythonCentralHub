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


# Alternative solution
words2 = {}

# Loop through the list of words
for word in words:
    # If the word is not in the dictionary, add it
    if word not in words2:
        words2[word] = 1
    # If the word is in the dictionary, increment its value
    else:
        words2[word] += 1
        
# Sort the dictionary by value in descending order
sorted_words = sorted(words2.items(), key=lambda x: x[1], reverse=True)

# Print the 10 most common words
print(sorted_words[:10])

# Close the file
text.close()