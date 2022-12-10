#%%
## import package
import os
import random
import json
from k_sat_func import *
import time
from nltk import sent_tokenize, word_tokenize
from itertools import combinations, permutations
## preset for random seed
random.seed(100)

## read passage from file(delete in final version)
# filepath='/home/a1930008/k_sat/testset/221138.txt'
# passageID=filepath.split('/')[-1].split('.')[0]
# f = open(filepath)
# passage = f.read()

## preset for question_dict
question_dict_sample={'passageID':None,
                    'question_type':None,
                    'question':None, 
                    'new_passage':None,
                    'answer':None,## 1~5번
                    'e1':None, 'e2':None, 'e3':None, 'e4':None, 'e5':None}
#%% 18, 20, 22(목적/요지/주제): 한국어 보기, 23, 24, 41(주제/제목): 영어 보기
class Q1:
    def __init__(self):
        self.question_type=1
        self.qlist=['목적으로', '주장으로', '요지로']
        self.question=f'다음 글의 {random.choice(self.qlist)} 가장 적절한 것은?'

    def get_ans(self, passage:str)->str:
        return get_paraphrased_sentences_1(passage)

    def get_dist(self, passage:str)->list:
        return get_false_sentences_n(passage, 4)
    
    def make_json(self, passageID:int, passage:str, is_Korean=False):
        question_dict=question_dict_sample.copy()
        
        question_dict['passageID'] = int(passageID)
        question_dict['question_type'] = self.question_type
        question_dict['question'] = self.question
        question_dict['new_passage'] = passage

        answer_sentence=self.get_ans(passage)
        dist_list=self.get_dist(passage)

        if answer_sentence == None or dist_list == None: return None
        
        ## choose answer
        ansidx=random.randint(0, 4)    # ans: 0~4
        question_dict['answer'] = ansidx + 1   ## 0~4 -> 1~5

        dist_list.insert(ansidx, answer_sentence)

        ex_list=[]
        for i in dist_list:
            ex_list.append(check_punctuation_capital_sentence(i))
        
        if len(ex_list) == 5:
            question_dict['e1'] = ex_list[0]
            question_dict['e2'] = ex_list[1]
            question_dict['e3'] = ex_list[2]
            question_dict['e4'] = ex_list[3]
            question_dict['e5'] = ex_list[4]
        else: return None
        return json.dumps(question_dict, ensure_ascii = False)
# %% test Q1
# q1=Q1()
# for i in range(3):
#     q1_json_eng=q1.make_json(passageID, passage, is_Korean=False)
#     if q1_json_eng!=None: break
#     time.sleep(10)    ## RateLimitError 피하기
# print(q1_json_eng)
#%% 26-28, 45(내용 일치/불일치): 영어 보기/한글 보기
class Q2:
    def __init__(self):
        self.question_type=2
        self.qlist =['적절한', '적절하지 않은']
        choice = random.choice(self.qlist)
        # choice =  '적절하지 않은'
        self.flag = True
        if choice=='적절하지 않은': self.flag = False

        self.question=f'윗글에 관한 내용으로 가장 {choice} 것은?'

    def get_ans(self, passage:str):
        if self.flag == True: return get_paraphrased_sentences_1(passage)
        else: return get_paraphrased_sentences_n(passage, 4)

    def get_dist(self, passage:str):
        if self.flag == True: return get_false_sentences_n(passage, 4)
        else: return get_false_sentences_1(passage)

    def make_json(self, passageID:int, passage:str, is_Korean=False):
        question_dict=question_dict_sample.copy()
        
        question_dict['passageID']=int(passageID)
        question_dict['question_type']=self.question_type
        question_dict['question'] = self.question
        question_dict['new_passage'] = passage

        ans=self.get_ans(passage)
        dist=self.get_dist(passage)
        if ans == None or dist == None: return None

        if self.flag==True:
            ## ans: str, dist: list
            ansidx=random.randint(0, 4)    # ans: 0~4
            question_dict['answer'] = ansidx+1   ## 0~4 -> 1~5

            dist.insert(ansidx, ans)
            tmp_ex_list = dist

        else:
            ## ans: list, dist: str
            ansidx=random.randint(0, 4)    # ans: 0~4
            question_dict['answer'] = ansidx+1   ## 0~4 -> 1~5

            ans.insert(ansidx, dist)
            tmp_ex_list = ans


        ex_list=[]
        for i in tmp_ex_list:
            ex_list.append(check_punctuation_capital_sentence(i))
        
        if len(ex_list) == 5:
            question_dict['e1'] = ex_list[0]
            question_dict['e2'] = ex_list[1]
            question_dict['e3'] = ex_list[2]
            question_dict['e4'] = ex_list[3]
            question_dict['e5'] = ex_list[4]
        else: return None
        return json.dumps(question_dict, ensure_ascii = False)
