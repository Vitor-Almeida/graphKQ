import re
import pandas as pd
import fnmatch
from google.cloud import translate

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

def read_text(path):
    file = open(path)
    texto = file.read()

    #texto = texto.replace("\n"," ")
    #texto = re.sub('\\s+', ' ', texto)

    file.close()

    return texto

def mountRegexDic(reg,texto):

    artDic = {}
    nFound = 0

    for match in re.finditer(reg, texto):
        artDic[nFound]={'matchName':match.group(),'start':match.start(),'end':match.end()}
        nFound += 1

    for idx,articles in enumerate(artDic):

        if idx == len(artDic)-1:
            artDic[idx]['splitText'] = texto[artDic[idx]['start']:len(texto)] 
        else:
            artDic[idx]['splitText'] = texto[artDic[idx]['start']:artDic[idx+1]['start']]

    return artDic

def get_pre_next(idx,arr):

    if isinstance(arr, dict):
        keyList = list(arr)

        try:
            key0 = keyList[idx-1]
            pre = arr[key0]
        except:
            pre = None
        try:
            key2 = keyList[idx+1]
            nextt = arr[key2]
        except:
            nextt = None
    else:
        try:
            pre = arr[idx-1]
        except:
            pre = None

        try:
            nextt = arr[idx+1]
        except:
            nextt = None

    return pre,nextt

def remove_weird(texto):

    texto = texto.replace("\n"," ")
    texto = re.sub('\\s+', ' ', texto)
    texto = texto.strip()

    return texto

def subBelong(idx,dic1,dic2):

    arrItem = []
    pre_dic1,next_dic1 = get_pre_next(idx,dic1)
    cur_dic1 = dic1[idx]

    line_found = False

    for ydx in dic2:

        if next_dic1 != None:
            start = cur_dic1['start']
            end = next_dic1['start']
        else:
            start = cur_dic1['start']
            end = cur_dic1['end']

        if (start <= dic2[ydx]['start']) and (end >= dic2[ydx]['end']):
            line_found=True
            arrItem.append([idx,ydx])

    return arrItem,line_found

def twoDlistSum(lista,valor):

    tmpList = []

    for n in lista:
        tmpList.append(n+valor)

    return tmpList

def belongs(hierDic):

    arrItem = []
    sumTotal = []

    for idx,n in enumerate(hierDic):

        pre_hierDic,next_hierDic = get_pre_next(idx,hierDic)
        cur_hierDic = hierDic[n]

        dic1 = cur_hierDic
        dic2 = next_hierDic

        if dic1 == None or dic2 == None:
            return arrItem

        for xdx in dic1:

            tmpArr,line_found = subBelong(xdx,dic1,dic2)
            nextDim = 0
            if tmpArr != []:
                tmpArr=twoDlistSum(tmpArr,[idx,idx+nextDim+1])

            while line_found == False:
                pre_hierDicSub,next_hierDicSub = get_pre_next(idx+(nextDim+1),hierDic)

                if dic1 == None or next_hierDicSub == None:
                    break

                tmpArr,line_found = subBelong(xdx,dic1,next_hierDicSub)
                if tmpArr != []:
                    tmpArr=twoDlistSum(tmpArr,[idx,idx+nextDim+2])
                nextDim += 1

            sumTotal = sumTotal + tmpArr

        arrItem.append(sumTotal)
        sumTotal = []

    return arrItem

def list_join(list1,list2):

    new_list = []

    for y in list1:
        line_found = False
        for x in list2:

            if y[-1] == x[0]:
                line_found=True
                tmplist = y + [x[-1]]
                new_list.append(tmplist)

        if line_found == False:
            tmplist = y + ['None']
            new_list.append(tmplist)

    return new_list

