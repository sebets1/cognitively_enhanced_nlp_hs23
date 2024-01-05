#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:  Seraina Betschart
# date: 22.12.2023
# Course: Cognitively Enhanced NLP

import csv


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
    """open csv file, tokenize and clean-up data, return needed data"""
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
    """Build a dictionary for a chosen language with keys being the text numbers and values a list of lists with all
    tokens and their additional information."""
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


def build_participant_data(data_dict):
    """Calculate average fixation for every word and prepare a list adapted to the save_data_to_csv() function."""
    fixation_data_list = []
    text_counter = 1
    for i in range(len(data_dict)):
        act_sent = 1
        item_id_list = []
        fixation_data_list.append([f'XXX_Text {text_counter}'])
        fixation_no=0 # number of participants who have read the word (not every participant has read the same texts)
        fixation_tot=0 # sum of all participants' fixation duration for the word
        for int, row in enumerate(data_dict[i + 1]):

            if row[2] == act_sent:
                if row[3] not in item_id_list:  # to avoid doubles
                    item_id_list.append(row[3])
                    if fixation_no>0:
                        fixation_avg=fixation_tot/fixation_no
                        fixation_data_list.append([data_dict[i+1][int-1][4], fixation_avg])
                    else:
                        fixation_data_list.append([f'XXX_Sentence {act_sent}'])
                    fixation_no=1
                    fixation_tot=row[5]
                else:
                    fixation_no += 1
                    fixation_tot += row[5]

            else:
                fixation_avg = fixation_tot / fixation_no
                fixation_data_list.append([data_dict[i + 1][int - 1][4], fixation_avg])
                fixation_no = 0
                act_sent += 1

        fixation_avg = fixation_tot / fixation_no
        fixation_data_list.append([data_dict[i + 1][int - 1][4], fixation_avg])
        # print(data_dict[i+1][int-1][4])
        text_counter += 1

    # ------------------------------------------------------------------
    # uncomment to check how many participants have read a certain text (eg the one with the word "luxurious"
    # for x in data_dict.values():
    #     for ele in x:
    #         if ele[4]== "luxurious":
    #             print(ele)
    # ------------------------------------------------------------------
    # uncomment to see the first 20 words and their data
    # for i in range(20):
    #     print(data_dict[1][i])
    # for i, ele in enumerate(fixation_data_list):
    #     if i<10:
    #         print(ele)
    # ------------------------------------------------------------------

    return fixation_data_list


def normalize_fixation_values(fixation_data):
    """Normalize fixation values across sentences"""
    sent_fixation = 0  # total fixation time for the sentence
    sent = []
    sent_count = 1
    text_count = 1
    norm_fixation_values = []
    for int, ele in enumerate(fixation_data):
        # if a list with two elements (word and score), add word to sentence and sum all scores to later calculate ratio
        if len(ele) == 2:
            sent_fixation += ele[1]
            sent.append(ele)

        elif "XXX_Sentence" in ele[0]:

            if "XXX_Text" in fixation_data[int - 1][0]:
                # to not forget to append the last sentences of a text
                if len(sent) > 0:
                    norm_fixation_values.append([f"XXX_Sentence{sent_count}"])
                    for token in sent:
                        norm_fixation = 1 / sent_fixation * token[1]
                        norm_fixation_values.append([token[0], norm_fixation])
                    sent = []
                    sent_fixation = 0

                norm_fixation_values.append([f"XXX_Text{text_count}"])
                text_count += 1
                sent_count = 1

            # calculate the ratio of attention for each token in the sentence and append sentence to output list
            if len(sent) > 0:
                norm_fixation_values.append([f"XXX_Sentence{sent_count}"])
                for token in sent:
                    norm_fixation = 1 / sent_fixation * token[1]
                    norm_fixation_values.append([token[0], norm_fixation])
                sent = []
                sent_fixation = 0
                sent_count += 1

    # to add the very last sentence
    if len(sent) > 0:
        norm_fixation_values.append([f"XXX_Sentence{sent_count}"])
        for token in sent:
            norm_fixation = 1 / sent_fixation * token[1]
            norm_fixation_values.append([token[0], norm_fixation])

    # ------------------------------------------------------------------
    # sum = 0
    # for i, ele in enumerate(norm_fixation_values):
    #     if i < 27:
    #         if len(ele)==2:
    #             sum+=ele[1]
    #         print(ele)
    # print(sum)
    # ------------------------------------------------------------------
    return norm_fixation_values


