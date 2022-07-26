from PyPDF2 import PdfReader
import json
import pandas as pd
import re

#export GOOGLE_APPLICATION_CREDENTIALS="/home/jaco/Projetos/graphKQ/data/lawtranslator-9bb51ce495c7.json"
#https://console.cloud.google.com/apis/dashboard?project=lawtranslator

RELEVANT_PAGES = {'D_33327_2019':range(0,57)}

nArtFounds = 0
filename = 'D_33327_2019'
reader = PdfReader(f"/home/jaco/Projetos/graphKQ/data/pdf/{filename}.pdf")
found_articles = {}
text = ''

for pgNum in RELEVANT_PAGES['D_33327_2019']:
    page = reader.pages[pgNum]
    text += page.extract_text()

for match in re.finditer(r'Art.*?[0-9]+', text):
    found_articles[nArtFounds]={'article':match.group(),'start':match.start(),'end':match.end()}
    nArtFounds += 1

for idx,articles in enumerate(found_articles):

    ##arrumar o OCR quando: GOVERNADOR no pdf vira GOVER NADOR entre outros
    ##tradutor arruma isso 

    if idx == len(found_articles)-1:
        found_articles[idx]['splitText'] = text[found_articles[idx]['start']:len(text)]
        found_articles[idx]['splitText'] = found_articles[idx]['splitText'].replace("\n"," ")
        found_articles[idx]['splitText'] = re.sub('\\s+', ' ', found_articles[idx]['splitText'])
        found_articles[idx]['splitText'] = found_articles[idx]['splitText'].strip()
        
    else:
        found_articles[idx]['splitText'] = found_articles[idx]['article']+text[found_articles[idx]['end']:found_articles[idx+1]['start']]
        found_articles[idx]['splitText'] = found_articles[idx]['splitText'].replace("\n"," ")
        found_articles[idx]['splitText'] = re.sub('\\s+', ' ', found_articles[idx]['splitText'])
        found_articles[idx]['splitText'] = found_articles[idx]['splitText'].strip()

def translate_text(text):

    import six
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language="en",source_language="pt")

    return result["translatedText"]

#for idx,articles in enumerate(found_articles):
#for idx in range(0,2):
#    found_articles[idx]['splitTextTranslated'] = translate_text(found_articles[idx]['splitText'])

df = pd.DataFrame.from_dict(found_articles, orient='index')
df.to_csv(f'data/processedText/{filename}.csv',index=False)

with open(f'data/processedText/{filename}.json', 'w') as fp:
    json.dump(found_articles, fp)