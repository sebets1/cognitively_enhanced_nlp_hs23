#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:  Seraina Betschart
# date: 22.12.2023
# Course: Cognitively Enhanced NLP

import csv
import scipy.stats as stats
from transformers import BertTokenizer

# do I need the BERT tokenizer?
# tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)


def read_csv_file(csv_file):
    """open csv file, tokenize and clean-up data, save needed data"""
    with open(csv_file, "r", encoding="utf-8") as rows:

        rows = csv.reader(rows, delimiter=',')

        filtered_data = []

        for row in rows:
            if len(row) > 1:
                filtered_data.append([row[0], float(row[1])])
            else:
                filtered_data.append(row)

    return filtered_data


def read_txt_file(txt_file):
    """open txt file, tokenize and clean-up data, save needed data"""
    with open(txt_file, "r", encoding="utf-8") as file:

        filtered_data = []

        for line in file:
            ele=line.split("\t")
            if len(ele)>1:
                filtered_data.append([ele[0], float(ele[1])])
            else:
                filtered_data.append(ele)

    return filtered_data


def reverse_bert_tokenization(sent_list, score_list):
    current_word = ""
    current_score= 0
    remade_sent=[]
    add_score = []
    for i, tok in enumerate(sent_list):
        if "##" in tok:
            tok=tok[2:]
            current_word += tok
            current_score += score_list[i]
        elif "," == tok or "." == tok or "'" == tok or "’" == tok or "-" == tok:
            current_word += tok
            current_score += score_list[i]
        elif "s" == tok or ";" == tok or ":" == tok:
            current_word += tok
            current_score += score_list[i]
        else:
            if current_word != "":
                remade_sent.append(current_word)
                add_score.append(current_score)
            current_word = tok
            current_score = score_list[i]

    remade_sent.append(current_word)
    add_score.append(current_score)

    if len(remade_sent) != len(add_score):
        print("ERROR IN TOKENIZATION. Lengths don't match.")
        print(remade_sent)
        print(add_score)

    return remade_sent, add_score


def prepare_sent(filtered_data, bert_tok=False):
    """return a list with attention scores, separated by sentence and text"""
    sent_separated = []
    sent_scores = []
    sent_tokens = []
    text=[]
    for ele in filtered_data:
        if "XXX_Sentence" in ele[0]:
            if len(sent_scores)>0:
                if bert_tok==True:
                    sent_tokens, sent_scores = reverse_bert_tokenization(sent_tokens, sent_scores)
                text.append(sent_scores)
                sent_scores = []
                sent_tokens = []
        elif "XXX_Text" in ele[0]:
            if bert_tok == True:
                sent_tokens, sent_scores = reverse_bert_tokenization(sent_tokens, sent_scores)
            if len(sent_scores) > 0:
                text.append(sent_scores)
                sent_separated.append(text)

            sent_scores = []
            sent_tokens = []
            text = []
        else:
            sent_scores.append(ele[1])
            sent_tokens.append(ele[0])

    if bert_tok == True:
        sent_tokens, sent_scores = reverse_bert_tokenization(sent_tokens, sent_scores)
    text.append(sent_scores)
    sent_separated.append(text)

    if len(sent_separated[0])== 1:
        del sent_separated[0]
    # -------------------------------------------------------
    # control that number of sentences and texts is correct
    # for i, text in enumerate(sent_separated):
    #     print(f"Text {i+1}")
    #     for a, sent in enumerate(text):
    #         print(f"Sentence {a+1}")
    # -------------------------------------------------------
    return sent_separated


def spearman_correlation(x, y):
    r, p_value = stats.spearmanr(x, y)
    return r, p_value


def pearson_correlation(x, y):
    r, p_value = stats.pearsonr(x, y)
    return r, p_value