# %% test Q2
# q2=Q2()
# for i in range(3):
#     q2_json_eng=q2.make_json(passageID, passage, is_Korean=False)
#     if q2_json_eng!=None: break
#     time.sleep(10)    ## RateLimitError 피하기

# print(q2_json_eng)
#%% 36-37, 43(순서(ABC)): 영어 보기
class Q3:
    def __init__(self):
        self.question_type=3
        self.question='주어진 글 다음에 이어질 글의 순서로 가장 적절한 것을 고르시오.'

    def separate(self, passage:str):

        sent=sent_tokenize(passage)
        sent_num=len(sent)
        output_passage_list=[]
        new_passage=sent[0]+'\n\n'

        a=int((sent_num-1)/3)
        if a==0: return None

        output_passage_list.append(sent[1:1+a])
        output_passage_list.append(sent[1+a:1+2*a])
        output_passage_list.append(sent[1+2*a:])

        dist_list=[['A','C','B'],['B','A','C'],['B','C','A'],['C','A','B'],['C','B','A']]
        ansidx=random.randint(0, 4)    ## ans: 0~4

        output=[0 for i in range(3)]
        outputidx_dict={'A':0, 'B':1, 'C':2}

        for i in range(3):
            outputidx=outputidx_dict[dist_list[ansidx][i]]
            sent='('+dist_list[ansidx][i]+')   '
            for j in output_passage_list[i]:
                sent=sent+j
            output[outputidx]=(sent.replace('.', '. '))

        for i in output:
            new_passage=new_passage+'\n'+i

        for i in range(len(dist_list)):
            ex_str=''
            for j in dist_list[i]:
                ex_str=ex_str+'('+j+')\t'
            dist_list[i]=ex_str.strip().replace('\t', '-')

        return new_passage, ansidx, dist_list

    def make_json(self, passageID:int, passage:str)->dict:
        question_dict=question_dict_sample.copy()
        
        question_dict['passageID']=int(passageID)
        question_dict['question_type']=self.question_type
        question_dict['question'] = self.question

        separate_output = self.separate(passage)
        if separate_output == None: return None
        new_passage, ansidx, ex_list=separate_output[0], separate_output[1], separate_output[2]

        question_dict['new_passage'] = new_passage
        question_dict['answer']=ansidx+1


        if len(ex_list)==5:
            question_dict['e1']=ex_list[0]
            question_dict['e2']=ex_list[1]
            question_dict['e3']=ex_list[2]
            question_dict['e4']=ex_list[3]
            question_dict['e5']=ex_list[4]
        else:
            return None
        return json.dumps(question_dict, ensure_ascii = False)
