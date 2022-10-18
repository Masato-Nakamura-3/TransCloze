# Overview

The TransCloze pipline facilitates automatic processing of speech production data. This pipeline detects the onset of the speech data, and provides machine-based transcriptions. The aim is to speed up the time-consuming processing of the speech data. I recommend you not to completely rely on the automated trascriptions/onsets but check each data by yourself, but it will still significantly facilitate speech data analysis.



THE AIM IS NOT TO MAGICALLY GENERATE PERFECT TRANSCRIPTIONS etc but a reasonably well starting point that requires minimal work to correct.



This is designed to be especially useful for the online speeded cloze task (or the sentence completion task), or other kinds of data that have some of the following features:

1. Open-ended but constrained responses
2. Typically short responses (mostly a single word)
3. The audio files contain some irrelevant noise
4. The latencies of responses are valuable data

However, it could be used for processing of other kinds of speech data as well.



![overview](./overview.png)

The main body of this pipleline is the TransCloze.py module, which takes .wav files and:

1. Gets onset data from [Chronset](https://www.bcbl.eu/databases/chronset/)
2. Gets automatic transcription from [Google Cloud Speech-to-Text API](https://cloud.google.com/speech-to-text)
3. Combines the information + context/probe info of the experiment and output them as Praat TextGrids (which can be inspected by humans)
4. Use the human-corrected transcription to improve automatic transcription.
5. Generates a csv file that contians the machine-genrated or human-corrected trasncription and onset information,, which can be easily analyzed by other scripts.



This pipeline also contains a few supplementary scripts:

1. webm2wav: Transforms PCIbex outputs into wav files
2. CheckAndEdit: A Praat script to facilitate human inspection of machine-generated onset and transcription

3. 



## Instructions

### Preperation

Please download the entire folder and place it whereever you want.



#### Data

- Wav of webm files whose names following a specific naming rule. It must contain the trial type, the item ID with one-letter condition code, and the participant ID, each of which separated by underscores (e.g. exp_10a_tdlf.webm). The trial type and the subject ID can be whatever strings that do not contain underscores. The second part indicating the item information ("10a" in the example above) can also be whatever string, but if you want to generate a csv file using this pipeline, it must be a combination of one number (whatever digits will be fine) and one alphabet following it.
- Optional: If you want to include contextual information in the output Praat files or csv files, you need a python dictionary that maps item information (e.g. "10a") onto the contextual information. (e.g. {"10a": "The dog bit the", "10b": "The man bit the", ...}). Such contextual information can help human inspection/correction of automated transcription.



### Converting webm files to wav files (webm2wav)

If you collected your data online using PCIbex, you will get webm files. However Praat, Chronest and Google Cloud Speech-to-Text API all don't accept webm files, so you need to convert them into wav files. ffmpeg is a free software that can do this, but it is not straightforward to convert files in different folders, since the output audio files of PCIbex are usually separated by participants. The "webm2wav" file recursively convert all the webm wiles below a certain directory at once.

#### Requirements

- ffmpeg (#####LINK##########)

#### Instructions

Enter the following line into your command line substituting the arguments.

```bash
bash location_of_webm2wav input_file_directory output_file_directory
```

- First argument:  the path to "webm2wav" file
- Second argument: the path to the directory which contaions all the webm files
- Third argument: the path to the output directory

NOTE: All the wav files below the input directry will be generated directly in the output directory



### TransCloze.py

This python module contains a set of useful functions for automatic transcription and onset detection.

Here is a list of short descriptions of the functions:

- 



For the detailed use of the TransCloze module, please see Sample.ipynb or Sample.py. You can also use help(TransCloze.NAME_OF_FUNCTION) functions to see the description of each function in the module.

#### Requirements

temp_note.TextGrid: A template of textgrid files used in transcribe.ipynb



Be careful that Google Cloud Speech-to-Text API is a paid service, and you need to set up your own Google Cloud Platform account to use this pipeline. See the instructions here. I decided to use this pipeline for its accuracy and its feature to constrain the candidates of transcription. Good news is that you can use it for practically free for the first 90 days.







 (pyに直すか)



Short description of functions:





### CheckAndEdit

Once you have the machine-generated trancriptions and onsets, you would want to correct them by manual inspection. CheckAndEdit facilitates this process by successively???? openning the wav files and TextGrid files together that can be corrected by researchers, and saving the edits.

This Praat script:

1. Opens TextGrid and wav files with the same name and present them together
2. Saves edits on the TextGrid

Simply enter the path to the wav files and textgrids to the box, and then the corresponding files are opened at once.

Be careful that the script overwrites the TextGrid file once you click on "continue"







Notes:

* This pipeline is built for OSX. This should work for other major OS's but it might need some modification.





If you have any questons, please contact Masato Nakamura (mnaka@umd.edu).





Chronsetなどの紹介はどこで？

Chronsetのcitation

