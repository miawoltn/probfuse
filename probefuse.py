#!/usr/bin/env python
# coding: utf-8

# In[1]:


import csv
from pathlib import Path


# In[2]:


def load_file(filename):
    # compile ir queries in a list
    file_content = []
    try:
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                file_content.append(row);
        return file_content
    except:
        print("Unable to read file.")
#         exit();


# In[3]:


def read_ir_queries(hr_results): 
    ir_a = list()
    ir_b = list()
    ir_c = list()
    ir_d = list()
    for row in hr_results:
        if 'A' in row[0]:
            ir_a.append(row[1:])
        if 'B' in row[0]:
            ir_b.append(row[1:])
        if 'C' in row[0]:
            ir_c.append(row[1:])
        if 'D' in row[0]:
            ir_d.append(row[1:])
    return [ir_a, ir_b, ir_c, ir_d]


# In[4]:


def get_user_input(message):
    return input(message);


# In[5]:


def get_file_content(filename):
    file_path = Path(filename+".csv")
    if file_path.is_file():
        file_content = load_file(file_path.name)
        return file_content
    else:
        raise ValueError()


# In[6]:


def get_ir_queries():
    filename = get_user_input("Enter historical result file name: ")
    try:
        while True:
            ir_queries = read_ir_queries(get_file_content(filename)); 
            return ir_queries
    except:
        print('can\'t open '+filename)
        get_ir_queries()


# In[7]:


def get_segment_count():
    try:
        while True:
            segment_count = int(get_user_input("Enter number of segments: "))
            return segment_count
    except:
        print('invalid input')
        get_segment_count()


# In[8]:


def get_results_to_fuse():
    ir_dic = {"A":1, "B":2, "C":3, "D":4}
    results_to_fuse = {}
    try:
        while True:
            irs_to_fuse = get_user_input("What result do you want to fuse out? Enter any combination of A, B, C, or D separated by comma: ")
            irs = irs_to_fuse.split(",")
            if(len(irs) < 2):
                raise ValueError()
            for ir in irs_to_fuse.split(","):
                if ir not in ir_dic:
                    raise ValueError()
                results_to_fuse[ir] = ir_dic.get(ir)
            return results_to_fuse
    except:
        print('invalid input')
        get_results_to_fuse()


# In[9]:


def segment(alist, wanted_parts=1):
    length = len(alist)
    return [alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ]


# In[10]:


# ir queries are read separately per line
# this will put similar queries in the same segment in list 
# in order to calculate their weights
def merge_similar_segment_queries(segmented_ir):
    ir_seg_dic = {}
    for index, segment in enumerate(segmented_ir):
        for idx, sub_segment in enumerate(segment):
            if idx not in ir_seg_dic:
                ir_seg_dic[idx] = list()
            ir_seg_dic[idx].append(sub_segment)
    return ir_seg_dic


# In[11]:


def get_segment_weight(segment, segment_number):
    query_count = 0
    query_probability = []
    for query in segment:
        query_count += 1
        relevant_query_count = query.count('R')
        relevant_query_probability = round(relevant_query_count/len(query),1)
        query_probability.append(relevant_query_probability)
    segment_probability = round(sum(query_probability)/query_count, 1)   
    segment_weight = segment_probability/segment_number
    return segment_weight


# In[12]:


# segment subqueries for a specific ir 
# eg IR A1, A2,...
def segment_ir_subqueries(ir_sub_queries):
    ir_segmented_subquery = []
    for query in ir_sub_queries:
        ir_segmented_subquery.append(segment(query, seg_count))
    return ir_segmented_subquery


# In[13]:


# goes through all the irs and segment their queries
# eg. IR A, B, C,...
def segment_ir_queries(ir_queries):
    ir_segmented_queries = []
    for ir_sub_query in ir_queries:
        ir_segmented_queries.append(segment_ir_subqueries(ir_sub_query))
    return ir_segmented_queries


# In[14]:


def merge_ir_segments(ir_segmented_queries):
    merged_ir_segments = []
    for ir_seg_query in ir_segmented_queries:
        merged_ir_segments.append(merge_similar_segment_queries(ir_seg_query))
    return merged_ir_segments


# In[15]:


def get_ir_segments_weight(merged_ir_segment):    
    ir_seg_weight_dic = {}
    precision = 1
    for key in merged_ir_segment:
        ir_seg_weight_dic[key] = round(get_segment_weight(merged_ir_segment[key], key+1), precision)
    return ir_seg_weight_dic


# In[16]:


def get_ir_segment_weights(merged_ir_segments): 
    ir_segment_weights = []
    for merged_ir_segment in merged_ir_segments:
        ir_segment_weights.append(get_ir_segments_weight(merged_ir_segment))
    return ir_segment_weights


# In[17]:


def read_liveresults(liveresults):  
    lr_a = []
    lr_b = []
    lr_c = []
    lr_d = []
#     try:
    for row in liveresults:
        if 'A' in row[0]:
            lr_a = (row[1:])
        if 'B' in row[0]:
            lr_b = (row[1:])
        if 'C' in row[0]:
            lr_c = (row[1:])
        if 'D' in row[0]:
            lr_d = (row[1:])
    return [lr_a, lr_b, lr_c, lr_d]
#     except:
#         print('unable to get Liveresults content')


# In[18]:


def get_liveresults():
    filename = get_user_input("Enter live result file name: ")
    try:
        while True:
            liveresults = read_liveresults(get_file_content(filename)); 
            return liveresults
    except:
        get_liveresults()


# In[19]:



def weight_liveresults(liveresults, results_to_fuse):
    liveresults_rating = []
    for index, liveresult in enumerate(liveresults):
        if index+1 not in results_to_fuse.values(): # only fuse results specified by user
            continue
        liveresults_dic = {}
        length = len(liveresult)
        batch_size = length//seg_count
        # loop results in batches to apply weights
        for i in range(0, length, batch_size): 
            batch = liveresult[i:i+batch_size]
            ir_weight = ir_weights[index] # get segment weights
            for indx, doc in enumerate(batch):
                liveresults_dic[doc] = ir_weight.get(i%4)
        liveresults_rating.append(liveresults_dic)
    return liveresults_rating


# In[20]:


def fuse_liveresult(weighted_liveresult):
    ranking_table = {}
    for index, weighted_liveresult in enumerate(weighted_liveresults):
        for key in weighted_liveresult:
            if key in ranking_table:
                ranking_table[key] = ranking_table.get(key) + weighted_liveresult.get(key)
            else:
                ranking_table[key] = weighted_liveresult.get(key)
    ranking_table = dict(sorted(ranking_table.items(), key=lambda item: item[1], reverse=True))
    return ranking_table


# In[21]:


def save_results():
    with open('result.csv', 'w') as csv_file:  
        writer = csv.writer(csv_file)
        for key, value in fused_result.items():
            writer.writerow([key, value])
    print('result.csv saved.')


# In[22]:


ir_queries = get_ir_queries()


# In[23]:


seg_count = get_segment_count()


# In[24]:


results_to_fuse = get_results_to_fuse()
results_to_fuse


# In[25]:


ir_segmented_queries = segment_ir_queries(ir_queries)


# In[26]:


merged_ir_segments = merge_ir_segments(ir_segmented_queries)


# In[27]:


ir_weights = get_ir_segment_weights(merged_ir_segments)


# In[28]:


liveresults = get_liveresults()


# In[29]:


weighted_liveresults = weight_liveresults(liveresults, results_to_fuse)


# In[30]:


fused_result = fuse_liveresult(weighted_liveresults)


# In[31]:


save_results()


# In[ ]:




