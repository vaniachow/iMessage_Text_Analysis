import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from transformers import pipeline
from nltk.stem import WordNetLemmatizer
import re
import contractions
'''
READING AND CLEANING TEXT MESSAGES
'''
def preprocessing(text):
    text = text.strip()
    text = contractions.fix(text)
    text = re.sub(r'[^\w\s]', '', text)
    lemmatizer = WordNetLemmatizer()
    cleaned_words = []
    for word in text.split():
        cleaned_words.append(lemmatizer.lemmatize(word))
    text = ' '.join(cleaned_words)
    text = text.lower()
    return text

def read_file(file_path, df):
    with open(file_path, "r") as file:
        all_messages = file.read()
        soup = BeautifulSoup(all_messages, "html.parser")
        messages = soup.find_all("div", class_="message")
        message_counter = 0
        for message in messages:
            if message_counter % 10 == 0:
                #Parse time
                time = message.find("span", class_ = "timestamp").text
                time = time.split("(")[0]
                time = time.rstrip()
                date_obj = datetime.strptime(time, "%b %d, %Y %I:%M:%S %p")
                text = message.find("div", class_="message_part")
                if date_obj > DATE_AFTER and text:
                    #Parse sender
                    sender = message.find("span", class_ = "sender").text
                    # Parse message
                    text = text.text
                    clean_text = preprocessing(text)
                    # Append
                    new_row = {'Time': date_obj, 'Sent From': sender, 'Message': clean_text}
                    df.loc[len(df)] = new_row
            message_counter += 1

'''
SENTIMENT ANALYSIS
'''
def sentiment_analysis(df):
    classifier = pipeline("text-classification", model='bhadresh-savani/bert-base-uncased-emotion',
                          return_all_scores=True)
    emotion_weightings = {'sadness': 10, 'joy': 1, 'love': 10, 'anger': 1, 'fear': 10, 'surprise': 10}
    for index, row in df.iterrows():
        message = row['Message']
        prediction = classifier(message, )
        max_emotion, max_score = '', 0
        for emotion in prediction[0]:
            emotion_word = emotion['label']
            emotion_score = emotion['score'] * emotion_weightings[emotion_word]
            df.loc[index, emotion_word] = float(emotion_score)
            if max_emotion == '' or emotion_score > max_score:
                max_emotion = emotion_word
                max_score = emotion_score
        df.loc[index, 'sentiment'] = max_emotion

'''
TERMINAL
'''
column_titles = ['Time', 'Sent From', 'Message', 'sadness', 'joy', 'love', 'anger', 'fear', 'surprise', 'sentiment']
df = pd.DataFrame(columns=column_titles)
folder_path = "imessage_export"
DATE_AFTER = datetime(2023, 1, 1)
#CONVERSATIONS = 5
CONVERSATIONS = len(os.listdir(folder_path))
for filename in os.listdir(folder_path):
    if CONVERSATIONS > 0:
        file_path = os.path.join(folder_path, filename)
        print(file_path)
        read_file(file_path, df)
        CONVERSATIONS -= 1
sentiment_analysis(df)
print(df['Sent From'])
print(set(df['Sent From']))
df.to_csv('complete.csv')