# %% test Q3
# q3=Q3()
# for i in range(3):
#     q3_json=q3.make_json(passageID, passage)
#     if q3_json!=None: break
#     time.sleep(10)  ## RateLimitError 피하기
# print(q3_json)
#%% 31(빈칸추론(단어)): 영어 보기
class Q4:
    def __init__(self):
        self.question_type = 4
        self.question = '다음 빈칸에 들어갈 말로 가장 적절한 것을 고르시오'

    def get_ans(self, passage:str)->str:
        kwd_list = get_kwd_n_list(passage, 1)
        if kwd_list == None: return None
        return kwd_list[0][0]

    def get_dist(self, kwd:str)->list:    ## 오답 단어 4개 만들기
        kwd_lmtzr=get_lmtzr(kwd)

        antonym= get_antonym_list_gpt(kwd_lmtzr, 5)
        if antonym == None: return None
        antonym_list, _ = antonym[0], antonym[1]

        synonym = get_synonym_list_gpt(kwd_lmtzr, 5)
        if synonym == None: return None
        synonym_list, _ = synonym[0], synonym[1]

        if len(antonym_list)+len(synonym_list) < 4: return None
        if len(antonym_list)+len(synonym_list) == 4: return antonym_list+synonym_list

        distractors_pre = del_same_start(del_same_lemmatization(antonym_list+synonym_list))
        if distractors_pre == None or len(distractors_pre) == 0: return None

        ## 정답과 4글자 이상 유사한거 삭제, None이 선지에 들어가지 않도록 처리하기
        distractors = []
        if len(kwd) >= 4:
            kwd_start = kwd[:4]
        else: kwd_start = kwd
        for i in distractors_pre:
            if kwd_start not in i and i != 'None':
                distractors.append(i)

        if len(distractors) < 4: return None
        distractors = random.sample(distractors, 4)
        return distractors

    def make_new_passage(self, passage:str, answer:str)->str:
        space = '_'*int(len(answer)*0.6)

        cnt_ans = passage.count(answer)
        cnt_ans_l = passage.count(answer.lower())
        
        if cnt_ans == 0 and cnt_ans_l == 0: return None

        elif cnt_ans == 0 and cnt_ans_l == 1:
            new_passage = passage.replace(answer.lower(), space, 1)

        elif cnt_ans == 0 and cnt_ans_l > 1: 
            loc = random.randint(1, cnt_ans_l)

            new_passage = passage.replace(answer.lower(), space, loc)
            new_passage = new_passage.replace(space, answer.lower(), loc-1)

        elif cnt_ans == 1: 
            new_passage = passage.replace(answer, space, 1)

        else:
            loc = random.randint(1, cnt_ans_l)
            new_passage = passage.replace(answer.lower(), space, loc)
            new_passage = new_passage.replace(space, answer.lower(), loc-1)

        return new_passage

      
    def make_json(self, passageID:int, passage:str):
        question_dict = question_dict_sample.copy()
        question_dict['passageID'] = int(passageID)
        question_dict['question_type'] = self.question_type
        question_dict['question'] = self.question

        ans = self.get_ans(passage)
        if ans == None: 
            return None

        dist_list = self.get_dist(ans)    ## list(4개)
        if dist_list == None: 
            return None


        new_passage=self.make_new_passage(passage, ans)   ##str
        if new_passage==None: 
            return None

        question_dict['new_passage']=new_passage

        ansidx=random.randint(0, 4)    ## ans: 0~4
        question_dict['answer']=ansidx+1
        dist_list.insert(ansidx, ans)

        ex_list=[]
        for w in dist_list:
            ex_list.append(w.capitalize().strip())

        if len(ex_list) == 5:
            question_dict['e1']=ex_list[0]
            question_dict['e2']=ex_list[1]
            question_dict['e3']=ex_list[2]
            question_dict['e4']=ex_list[3]
            question_dict['e5']=ex_list[4]
        else: 
            return None
        return json.dumps(question_dict, ensure_ascii = False)