def populateTextDic(texto):

    hierDic = {'fullCapDic':mountRegexDic(r'\nCAPÍTULO [MDCLXVI]+',texto),
                'fullSecDic':mountRegexDic(r'\nSeção [MDCLXVI]+',texto),
                'fullArtDic':mountRegexDic(r'\nArt.*?[0-9]+',texto),
                'fullParDic':mountRegexDic(r'\n§',texto),
                'fullItemDic':mountRegexDic(r'\n[MDCLXVI]+.-',texto),
                'fullLetterDic':mountRegexDic(r'\n[a-z]\).',texto)}

    tmpArr = belongs(hierDic)

    dicCol = {}
    larg = 0
    for n in tmpArr:
        larg = larg + len(n)

    numOfCol = [0,1,2,3,4,5,6]

    for n in range(0,larg):
        dicCol[n]={0:'None',1:'None',2:'None',3:'None',4:'None',5:'None',6:False}

    dicIndex = 0
    alt = False
    for n in tmpArr:
        for idx,itm in enumerate(n):
            col1 = itm[-2]
            col2 = itm[-1]

            if abs(col1-col2)>1:
                alt = True
            else:
                alt = False

            colOk = [col1]+[col2] + [6]

            dicCol[dicIndex][col1] = itm[0]
            dicCol[dicIndex][col2] = itm[1]
            dicCol[dicIndex][6] = alt

            for nok in numOfCol:
                if nok in colOk:
                    continue
                else:
                    dicCol[dicIndex][nok] = 'None_' + str(idx)

            dicIndex += 1

    lista1 = []

    tmpArrAj = []

    dicIndex = []

    for leng in tmpArr:
        dicIndex.append(len(leng))

    alteredIndices_List= []
    normalIndices_List = []
    alteredIndices = []
    finalIndList = []
    for leng in range(0,len(dicIndex)):
        #for n in range(0,len(tmpArr[leng])):

        if leng == 0:
            start = 0
        else:
            start = sum(dicIndex[:leng])
        end = dicIndex[leng]

        normalIndices = list(range(start,start+end))
        normalIndices_List.append(normalIndices)

        for x in normalIndices:
            if dicCol[x][6] == True:
                alteredIndices.append(x)

        alteredIndices_List.append(alteredIndices)
        alteredIndices = []

    for leng in range(0,len(dicIndex)-1):
        finalIndList.append(list(set(normalIndices_List[leng+1]).union(set(alteredIndices_List[leng]))))

    finalIndList = [list(range(0,0+dicIndex[0]))] + finalIndList

    for leng in range(0,len(dicIndex)):
        #for n in range(0,len(tmpArr[leng])):

        if leng == 0:
            start = 0
        else:
            start = dicIndex[leng-1]
        end = dicIndex[leng]

        normalIndices = list(range(start,end))

        for n in finalIndList[leng]:
            #if idx == dicIndex[leng]:
            #    break
            #if fnmatch.fnmatchcase(str(dicCol[n][leng]), 'None_??') and fnmatch.fnmatchcase(str(dicCol[n][leng+1]), 'None_??'):
            #    continue
            #else:
            lista1.append([dicCol[n][leng],dicCol[n][leng+1]])

        tmpArrAj.append(lista1)
        lista1 = []

    for idx,n in enumerate(tmpArrAj):

        pre_tmpArrAj,next_tmpArrAj = get_pre_next(idx,tmpArrAj)
        cur_tmpArrAj = n

        if idx == 0:
            tmpIndexTab = cur_tmpArrAj

        if next_tmpArrAj != None:
            tmpIndexTab = list_join(tmpIndexTab,next_tmpArrAj)

    transTab = []

    for rows in tmpIndexTab:
        tmplist = []

        for idx,n in enumerate(hierDic):
            col = hierDic[n].get(rows[idx],'None')
            if col != 'None':
                if idx >= 0 and idx <= 2:
                    tmplist.append(remove_weird(col['matchName']))
                else:
                    tmplist.append(remove_weird(col['splitText']))
            else:
                tmplist.append('None')

        transTab.append(tmplist)

    return transTab


def main():

    path = '/home/jaco/Projetos/graphKQ/data/garbage/raw.txt'
    texto = read_text(path)

    df = populateTextDic(texto)
    df.to_csv(f'data/processedText/teste.csv',index=False)

    #texto = text()
    texto = texto.replace("\n"," ")
    texto = re.sub('\\s+', ' ', texto)
    texto = texto.strip()

if __name__ == '__main__':
    main()