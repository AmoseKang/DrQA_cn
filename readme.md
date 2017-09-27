# DrQA Chinese implementation

## Introduction
This is a modified version of facebook [DrQA](https://github.com/facebookresearch/DrQA) module which supports Chinese language. The module is for study only. This module can be used to answer question for any specific context. The initial optimization is targeting to an area of specific university. This project is not fully tested nor fully complete.

## Installation
This is a modified version of facebook [DrQA](https://github.com/facebookresearch/DrQA) module. This module is for study only.
To install this module, please install pytorch according to [pytorch.org](http://pytorch.org/)and run the setup.py in python3 environment. (3.5, 3.6 both works well) (the setup may cover the facebook DrQA) If I missed some requirements, please just install with pip. Then install corenlp with Chinese package according to [CoreNLP offical](https://stanfordnlp.github.io/CoreNLP/), you may specific classpath in environment or in file `drqa\tokenizers\Zh_tokenizer.py`. Then you may download vectors and training sets to start your work.

## Structures
    /data : stores all the data  
        /vector 
        /'training set'
        /'db' : retriever db
        /'module' : saved module
        ...
    /drqa : main modules
        /features : common features file shared in project
        /pipline : concact reader and retriever
            drqa.py  original pipline manager
            simpleDrQA.py  a simple version of pipline manager
        /reader : reader module
            ...
        /retriever : retriever module
            ...
            net_retriever.py : simply retrieve context (search) in the search engine (baidu) and use results as context
        /tokenizers : tokenizer features
            /Zh_tokenizer.py : corenlp chinese
            /zh_features.py : common chinese features
    /scripts : common command line methold
        ...
        /pipline
            sinteractive.py : use simple drqa agent
            ...
Common files in the project is not mentioned, please check with facebook DrQA.

## Features
Please check facebook module for designing features.  
As a Chinese implementation of original module, this project supported full Chinese support with full Chinese linguistic tags. Chinese Lemma tag is replaced with English translation. All the expression will be parsed through Chinese normalization. (symbol, simp and trad)  
Includes function for various Chinese transformation :
1. simplified to traditional
2. Chinese to pinyin
3. Chinese number to number
4. SBC case to DBC case
6. common symbol transformation

The module embed with common words mapping. (abbreviation <-> full spell, etc.)    
This module provides a simple context scoring function for better answer ranking.  
Provide simple context retriever. (worked with baidu search engine)
Provide parsed and tested training set (based on WebQA) and word embedding (60 dimension and 200 dimension).


## Result
sinteractive.py result example: 

\>\>\> process("西交图书馆的全名？", doc_n=1, net_n=3)  
09/27/2017 04:45:38 PM: [ [question after filting : 西安交通大学图书馆的全名? ] ]   
09/27/2017 04:45:39 PM: [ [retreive from net : 3 | expect : 3] ]  

...

09/27/2017 04:45:43 PM: [ [retreive from db] ]
\=================raw text==================  
...侧,目前为工程训练中心、实验室及艺术庭院.西安交大图书馆北楼始建于1961年7月,共三层,建筑面积11200平方米,是和老教学主楼一并设计建设“中苏风格”建筑,风格朴实宏伟.和北楼相连的南楼建筑面积18000平方米,于1991年3月投入使用,地上13层,地下2层.设计上南楼保留了北楼的设计元素,外形呈金字塔形,被部分同学们戏称为“铁甲小宝”.图书馆南楼顶部有报时的大钟,报时音乐为“东方红”,2010年曾改为中国名曲“茉莉花”,后因国际形势变化改回“东方红”.1995年,图书馆经钱学森本人同意及中宣部批准改名钱学森图书馆,并由时任中共中央总书记、国家主席江泽民题写馆名.现今该图书馆拥有阅览座位3518席,累计藏书522.8万册(件),报刊10053种,现刊4089种.
\===================================

....

图书馆南楼顶部有报时的大钟,报时音乐为“东方红”,2010年曾改为中国名曲“茉莉花”,后因国际形势变化改回“东方红” 1995年,图书馆经钱学森本人同意及中宣部批准改名钱学森图书馆,并由时任中共中央总书记、国家主席江泽民题写馆名
======== answer :钱学森图书馆
answer score : 0.0819935
context score : 9.164698700898501
Time: 12.1489

Training with WebQA training dataset, the code runs a 65% conplete match rate in valiation set.  
The result of retriever module or pipline is not tested. (our document set is not complete at all and retriever module seems working badly) The procession for context (retrieved data) is vital in final performance. 


## License
DrQA_cn is BSD-licensed based on [DrQA](https://github.com/facebookresearch/DrQA).

Training set is licensed by baidu : [WebQA](http://idl.baidu.com/WebQA.html). This dataset is released for research purpose only. Copyright (C) 2016 Baidu.com, Inc. All Rights Reserved.
    