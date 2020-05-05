#dependencies
#wikipidida data
#bs4
from bs4 import BeautifulSoup
import requests
import re
import operator
import json as j
from tabulate import tabulate
import sys
from stop_words import get_stop_words


def getList(url):
    word_list = []
    #raw data
    source_code = requests.get(url)
    #convert to text
    plain_text = source_code.text
    #lxml format
    soup = BeautifulSoup(plain_text,'lxml')

    #find the words in paragraph tag
    for text in soup.findAll('p'):
        if text.text is None:
            continue
        #content
        content = text.text
        #lowercase and split into an array
        words = content.lower().split()

        #for each word
        for word in words:
            #remove non-chars
            cleaned_word = clean_word(word)
            #if there is still something there
            if len(cleaned_word) > 0:
                #add it to our word list
                word_list.append(cleaned_word)

    return word_list


#clean word with regex
def clean_word(word):
    cleaned_word = re.sub('[^A-Za-z]+', '', word)
    return cleaned_word


def FrequencyTable(word_list):
    #word count
    word_count = {}
    for word in word_list:
        #index is the word
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1

    return word_count

#remove stop words
def remove_stop_words(frequency_list):
    stop_words = get_stop_words('en')

    temp_list = []
    for key,value in frequency_list:
        if key not in stop_words:
            temp_list.append([key, value])

    return temp_list
a_link = "https://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srsearch="
m_link = "https://en.wikipedia.org/wiki/"
if( len( sys.argv)<2):
        print("please enter a valid string ")
        exit(-1)
else:
    querym=sys.argv[1]
    if(len(sys.argv)>2):
        search_mode=True
    else:
        search_mode=False

    main_url=a_link+querym
    try:
        res=requests.get(main_url)
        data=j.loads(res.content.decode('utf-8'))
        #got the data
        page_tabs=data['query']['search'][0]['title']
        main_url=m_link+page_tabs
        page_word_list=getList(main_url)
        #pandas and stuff
        word_count=FrequencyTable(page_word_list)   
        sorted_frequency_list=sorted(word_count.item(),key=operator.itemgetter(1),reverse=True)
        #removing stopwords
        if(search_mode):
            sorted_frequency_list=remove_stop_words(sorted_frequency_list)
        total_words_sum=0
        for key,value in sorted_frequency_list:
            total_words_sum+=value
    #top to result
        if(len(sorted_frequency_list)>10):
            sorted_frequency_list=sorted_frequency_list[:10]
        final_list=[]
        for key,value in sorted_frequency_list:
            percentage=float((value*100))/total_words_sum
            final_list.append(key,value,round(percentage,4))
        print_headers=['Word','frequency','Frequency Percentage']
        print(tabulate(final_list,headers=print_headers,tablefmt='orgtbl'))
    except requests.exceptions.Timeout:
        print("timeout, server did not respond")