# %% test Q4
# q4=Q4()
# for i in range(3):
#     q4_json=q4.make_json(passageID, passage)
#     if q4_json!=None: break
#     time.sleep(10)  ## RateLimitError 피하기
# print(q4_json)
#%% 30, 42(적절하지 않은 단어)
class Q5:
    def __init__(self):
        
        self.question_type=5
        self.question='다음 글의 밑줄 친 부분 중, 문맥상 낱말의 쓰임이 적절하지 않은 것은?'

    def get_keyword_list(self, passage: str)->list:
        kwd=get_kwd_n_list(passage, 5)
        if kwd == None: return None
        if kwd[1] == False: return None
        return kwd[0]

    def get_antonym_and_ansidx(self, passage:str, kwd_list:list)->str:
        ansidx_list=[]
        antonym_list=[]
        ansidx = -1

        for i in range(len(kwd_list)):
            keyword=kwd_list[i]
            antonym = get_antonym_list_gpt(keyword, 1)
            if antonym != None:
                antonym_w = antonym[0][0]
                ansidx = i
                break
            time.sleep(5)
            if ansidx < 0: return None

        return antonym_w, ansidx

    def make_new_passage_exlist_ansidx(self, passage:str, keyword_list:list, tmp_ansidx:int, antonym:str):
        new_passage=''+passage

        if len(keyword_list) !=5: return None

        for i in range(len(keyword_list)):
            kwd=keyword_list[i]
            space = '(__index__) '+kwd

            if i == tmp_ansidx: space = '(__index__) '+ antonym
            cnt_kwd = passage.count(kwd)
            cnt_kwd_l = passage.count(kwd.lower())

            if cnt_kwd == 0 and cnt_kwd_l == 0: 
                return None

            elif cnt_kwd == 0 and cnt_kwd_l == 1:
                new_passage = new_passage.replace(kwd.lower(), space.lower(), 1)

            elif cnt_kwd == 0 and cnt_kwd_l > 1: 
                loc = random.randint(1, cnt_kwd_l)
                new_passage = new_passage.replace(kwd.lower(), space.lower(), loc)
                new_passage = new_passage.replace(space.lower(), kwd.lower(), loc-1)

            elif cnt_kwd == 1: 
                new_passage = new_passage.replace(kwd, space, 1)

            else:
                loc = random.randint(1, cnt_kwd_l)
                new_passage = new_passage.replace(kwd.lower(), space.lower(), loc)
                new_passage = new_passage.replace(space.lower(), kwd.lower(), loc-1)
        
        new_passage_word=word_tokenize(new_passage)
        ex_list=[]

        for i in range(len(new_passage_word)):
            if new_passage_word[i] == '(__index__)' or (new_passage_word[i-1].endswith('_') and new_passage_word[i]==')'):
                ex_list.append(new_passage_word[i+1])

        for i in range(5):
            new_passage = new_passage.replace('(__index__)', '('+str(i+1)+')', 1)
        
        if antonym in ex_list:
            ansidx=ex_list.index(antonym)
        elif antonym.lower() in ex_list:
            ansidx=ex_list.index(antonym.lower())

        else: return None

        return new_passage, ex_list, ansidx
    
    def make_json(self, passageID:int, passage:str):
        question_dict=question_dict_sample.copy()
        question_dict['passageID']=int(passageID)
        question_dict['question_type']=self.question_type
        question_dict['question'] =self.question
        
        keyword_list=self.get_keyword_list(passage)
        if keyword_list == None or len(keyword_list) == 0: 
            # print(question_dict['passageID'], ': keyword_list == None' )
            return None

        get_antonym_and_ansidx_output=self.get_antonym_and_ansidx(passage, keyword_list)
        if get_antonym_and_ansidx_output == None: 
            # print(question_dict['passageID'], ': get_antonym_and_ansidx == None' )
            return None
        antonym, tmp_ansidx = get_antonym_and_ansidx_output[0], get_antonym_and_ansidx_output[1]


        output= self.make_new_passage_exlist_ansidx(passage, keyword_list, tmp_ansidx, antonym)
        if output == None: 
            # print(question_dict['passageID'], ': make_new_passage_exlist_ansidx == None' )
            return None
        new_passage, ex_list,ansidx = output[0], output[1], output[2]
        
        question_dict['new_passage']=new_passage
        question_dict['answer']=ansidx+1


        if len(ex_list)==5:
            question_dict['e1'] = ex_list[0].capitalize().strip()
            question_dict['e2'] = ex_list[1].capitalize().strip()
            question_dict['e3'] = ex_list[2].capitalize().strip()
            question_dict['e4'] = ex_list[3].capitalize().strip()
            question_dict['e5'] = ex_list[4].capitalize().strip()
        else: 
            # print(question_dict['passageID'], ': ex_list == None' )
            return None
        return json.dumps(question_dict, ensure_ascii = False)
# %% test Q5
# q5=Q5()
# for i in range(3):
#     q5_json=q5.make_json(passageID, passage)
#     if q5_json!=None: break
#     time.sleep(10)  ## RateLimitError 피하기
# print(q5_json)
#%% 38-39 문장이 들어가기에 적절한 곳
class Q6:
    def __init__(self):
        self.question_type=6
        self.question='글의 흐름으로 보아, 주어진 문장이 들어가기에 가장 적절한 곳을 고르시오.'
    
    def separate(self,passage:str):
        sent=sent_tokenize(passage)
        s_sentence=sent[0]
        sent.remove(s_sentence)

        ans_sentence=random.choice(sent)
        ansidx=sent.index(ans_sentence)
        sent.remove(ans_sentence)

        if len(sent) < 5: return None
        sample = random.sample(sent, 5)

        cnt=1
        for i in range(len(sent)):
            if sent[i] in sample:
                sent[i]='('+str(cnt)+') '+sent[i]
                cnt+=1
        new_passage=ans_sentence+'\n\n'+s_sentence
        for i in sent:
            new_passage=new_passage+i
        
        return new_passage, ansidx


    def make_json(self, passageID:int, passage:str):# , passage:str)->dict:
        # 글의 흐름으로 보아, 주어진 문장이 들어가기에 가장 적절한 곳을 고르시오.
        question_dict=question_dict_sample.copy()
        
        question_dict['passageID']=int(passageID)
        question_dict['question_type']=self.question_type
        question_dict['question'] = self.question

        separate_output=self.separate(passage)
        if separate_output==None : return None
        new_passage, ansidx=separate_output[0], separate_output[1]
        
        question_dict['new_passage'] = new_passage
        question_dict['answer']=ansidx+1

        question_dict['e1'] = '1'
        question_dict['e2'] = '2'
        question_dict['e3'] = '3'
        question_dict['e4'] = '4'
        question_dict['e5'] = '5'
        return json.dumps(question_dict, ensure_ascii = False)
# %% test Q6
# q6=Q6()
# for i in range(3):
#     q6_json=q6.make_json(passageID, passage)
#     if q6_json!=None: break
#     time.sleep(10)  ## RateLimitError 피하기
# print(q6_json)
#%% 35 전체 흐름과 관계 없는 문장
class Q7:
    def __init__(self):
        self.question_type=7
        self.question='다음 글에서 전체 흐름과 관계 없는 문장은?'

    def get_ans(self, passage: str)->str:
        return get_false_sentences_1(passage).strip()

    def make_new_passage_and_ansidx(self, passage: str, answer: str)->str:
        sent=sent_tokenize(passage)
        s_sentence=sent[0]
        sent.remove(s_sentence)
        new_passage=s_sentence

        if len(sent) < 5: return None
        sample=random.sample(sent, 5)
        ansidx=random.randint(0, 4)

        cnt=0
        for i in range(len(sent)):
            if sent[i] in sample:
                snt = '('+str(cnt+1)+')'+sent[i]
                if cnt == ansidx:
                    tmp=sent[i]
                    snt ='('+str(cnt+1)+')'+answer+' '+tmp
                sent[i]=snt
                cnt+=1
        for i in sent:
            new_passage=new_passage+' '+i
        return new_passage, ansidx

    def make_json(self, passageID:int, passage:str)->dict:
        question_dict=question_dict_sample.copy()
        
        question_dict['passageID']=int(passageID)
        question_dict['question_type']=self.question_type
        question_dict['question'] = self.question   ## 다음 글에서 전체 흐름과 관계 없는 문장은?

        ans_sent=self.get_ans(passage)  ## list5개
        if ans_sent == None : return None

        make_new_passage_and_ansidx_output=self.make_new_passage_and_ansidx(passage, ans_sent)    ## dict
        if make_new_passage_and_ansidx_output == None: return None
        new_passage, ansidx = make_new_passage_and_ansidx_output[0], make_new_passage_and_ansidx_output[1]
        
        question_dict['new_passage'] = new_passage
        question_dict['answer'] = ansidx+1
        question_dict['e1'] = '1'
        question_dict['e2'] = '2'
        question_dict['e3'] = '3'
        question_dict['e4'] = '4'
        question_dict['e5'] = '5'
        return json.dumps(question_dict, ensure_ascii = False)
