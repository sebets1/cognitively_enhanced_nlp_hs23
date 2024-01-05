#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:  Seraina Betschart
# date: 22.12.2023
# Course: Cognitively Enhanced NLP

import csv
import time



def tokenize_broken_rows(row):
    """ to fix rows which get saved as one long string instead of list and thus cause problems (apparently,
    as list didn't work because the word was followed by a comma. thus I also put a comma back in)."""
    for str_row in row:
        fixed_row=str_row.split(",")
        fixed_row[7]=fixed_row[7].replace('"', '')
        fixed_row[7]+=","
        del fixed_row[8]
        return fixed_row


def read_csv_file(csv_file):
    """opens a csv file, tokenizes and cleans up data, saves needed data"""
    with open(csv_file, "r", encoding="utf-8") as rows:

        rows = csv.reader(rows, delimiter=',')

        filtered_data = []
        first_row=True
        for row in rows:
            if first_row== True:
                first_row=False
            else:
                if len(row)<20:
                    fixed_row=tokenize_broken_rows(row)
                    row=fixed_row

                # important columns: col0 identifies subject, col3-text number, col5-> sentence number,
                # col6 -> word position in text, col7 -> word, col16 -> fixation duration

                # if no fixation duration value, set 0 as default to not have trouble with later calculations
                if len(row[16])==0:
                    row[16]=0
                filtered_row=[row[0], int(row[3]), int(row[5]), int(row[6]), row[7], int(row[16])]
                if len(filtered_row) !=6:
                    print(filtered_row)
                filtered_data.append(filtered_row)

    return filtered_data


def build_data(filtered_data_list, country_code):
    """use data from all participants of one country to get all the MECO sentences
     (one participant would not be enough because of trimming).
     Put the data in order and get a dictionary ordered by texts."""
    data_dict={}
    for row in filtered_data_list:
        if country_code in row[0]:
            if row[1] in data_dict:
                data_dict[row[1]].append(row)
            else:
                data_dict[row[1]]=[row]

    # sort every text i by item number (word number)
    for i in range(len(data_dict)):
        data_dict[i+1] = sorted(data_dict[i+1], key=lambda x: x[3])

    return data_dict


def build_dataset(participant_data_dict, filename):
    """Get rid of doubles and save all texts to a file."""
    data_dict=participant_data_dict
    all_texts=[]
    text_counter=1
    for i in range(len(data_dict)):
        act_sent = 1
        all_sent = []
        sent = []
        item_id_list = []
        all_sent.append([f'Text {text_counter}'])
        for row in data_dict[i+1]:
            if row[2] == act_sent:
                if row[3] not in item_id_list:  # to avoid doubles
                    sent.append(row[4])
                    item_id_list.append(row[3])
            else:
                all_sent.append(sent)
                sent = []
                act_sent += 1
        all_sent.append(sent)
        all_texts.append(all_sent)

        text_counter+=1

    for ele in all_texts:
        print(ele)

    with open(filename, 'w') as file:
        for text in all_texts:
            for sent in text:
                list_to_str = ' '.join([str(word) for word in sent])
                file.write(list_to_str)
                file.write("\n")
            file.write("\n")


if __name__ == '__main__':
    input_file = "meco_data2.csv"
    output_file = "data/meco_data.txt"

    filtered_data = read_csv_file(input_file)
    data_dict = build_data(filtered_data, "DU")
    build_dataset(data_dict, output_file)

