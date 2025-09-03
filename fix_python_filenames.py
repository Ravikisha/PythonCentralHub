import os
import re
import glob

# Map MDX files to their corresponding Python filenames
filename_mapping = {
    # Beginners
    'asciiartgenerator.mdx': 'asciiartgenerator.py',
    'automatedfilemover.mdx': 'automatedfilemover.py',
    'basic-calendar-app.mdx': 'basiccalendarapp.py',
    'basic-text-editor.mdx': 'basictexteditor.py',
    'basicalarmclock.mdx': 'basicalarmclock.py',
    'basicchatbot.mdx': 'basicchatbot.py',
    'basicmusicplayer.mdx': 'basicmusicplayer.py',
    'basicwebcrawler.mdx': 'basicwebcrawler.py',
    'basicwebscrapper.mdx': 'basicwebscrapper.py',
    'basicwebserver.mdx': 'basicwebserver.py',
    'binarytodecimal.mdx': 'binary_to_decimal.py',
    'blackjack.mdx': 'blackjack.py',
    'calculatorgui.mdx': 'calculatorgui.py',
    'currencyconverter.mdx': 'currencyconverter.py',
    'currencyexchnageratecalculator.mdx': 'currencyexchnageratecalculator.py',
    'dicerolling.mdx': 'dicerolling.py',
    'emailsender.mdx': 'emailsender.py',
    'fibonaccisequence.mdx': 'fibonacci_sequence_generator.py',
    'fileexplorer.mdx': 'fileexplorer.py',
    'guessthenumber.mdx': 'guessthenumber.py',
    'hangman.mdx': 'hangman.py',
    'helloworld.mdx': 'helloworld.py',
    'json-data-validator.mdx': 'jsondatavalidator.py',
    'morsecodetranslator.mdx': 'morsecodetranslator.py',
    'movie-recommendation-system.mdx': 'movierecommendationsystem.py',
    'numberguessingwithai.mdx': 'numberguessingwithai.py',
    'paint.mdx': 'paint.py',
    'passwordstrengthchecker.mdx': 'passwordstrengthchecker.py',
    'personaldiary.mdx': 'personaldiary.py',
    'quizapp.mdx': 'quizapp.py',
    'randompasswordgenerator.mdx': 'randompasswordgenerator.py',
    'reversestring.mdx': 'reverse_string.py',
    'rockpaperscissors.mdx': 'rockpaperscissors.py',
    'rssfeedreader.mdx': 'rssfeedreader.py',
    'simple-blog-system.mdx': 'simpleblogsystem.py',
    'simplecalculator.mdx': 'calculator.py',
    'simplereminderapp.mdx': 'simplereminderapp.py',
    'simplestopwatch.mdx': 'simplestopwatch.py',
    'tempconv.mdx': 'tempconverter.py',
    'textbasedadventuregame.mdx': 'textbasedadventuregame.py',
    'todo.mdx': 'todo.py',
    'todolist.mdx': 'todo.py',
    'urlshorter.mdx': 'urlshorter.py',
    'webpagecontentdownloader.mdx': 'webpagecontentdownloader.py',
    'webpagescrapernotifications.mdx': 'webpagescrapernotifications.py',
    'wordcounter.mdx': 'wordcounter.py',
    
    # Intermediate
    'advanced-web-scraping.mdx': 'advancedwebscraper.py',
    'data-visualization-suite.mdx': 'datavisualization.py',
    'file-encryption-tool.mdx': 'fileencryption.py',
    'morse-code-audio-player.mdx': 'morseCodeAudioPlayer.py',
    'portfolio-website-generator.mdx': 'portfoliowebsitegenerator.py',
    'portfolio-website.mdx': 'portfoliowebsite.py',
    'rest-api-auth.mdx': 'restapiauth.py',
    'rest-api-server.mdx': 'restapiserver.py',
    'weather-app-gui.mdx': 'weatherappgui.py'
}

def fix_code_blocks_with_mapping(file_path):
    filename = os.path.basename(file_path)
    
    if filename not in filename_mapping:
        print(f'Skipping {filename} - no mapping found')
        return False
    
    python_filename = filename_mapping[filename]
    print(f'Processing: {file_path} -> {python_filename}')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace existing title references to use correct Python filename
    pattern = r'```python title="[^"]*\.py" showLineNumbers\{1\}'
    replacement = f'```python title="{python_filename}" showLineNumbers{{1}}'
    
    new_content = re.sub(pattern, replacement, content)
    
    # Check if any changes were made
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

# Find all mdx files in projects folder
project_files = glob.glob('src/content/docs/projects/**/*.mdx', recursive=True)
print(f'Found {len(project_files)} MDX files')

updated_files = []
for file_path in project_files:
    if fix_code_blocks_with_mapping(file_path):
        updated_files.append(file_path)

print(f'\nUpdated {len(updated_files)} files with correct Python filenames:')
for file in updated_files:
    print(f'  ✓ {file}')
