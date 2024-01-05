# Comparing Eye Data of Different L1 Speakers Reading in English to Attention Scores of BERT

This repository has been made as the final project for the course *Cognitively Enhanced NLP*.
It contains all scripts and files I produced trying to answer my research question:

**Is there a difference in correlation between model and human attention for groups of L2 English speakers with a different L1?** 

Please refer to the paper for more details.

## Purpose of the scripts

The purpose of the scripts is the following:

- extract data from the MECO corpus
- pipe sentences through the bert-base uncased model and extract first-layer attention scores
- get average fixation scores for every token for each language
- average and normalize these scores
- calculate correlation between two sets of attention scores



## How to run the scripts



The scripts should be run in the following order:

### convert_rda_to_csv.R
This script extracts the data from the MECO corpus and saves it into a CSV file.

**To run the script**:
- Get the openly available MECO eye data corpus here https://osf.io/q9h43/
- Adapt paths in script and run it

------------------------------------------------------
### build_meco_data.py
This script returns a text file extracting all texts and sentences from the CSV file of MECO data created previously.

**To run the script**:
- Adapt the information for the *input_file* on line 110 and *output_file* on line 111

------------------------------------------------------
### get_attention_values_eye_data.py
This script takes the total fixation duration of every token and averages the value across all tokens with the same id
(aka same words) for all participants of one language. The values are then averaged across sentence.
The output is a separate file for every language with all the averaged fixation duration scores 
(used as human attention) for each word.

**To run the script**:
- For testing: uncomment line 254
and possibly adapt *input_file* and *output_file* in the function def build_one_language().
Comment the other lines in \_\_name__ == '\_\_main__'
- Run all: Adapt the *input_file* on line 257 and the *output_file* on line 263

------------------------------------------------------
### get_attention_weights_bert.py
This script pipes the sentences of the MECO corpus through a BERT model and extracts the first-layer attention scores.
It takes either the [CLS] query or the averages attention over all queries and does sentence normalization.
The values are then averaged across sentence.
The output is a file for the final scores in the same format as the language files from the get_attention_values_eye_data.py.


**To run the script**:
- Check that the filename for the MECO file on line 278 is correct
- Choose a name for the output file on line 280
- On line 282, choose between averaging all queries or taking the [CLS] query (average is default)
- On line 282, furthermore choose between piping sentences at a time through BERT or the whole paragraph 
(paragraph is default)

------------------------------------------------------
### evaluation.py
Choose two files (formatted in the way the output files of the get_attention[bert, eye_data] are) and calculate their
correlation. The script will calculate Pearson and Spearman correlations. By default it takes input file 1 and compares 
it to all MECO languages.

**To run the script**:
- Check filenames on lines 181 and 191
- Default is to compare the input file on line 181 to all language files. Adapt if needed

The output is printed to the console and could look like this:


```console
language     |pearson corr |p-value      |spearman corr|p-value

Dutch        |   0.4       |   0.24      |   0.38      |   0.25
Estonian     |   0.38      |   0.24      |   0.37      |   0.25
Finnish      |   0.39      |   0.26      |   0.39      |   0.25
German       |   0.41      |   0.24      |   0.4       |   0.24
Greek        |   0.43      |   0.24      |   0.42      |   0.21
Hebrew       |   0.43      |   0.24      |   0.43      |   0.22
Italian      |   0.4       |   0.26      |   0.4       |   0.23
English      |   0.32      |   0.3       |   0.32      |   0.31
Norwegian    |   0.39      |   0.25      |   0.39      |   0.24
Russian      |   0.4       |   0.24      |   0.37      |   0.25
Spanish      |   0.42      |   0.24      |   0.42      |   0.23
Turkish      |   0.41      |   0.22      |   0.41      |   0.21
```


### Included scripts:
- R script *convert_rda_to_csv.R*
- python script *build_meco_data.py*
- python script *get_attention_values_eye_data.py*
- python script *get_attention_weights_bert.py*
- python script *evaluation*

Additionally, all produced data used for the research paper.