# ---------------------------------------------------------------------------------------------- #
# provide save to .txt file as I had more problems with .csv later
# ---------------------------------------------------------------------------------------------- #
def save_data_to_csv(fixation_data, output_file):
    """Take a list of lists [word, att_score] and save it to a csv file"""
    # open the file in the write mode
    with open(output_file, 'w') as f:
        # create the csv writer
        writer = csv.writer(f)

        for ele in fixation_data:
            writer.writerow(ele)


def save_data_to_txt(fixation_data, output_file):
    """Take a list of lists [word, att_score] and save it to a txt file, tab-separated (in case csv causes problems)"""
    # open the file in the write mode
    with open(output_file, 'w') as f:

        for ele in fixation_data:
            if len(ele)==2:
                str_ele=f"{ele[0]}\t{ele[1]}\n"
            elif len(ele)==1:
                str_ele=str(ele[0])
                str_ele += "\n"
            f.write(str_ele)


def save_to_text_format(fixation_data, output_file, file_format):
    """saves the computed data in a chosen file format. Calls save data to txt/csv"""
    output_f = f"{output_file}.{file_format}"
    print(output_f)
    if file_format=="csv":
        save_data_to_csv(fixation_data, output_f)
    if file_format== "txt":
        save_data_to_txt(fixation_data, output_f)
    else:
        print(f"Chosen file format '{file_format}' not valid. Output was not saved.")


# ---------------------------------------------------------------------------------------------- #
def build_one_language():
    """to test functions, extract values for one language on small input file"""
    input_file = "short_meco_data_for_testing.csv"
    language = "DU"
    output_file = "data/fixation_attention_dutch_test"
    file_format = "txt"
    filtered_data = read_csv_file(input_file)
    data_dict = build_data(filtered_data, language)

    fixation_values = build_participant_data(data_dict)
    norm_fixation_values = normalize_fixation_values(fixation_values)
    save_to_text_format(norm_fixation_values, output_file, file_format)


def build_n_languages(input_f, lang_list, lang_data_names_list, output_f, file_format):
    """run all functions on all languages and save an output file for every language"""
    input_file = input_f
    filtered_data = read_csv_file(input_file)

    for i, lang in enumerate(lang_list):
        print(f"\nCurrent language: {lang}\n")
        output_file = f"{output_f}_{lang}"
        data_dict = build_data(filtered_data, lang_data_names_list[i])
        fixation_values = build_participant_data(data_dict)
        norm_fixation_values = normalize_fixation_values(fixation_values)
        save_to_text_format(norm_fixation_values, output_file, file_format)
# ---------------------------------------------------------------------------------------------- #


if __name__ == '__main__':
    # build_one_language()

    # ----------------------------------------
    input_file = "meco_data2.csv"

    language_list = ["Dutch", "Estonian", "Finnish", "German", "Greek", "Hebrew", "Italian", "English", "Norwegian",
                     "Russian", "Spanish", "Turkish"]
    lang_data_names = ["DU", "ee", "fi", "ger", "Gr", "HEB", "L2", "macmo", "NO", "ru", "spa", "tr"]

    output_file = "data/fixation_attention_full"
    file_format = "txt"  # "txt" or "csv"

    build_n_languages(input_file, language_list, lang_data_names, output_file, file_format)
    # ----------------------------------------