# %% test Q7
# q7=Q7()
# for i in range(3):
#     q7_json=q7.make_json(passageID, passage)
#     if q7_json!=None: break
#     time.sleep(10)  ## RateLimitError 피하기
# print(q7_json)
#%% 40 글의 내용 요약하고 빈칸 2개 단어 고르기
class Q8:
    def __init__(self):
        self.question_type=8
        self.question='다음 글의 내용을 요약하고자 한다. 빈칸 (A), (B)에 들어갈 말로 가장 적절한 것은?'

    def paraphrase(self, passage:str)->str:
        return get_paraphrased_sentences_1(passage)

    def get_keyword(self, paraphrase:str) ->list:
        keyword= get_kwd_n_list(paraphrase, 2)
        if keyword == None: return None
        if keyword[1] == False: return None
        return keyword[0]
    
    def get_distractors_fromPassage(self, passage:str, keyword:list, paraphrase:str)->list:    ## 오답 단어 2개 만들기
        kwd=get_kwd_n_list(passage, 5)

        if kwd == None: return None
        kwd_list, _ = kwd[0], kwd[1]

        passage_keyword=del_same_start(del_same_lemmatization(kwd_list+keyword))
        if passage_keyword == None: return None

        passage_dist_list=[]
        for i in passage_keyword:
            if i.lower() not in paraphrase.lower():
                passage_dist_list.append(i)

        if len(passage_dist_list) == 0: return None
        return passage_dist_list
    
    def get_distractors_fromWord(self, keyword: str):
        synonym=get_synonym_list_gpt(keyword, 2)
        if synonym == None: synonym_list=[]
        else: synonym_list = synonym[0]

        time.sleep(2)

        antonym=get_antonym_list_gpt(keyword, 2)
        if antonym == None: antonym_list=[]
        else: antonym_list = antonym[0]

        return synonym_list, antonym_list

    def get_distractors(self, passage:str, keyword:list, paraphrase:str)->list:
        a, b=keyword[0], keyword[1]

        a_synonym_list, a_antonym_list = self.get_distractors_fromWord(a)
        b_synonym_list, b_antonym_list = self.get_distractors_fromWord(b)
        if a_synonym_list + a_antonym_list == [] or b_synonym_list + b_antonym_list == []: return None

        passage_dist_list=self.get_distractors_fromPassage(passage, keyword, paraphrase)
        if passage_dist_list== None: passage_dist_list = []

        a_dist=[]; b_dist=[]    ## 둘 다 3개

        if len(a_synonym_list) >= 1 and len(a_antonym_list) >= 2:
            a_dist=[random.choice(a_synonym_list)]+random.sample(a_antonym_list, 2)
        elif len(a_synonym_list) + len(a_antonym_list) >= 3 :
            a_dist=random.sample(a_synonym_list+a_antonym_list, 3)
        elif len(a_synonym_list) + len(a_antonym_list) + len(passage_dist_list) >= 3 :
            a_dist=random.sample(a_synonym_list+a_antonym_list+passage_dist_list, 3)

        
        if len(b_synonym_list) >= 1 and len(b_antonym_list) >= 2:
            b_dist=[random.choice(b_synonym_list)]+random.sample(b_antonym_list, 2)
        elif len(b_synonym_list) + len(b_antonym_list) >= 3 :
            b_dist=random.sample(b_synonym_list+b_antonym_list, 3)
        elif len(b_synonym_list) + len(b_antonym_list) + len(passage_dist_list) >= 3 :
            b_dist=random.sample(b_synonym_list+b_antonym_list+passage_dist_list, 3)
        
        if a_dist==[] or b_dist==[]: return None

        dist_list_pre=[]
        idx = 0

        for a in a_dist:
            for b in b_dist:
                if a!=b:  dist_list_pre.append((a, b))
    
        while True:
            dist_list=random.sample(dist_list_pre, 4)
            a_dist=[];b_dist=[]
            for i in dist_list:
                a_dist.append(i[0])
                b_dist.append(i[1])
            if len(list(set(a_dist))) >= 2 and len(list(set(b_dist))) >= 2: 
                break
        return dist_list
        
    def make_new_passage(self, passage:str, paraphrase:str, keyword:list)->str:
        # self.question='다음 글의 내용을 요약하고자 한다. 빈칸 (A), (B)에 들어갈 말로 가장 적절한 것은?'
        new_passage=passage + '\n\n==>'
        new_paraphrase='' + paraphrase
        space='__(index)__'
        
        for kwd in keyword:
            if kwd in paraphrase or kwd.lower() in paraphrase:
                cnt_kwd = paraphrase.count(kwd)
                cnt_kwd_l = paraphrase.count(kwd.lower())
                # print(kwd, cnt_kwd, cnt_kwd_l)

                if cnt_kwd == 0 and cnt_kwd_l == 0: 
                    return None

                elif cnt_kwd == 0 and cnt_kwd_l == 1:
                    new_paraphrase = new_paraphrase.replace(kwd.lower(), space.lower(), 1)

                elif cnt_kwd == 0 and cnt_kwd_l > 1: 
                    loc = random.randint(1, cnt_kwd_l)
                    new_paraphrase = new_paraphrase.replace(kwd.lower(), space.lower(), loc)
                    new_paraphrase = new_paraphrase.replace(space.lower(), kwd.lower(), loc-1)

                elif cnt_kwd == 1: 
                    new_paraphrase = new_paraphrase.replace(kwd, space, 1)

                else:
                    loc = random.randint(1, cnt_kwd_l)
                    new_paraphrase = new_paraphrase.replace(kwd.lower(), space.lower(), loc)
                    new_paraphrase = new_paraphrase.replace(space.lower(), kwd.lower(), loc-1)
        
        ascci_A = 65  ##'A'의 아스키코드
        for i in range(new_paraphrase.count(space)):
            new_paraphrase = new_paraphrase.replace(space, '('+chr(ascci_A+i)+')', 1)

        new_passage = new_passage+new_paraphrase
        # print(new_passage)
        return new_passage

    def make_json(self, passageID:int, passage:str):
        question_dict=question_dict_sample.copy()
        question_dict['passageID']=int(passageID)
        question_dict['question_type']=self.question_type
        question_dict['question'] = self.question

        paraphrase=self.paraphrase(passage)   ## list
        if paraphrase == None: 
            return None
        paraphrase=check_punctuation_capital_sentence(paraphrase)
        if paraphrase == None: 
            return None

        keyword=self.get_keyword(paraphrase)    ## list
        if keyword == None: 
            return None

        new_passage=self.make_new_passage(passage, paraphrase, keyword) ## str
        if new_passage == None: 
            return None
        question_dict['new_passage'] = new_passage
        
        dist_list =self.get_distractors(passage, keyword, paraphrase)
        if dist_list==None: 
            return None

        ans=random.randint(0, 4)
        question_dict['answer']=ans+1

        ex_list = []
        for i in dist_list:
            ex_list.append('(A)'+i[0]+' (B) '+i[1])
        ex_list.insert(ans, '(A)'+keyword[0]+' (B) '+keyword[1])

        if len(ex_list)==5:
            question_dict['e1']=ex_list[0]
            question_dict['e2']=ex_list[1]
            question_dict['e3']=ex_list[2]
            question_dict['e4']=ex_list[3]
            question_dict['e5']=ex_list[4]
        else:
            return 
            None
        
        return json.dumps(question_dict, ensure_ascii = False)

# %% test Q8
# q8=Q8()
# for i in range(3):
#     q8_json=q8.make_json(passageID, passage)
#     if q8_json!=None: break
#     time.sleep(10)  ## RateLimitError 피하기
# print(q8_json)
# %%
## 8 단ㅓㅜ성을 바궈야ㄹㄷ,ㅅ
