#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:  Seraina Betschart
# date: 22.12.2023
# Course: Cognitively Enhanced NLP

from transformers import BertTokenizer, BertModel
import csv


def get_attention_weights_cls(input_sent):
    """Take a sentence and extract the attention each token gets from the [cls] special token after the first layer.
        Return a list with token-attention score pairs."""
    inputs = tokenizer.encode_plus(input_sent, return_tensors='pt', add_special_tokens=True)
    input_ids = inputs['input_ids']
    token_type_ids = inputs['token_type_ids']

    # Get attention weights
    attention = model(input_ids, token_type_ids=token_type_ids)[-1]
    # get attention weights from the first layer
    attention_l1 = attention[0][0].detach().numpy()

    # Access the attention scores for the [CLS] token in the first layer
    cls_attention_scores_l1 = attention_l1[0, 0, :].tolist()

    # Tokenize the sentence
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0])

    # Create a dictionary to store attention scores for each word
    word_attention_list=[]

    # Iterate through each word and its attention scores
    for i, word in enumerate(tokens):
        # Extract the attention scores for the [CLS] token in the first layer for the current word
        att_scores=cls_attention_scores_l1[i]
        # Store the attention scores in the dictionary as a list
        word_attention_list.append([word, att_scores])

    word_attention_list_avg = []
    for ele in word_attention_list:
        # Calculate the average attention score for each word
        avg_attention = ele[1]
        word_attention_list_avg.append([ele[0], avg_attention])


    return word_attention_list_avg


def get_attention_weights_avg_all_tokens(input_sent):
    """Take a sentence and calculate the average attention each token gets from the other tokens after the first layer.
    Return a list with token-attention score pairs."""
    inputs = tokenizer.encode_plus(input_sent, return_tensors='pt', add_special_tokens=True)
    input_ids = inputs['input_ids']
    token_type_ids = inputs['token_type_ids']  # Add this line to get token_type_ids

    # Get attention weights
    attention = model(input_ids, token_type_ids=token_type_ids)[-1]
    # get attention weights from the first layer
    attention_l1 = attention[0]

    # Access the attention scores for the [CLS] token in the first layer
    cls_attention_scores_l1 = attention_l1[0, 0, :].tolist()

    # Tokenize the sentence
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0])

    # Create a list to store attention scores for each word
    word_attention_list=[]

    # Iterate through each word and its attention scores
    for i, word in enumerate(tokens):
        # Extract the attention scores for the [CLS] token in the first layer for the current word
        att_scores=cls_attention_scores_l1[i]
        # cls_attention_scores_l1 = attention_l1[0, i, :].tolist()  # Convert to list
        # Store the attention scores in the dictionary as a list
        word_attention_list.append([word, att_scores])



    # save the average attention scores every token gets
    word_attention_list_avg=[]
    for i, ele in enumerate(word_attention_list):
        word=ele[0]
        score=0
        for int in range(len(word_attention_list)):
            score+=word_attention_list[int][1][i]
        score=score/len(word_attention_list)
        word_attention_list_avg.append([word, score])

# to check output------------------
#     for ele in word_attention_list_avg:
#         n = 12 - len(ele[0])
#         print(ele[0]+n*" " + str(ele[1]))
# ----------------------------------
    return word_attention_list_avg


def sentence_normalization(word_att_list, piping="sentence"):
    if piping!="paragraph":
        # get rid of [CLS] and [SEP] tokens
        corr_list=word_att_list[1:-1]
    else:
        corr_list = word_att_list
    norm_att_scores=[]

    # get the updated total score (without special tokens) to normalize to 100%
    n=0
    for ele in corr_list:
        n+=ele[1]

    for ele in corr_list:
        att_score=ele[1]/n*1
        norm_att_scores.append([ele[0], att_score])

    print("\nNormalized attention scores of sentence:\n")
    for ele in norm_att_scores:
        n = 12 - len(ele[0])
        print(ele[0]+n*" " + str(ele[1]))
    print(50*"-")

    return norm_att_scores


def prepare_piping(input_file):
    """Tokenize input file to sentence and text separated list"""
    with open(input_file, "r", encoding="utf-8") as file:

        sent_list = []
        text_no = 1
        sent_no = 1

        for line in file:
            line=line[:-1]
            # target the lines with "Text No" which are longer than the empty lines but shorter than any of the meco sentences
            if len(line)>2 and len(line)<9:
                sent_list.append([f"XXX_Text{text_no}"])
                text_no += 1
                sent_no = 1
            elif len(line)>10:
                sent_list.append([f"XXX_Sentence{sent_no}"])
                sent_list.append([line])
                sent_no += 1

    return sent_list


def save_data_to_csv(norm_att_scores, file):
    """Take a list of lists [word, att_score] and save it to a csv file"""
    # open the file in the append mode
    with open(file, 'a') as f:
        # create the csv writer
        writer = csv.writer(f)

        for ele in norm_att_scores:
            writer.writerow(ele)


def save_data_to_txt(output_list, output_file):
    """Take a list of lists [word, att_score] and save it to a txt file, tab-separated (in case csv causes problems)"""
    with open(output_file, 'w') as f:

        for ele in output_list:
            if len(ele)==2:
                str_ele=f"{ele[0]}\t{ele[1]}\n"
            elif len(ele)==1:
                str_ele=str(ele[0])
                str_ele += "\n"
            f.write(str_ele)


def pipe_sentence_avg(input_sentence):
    print(50*"-")
    word_att_list=get_attention_weights_avg_all_tokens(input_sentence)
    norm_att_scores_list = sentence_normalization(word_att_list)
    return norm_att_scores_list


def pipe_sentence_cls(input_sentence, piping="paragraph"):
    print(50 * "-")
    word_att_list=get_attention_weights_cls(input_sentence)
    norm_att_scores_list = sentence_normalization(word_att_list)
    return norm_att_scores_list


def pipe_paragraph(sent_list, method="avg"):
    """Quite an unnecessarily complicated way to pip paragraphs through BERT and then average over sentences. As I added
    this code in the end it got very complicated (I first only piped sentences)."""
    piped_list = []
    output_list = []
    text = ""

    for ele in sent_list:
        if "XXX_Text" in ele[0]:
            if len(text) > 0:
                if method == "avg":
                    norm_att_scores = pipe_sentence_avg(text)
                if method == "cls":
                    norm_att_scores = pipe_sentence_cls(text)
                for token in norm_att_scores:
                    piped_list.append(token)
            piped_list.append(ele)
            text = ""
        elif "XXX" not in ele[0]:
            text+= ele[0]

    if len(text) > 0:
        if method == "avg":
            norm_att_scores = pipe_sentence_avg(text)
        if method == "cls":
            norm_att_scores = pipe_sentence_cls(text)
        for token in norm_att_scores:
            piped_list.append(token)

    text_index = 0
    sent_index = 1
    sent = []

    for i, ele in enumerate(piped_list):
        if "XXX_Text" in ele[0]:
            output_list.append(ele)
            text_index += 1
            sent_index = 1
            output_list.append(["XXX_Sentence1"])
        elif ele[0] == "." and len(piped_list[i-1][0])>1:
            sent.append(ele)
            output_list.append(sent)
            sent = []
            sent_index += 1
            if i < (len(piped_list)-1):
                if "XXX_Text" not in piped_list[i+1][0]:
                    sentence_no = "XXX_Sentence" + str(sent_index)
                    output_list.append([sentence_no])
        else:
            sent.append(ele)

    rev_output_list = []
    for sent in output_list:
        print(sent)
        if len(sent)>1:
            norm_att_scores = sentence_normalization(sent, piping="paragraph")
            for token in norm_att_scores:
                rev_output_list.append(token)
        else:
            rev_output_list.append(sent)

    return rev_output_list





def get_attention_scores(output_file, sent_list, method="avg", piping="paragraph"):
    output_list = []

    if piping == "paragraph":
        output_list = pipe_paragraph(sent_list, method)
    if piping == "sentence":
        for sent in sent_list:
            if "XXX" in sent[0]:
                output_list.append(sent)
            else:
                if method=="avg":
                    norm_att_scores = pipe_sentence_avg(sent[0])
                if method=="cls":
                    norm_att_scores = pipe_sentence_cls(sent[0])
                for token in norm_att_scores:
                    output_list.append(token)

    save_data_to_txt(output_list, output_file)


if __name__ == '__main__':
    # ---------------------------------------------------------------
    model = BertModel.from_pretrained('bert-base-uncased', output_attentions=True)
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
    # ---------------------------------------------------------------

    sentence_list = prepare_piping("data/meco_data.txt")

    output_file='data/transformer_att_scores_paragraph_avg.txt'
    # method: either avg or cls, piping: either paragraph or sentence
    get_attention_scores(output_file, sentence_list, method="avg", piping="paragraph")

    output_file = 'data/transformer_att_scores_paragraph_cls.txt'
    get_attention_scores(output_file, sentence_list, method="cls", piping="paragraph")

    # for testing--------------------
    # sent_list=[["I love dogs."], ["Nothing is real but don't not buy christmas trees. or tresss"]]
    # output_file = 'data/test_avg.txt'
    # get_attention_scores(output_file, sent_list, method="avg")
    #
    # output_file = 'data/test_cls.txt'
    # get_attention_scores(output_file, sent_list, method="cls")