def calculate_correlations(scores1, scores2, corr_metric="spearman"):
    """Take two lists of scores (format [text[sent[scores]]]) and calculate either pearson or spearman correlation"""
    sum_r=0
    sum_p_value=0
    sum_sent=0
    for i, text in enumerate(scores1):
        print(40*"-")
        print(f"Text number {i+1}")
        for n, sent in enumerate(text):
            if len(sent)==len(scores2[i][n]):
                if corr_metric == "spearman":
                    r, p_value= spearman_correlation(sent, scores2[i][n])
                if corr_metric == "pearson":
                    r, p_value = pearson_correlation(sent, scores2[i][n])
                print(f"Sentence {n+1}: r={r}, p-value={p_value}")
                sum_r += r
                sum_p_value+= p_value
                sum_sent+=1
            else:
                print(f"########Length didn't match for sentence {n+1} in text {i+1}.########")
    avg_r = sum_r/sum_sent
    avg_p_value = sum_p_value/sum_sent
    print(40 * "-")
    print(f"\nTotal values: r={avg_r}, p-value={avg_p_value}")

    return avg_r, avg_p_value


def evaluation(input1, input2, bert_tok1=False, bert_tok2=False):
    """Calculate pearson and spearman correlations of the two given input files"""
    machine_data = read_txt_file(input1)
    machine_sent_sep = prepare_sent(machine_data, bert_tok=bert_tok1)
    eyegaze_data = read_txt_file(input2)
    eyegaze_sent_sep = prepare_sent(eyegaze_data, bert_tok=bert_tok2)
    pears_r, pears_p = calculate_correlations(machine_sent_sep, eyegaze_sent_sep, corr_metric="pearson")
    spear_r, spear_p = calculate_correlations(machine_sent_sep, eyegaze_sent_sep, corr_metric="spearman")
    return pears_r, pears_p, spear_r, spear_p


if __name__ == '__main__':
    language_list = ["Dutch", "Estonian", "Finnish", "German", "Greek", "Hebrew", "Italian", "English", "Norwegian",
                     "Russian", "Spanish", "Turkish"]

    # define first input file and state if the words have been tokenized with BERT
    input_file1 = 'data/transformer_attention_scores/transformer_att_scores_paragraph_cls.txt'
    bert_tok_file1 = True

    # input_file1 = "data/lang_fixation_attention_scores/fixation_attention_full_English.txt"
    # bert_tok_file1 = False

    results = []

    # iterate through files of all languages and calculate correlation of each one with input_file1
    for lang in language_list:
        input_file2 = f"data/lang_fixation_attention_scores/fixation_attention_full_{lang}.txt"
        bert_tok_file2 = False
        pears_r, pears_p, spear_r, spear_p = evaluation(
            input_file1, input_file2, bert_tok1=bert_tok_file1, bert_tok2=bert_tok_file2)
        results.append([pears_r, pears_p, spear_r, spear_p])

    # ----------------------------------------------------------------------------------------------------
    # print a nice output
    print("\n\n")
    print("language     |pearson corr |p-value      |spearman corr|p-value     ")
    print(13 * " ")
    for i, lang in enumerate(language_list):
        print(lang + (13 - len(lang)) * " "+"|" +
              2*" ", str(round(results[i][0], 2))+ (10-len(str(round(results[i][0],2))))* " "+"|" +
              2*" ", str(round(results[i][1], 2))+ (10-len(str(round(results[i][1],2))))* " "+"|" +
              2*" ", str(round(results[i][2], 2))+ (10-len(str(round(results[i][2],2))))* " "+"|" +
              2*" ", str(round(results[i][3], 2)) )


# ----------------------------------------------------------------------------------------------------
# some tests:

# sent = [["I", 0.3], ["superiokland", 0.2], ["if", 0.1], ["Antarctica", 0.2], ["don't", 0.15]]
# input=""
# for ele in sent:
#     input+=ele[0]
#     input+= " "
#
# sentence = "This is an example sentence for tokenization."
# tokens = tokenizer.tokenize(sentence)
# print(tokens)
#
# print(input)
# tokens = tokenizer.tokenize(input)
# print(tokens)





