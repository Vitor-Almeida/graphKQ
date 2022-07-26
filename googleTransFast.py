import codecs
import re
from google.cloud import translate
import time


def translate_text(text):

    project_id="lawtranslator"

    client = translate.TranslationServiceClient()
    location = "global"

    parent = f"projects/{project_id}/locations/{location}"

    response = client.translate_text(
            parent= parent,
            contents= [text],
            mime_type="text/plain",  # mime types: text/plain, text/html
            source_language_code= "pt-BR",
            target_language_code= "en-US"
    )

    #result = translate_client.translate(text, target_language="en",source_language="pt")

    return response.translations[0].translated_text

texto = open('/home/jaco/Projetos/graphKQ/data/garbage/raw.txt').read()
#texto = text()
texto = texto.replace("\n"," ")
texto = re.sub('\\s+', ' ', texto)
texto = texto.strip()

new_text = []
text_trans = []

MAX_CHAR = (5000) - 50

for idx,step in enumerate(range(0,len(texto),MAX_CHAR)):
    flag_aj = 0
    flag_sum = 0

    if idx == 0:
        continue

    while texto[step] != ' ':
        step += 1
        flag_sum += flag_sum
        flag_aj = 1

    if flag_aj:
        minbatch = (idx-1) * MAX_CHAR + (flag_sum)
    else:
        minbatch = (idx-1) * MAX_CHAR

    new_text.append(texto[minbatch:step])
    print(f'{minbatch}:{step}')

    if step + MAX_CHAR > len(texto):
        print(f'{step}:{len(texto)}')
        new_text.append(texto[step:len(texto)+2])

    
for idx,samples in enumerate(new_text):
    textoTra = translate_text(samples)
    textoTra = textoTra.replace("&#39;","'")
    text_trans.append(textoTra)
    print(f'já foi: {idx} de {int(round(len(texto)/MAX_CHAR,0))}')
    time.sleep(5)


texto = ' '.join(text_trans)

file = codecs.open("/home/jaco/Projetos/graphKQ/data/garbage/rawTranslation.txt", "w", "utf-8")
file.write(texto)
file.close()