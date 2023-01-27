#!/usr/bin/env python
# coding: utf-8


# No overlap in the item id

### Prep

def stereo2monaural(wav_dir, backup_dir, threshold = 400000):
    """Find stereo wav files and turn them into monaural files.

    This only works for wav files named with "{}_{item_id}_{subject_id}.wav"

    Parameters
    ----------
    param1 : wav_dir
        Path to the directory that contains all the input wav files.
    param2 : backup_dir
        Path to save the original stereo files as backups.
    param3 : threshold
        The minimal file size to check if the audio is stereo.


    Returns
    -------
    NONE
        This function creates zip files but does not return any values.
    """

    import os
    from pydub import AudioSegment
    import math
    import shutil


    # Get the paths to wav files
    all_path = [os.path.join(wav_dir, f) for f in os.listdir(wav_dir) if (".wav" in f)]

    # Identify large files
    # The number depends on the length of the audio files
    large_files = [p for p in all_path if os.path.getsize(p)  > threshold]

    # Get subjects with large file sizes
    subj = list(set([os.path.splitext(f.split("_")[-1])[0] for f in large_files]))

    # Get path lists for those subjects
    rel_files = [os.path.join(wav_dir, f) for f in os.listdir(wav_dir) if (".wav" in f) and (any([s in f for s in subj]))]

    count = 0
    st_list = []

    for p in rel_files:

        total_number = len(rel_files)

        sound = AudioSegment.from_wav(p)

        if sound.channels > 1:

            shutil.copy(p, backup_dir)

            sound = sound.set_channels(1)
            sound.export(p, format="wav")

            st_list.append(os.path.splitext(p)[0].split("_")[-1])

        count = count + 1

        if math.floor(10 * (count-1) / total_number) < math.floor(10 * count / total_number):
            print(count, "/" , total_number)

    if len(st_list) == 0:
        print("All files are monoral")
    else:
        print(set(st_list))


    # final check:
    sixty = [os.path.join(wav_dir, f) for f in os.listdir(wav_dir) if ("exp_60" in f)]

    for p in sixty:
        sound = AudioSegment.from_wav(p)

        if sound.channels > 1:
            print(os.path.splitext(p)[0].split("_")[-1])








def chronset_prep(name, wav_dir, zip_dir):
    """Create zip files to for Chronset.

    This function takes individual wav files and divide them into chunks containing up to 500 files such that Chronset can handle. It might be particularly useful for Mac users because those zip files do not contain any junks automatically created by Mac, which often cause errors in Chronset.

    Parameters
    ----------
    param1 : name
        Name of the zip files. Each files will be named {name}_1.zip, {name}_2.zip, ...
    param2 : wav_dir
        Path to the directory that contains all the input wav files.
    param3 : zip_dir
        Path to the output directory for the created zip files.

    Returns
    -------
    NONE
        This function creates zip files but does not return any values.
    """


    import os
    import zipfile

    # Set the name of the zip files
    # The output files will be named as "{name}{number}".zip (e.g. batch1_10.zip)
    zipname = name + "_"


    # Get the names of the wav files
    filenames = [i for i in os.listdir(wav_dir) if (".wav" in i)]

    # Make lists of 500 or fewer wav files
    fewerthan500 = []
    temp = []
    for f in filenames:
        temp.append(f)
        if len(temp) == 500:
            fewerthan500.append(temp)
            temp = []
    if len(temp) > 0:
        fewerthan500.append(temp)

    # Output zip files with 500 or fewer wav files in them
    fnum = 0
    for filelist in fewerthan500:
        fnum = fnum + 1
        with zipfile.ZipFile(os.path.join(zip_dir, zipname+str(fnum) + ".zip"), 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
            for f in filelist:
                new_zip.write(os.path.join(wav_dir, f), arcname = f)


    print(f'Created {len(fewerthan500)} zip files for {len(filenames)} wav files.')

### Chronset output processing
def chronset_dict(chronset_dir):
    import os
    import pandas as pd
    """Create a dictionary that maps the file names onto onset time (sec).

    Note that chronset uses miliseconds while praat uses seconds

    Parameters
    ----------
    param1 : chronset_dir
        The path to the directory containing the chronset output text files.

    Returns
    -------
    onset_dict
        A python dictionary that maps wav file names (excluding the extension) onto transcriptions.
    """

    onset_dict = dict()
    for textf in [t for t in os.listdir(chronset_dir) if ".txt" in t]:
        onset_df = pd.read_table(os.path.join(chronset_dir, textf), names = ["wav", "rt"])
        temp_dict = dict(zip([os.path.splitext(w)[0] for w in onset_df["wav"]], onset_df["rt"] / 1000))
        onset_dict.update(temp_dict)

    return onset_dict

### Transcription
def transcribe(wav_dir, cred_path, prefix = [], lang_code = "en-US", keyword = {}):
    """Transcribe wav files.

    This function takes wav files in a directory and probes Google Speech-to-Text for transcription.

    Parameters
    ----------
    param1 : wav_dir
        Path to the directory that contains all the input wav files.
    param2 : cred_path
        Path to the API key.
    param3 : prefix (optional)
        You can optionally specify the string that must be included in the part before the first underscore. (e.g. ["exp"] for "exp_1a_xxxx.wav")
    param4 : lang_code (optional)
        Language code for Google Speech-to-Cloud. The default is set to American English.
    param5 : keyword (optional)
        A dictionary that maps item ID (e.g. "1a" of "exp_1a_xxx.wav") onto a list of candidates ({"1a":["eat", "drink"]}). Be careful tht this does not work if an ID is mapped to a single candidate directly.

    Returns
    -------
    dict_transcription
        This function returns a dictionary mapping file names onto transcription.
    """

    import os
    import io

    from google.cloud import speech
    #import numpy as np

    # Set the API key
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path

    # Get the file names
    # You can only get the ones including prefixes
    filenames = [i for i in os.listdir(wav_dir) if (".wav" in i)]
    if len(prefix) > 0:
        filenames = [f for f in filenames if any([p in f for p in prefix])]

    # Set the output dictionary
    dict_transcription = dict()

    # Load the client
    client = speech.SpeechClient()

    # Transcribe the wav files
    for file in filenames:

        transc_list = []

        # Load the audio file
        filepath = os.path.join(wav_dir, file)
        with io.open(filepath, "rb") as audio_file:
            content = audio_file.read()

        # Load the key words
        # !!! This part only works with "{}_{item_number}{condition}_{"subject_id"}.wav" format
        item_id = os.path.splitext(file)[0].split("_")[1] # "item_id" here is actually a combination of item_id and condition

        audio = speech.RecognitionAudio(content=content)

        if item_id in keyword.keys():
            speech_context = speech.SpeechContext(phrases=keyword[item_id])
            config = speech.RecognitionConfig(
                language_code=lang_code,
                speech_contexts=[speech_context],
            )
        else:
            config = speech.RecognitionConfig(
                language_code=lang_code,
            )

        # Transcription by Google Cloud Speech-to-Text


        response = client.recognize(config=config, audio=audio)

        try:
            for result in response.results:
                transc_list.append(result.alternatives[0].transcript)
            transc = " ".join(transc_list)

            # If the transcription is empty
            if len(transc) == 0:
                transc = "NOT_RECOGNIZED"
                failed_list.append(file)

            print(file+":\t" + transc)


        except:
            print("Error at ", file)
            transc = "NOT_RECOGNIZED"


        dict_transcription[os.path.splitext(file)[0]] = transc

    return dict_transcription



# This function generates .TextGrid files for Praat
# You can optionally pass a dictionary for the onset and/or for the duration of the files
# The onset function is basically for Chronset
# You can also give it context info to help hand correction

# If the audio files have heterogeneous durations, add an argument of "inconsistent = 1"

# The function replaces the RT with 0.1 if the RT is 0 or shorter, or is NaN, producing an error message
def generate_textgrid(dict_transcription, output_dir, wav_dir, prefix = [], onset = dict(), context = dict(), inconsistent = False):
    """This function generates Praat TextGrid files with transcriptions and onset times.

    Parameters
    ----------
    param1 : dict_transcription
        A python dictionary that maps file base names (e.g. "exp_11a_dfsa") onto transcription.
    param2 : output_dir
        A directory to save the TextGrid files.
    param3 : wav_dir
        A directory which contains the wav_files.
    param3 : prefix (optional)
        You can optionally specify the string that must be included in the part before the first underscore. (e.g. ["exp"] for "exp_1a_xxxx.wav")
    param4 : onset (optional)
        A dictonary that specifies the onset time of each speech recordings. (The output of chronset_dict() )
    param5 : context (optional)
        You can include the contextual information in a TextGrid tier to help human inspection through a dictionary with the format of ("1a": "The cop arrested...")
    param6 : inconsistent (optional)
        When the length of audio files are inconsistent, you should set this value as True.

    Returns
    -------
    None
        This function does not return anything but generates TextGrid files.
    """
    import os
    import textgrids
    import numpy as np
    from pydub import AudioSegment

    # Get the absolute path to the textgrid template
    basedir = os.path.dirname(os.path.abspath(__file__))
    tgpath = os.path.normpath(os.path.join(basedir, "./temp_note.TextGrid"))


    filenames = [os.path.splitext(i)[0] for i in os.listdir(wav_dir) if (".wav" in i)]
    if len(prefix) > 0:
        filenames = [f for f in filenames if any([p in f for p in prefix])]


    for k in filenames:
        # Load the TextGrid template and edit it
        tg = textgrids.TextGrid(tgpath)

        # If the duration of the audio files are inconsistent, edit each TextGrid files to match the duration of the audio files
        if inconsistent == True:
            audio = AudioSegment.from_file(os.path.join(wav_dir, k + ".wav"))
            tg["words"][1].xmax = tg["words"][-1].xmin = audio.duration_seconds - 0.001

            if tg.xmax != audio.duration_seconds:
                tg.xmax = audio.duration_seconds

                for tier in tg.keys():
                    tg[tier][-1].xmax = audio.duration_seconds


        tg["words"][1].text = dict_transcription[k]

        if k in onset.keys():
            # If the onset is not detected or is negative, set 0.1
            if np.isnan(onset[k]) or onset[k] <= 0 :
                print("No onset for ", k)
                tg["words"][0].xmax = tg["words"][1].xmin = 0.1
            else:
                tg["words"][0].xmax = tg["words"][1].xmin = onset[k]

        item_id = k.split("_")[1]

        if item_id in context.keys():
            tg["context"][0].text = context[item_id]

        tg.write(os.path.join(output_dir, k + ".TextGrid"))


####
def generate_csv(tg_dir, output_path):
    """This function generates csv files with transcriptions and onset times from text grid files.

    The descriptions of the columns:
    - filenames: The TextGrid file names excluding .TextGrid. (This should be the same as the original wav files.)
    - item_id: The item id (e.g. 10a). This corresponds to the second part of the file names (e.g. exp_10a_dsfd.TextGrid).
    - item_num: The numerical part of the item id. (e.g. 10 for exp_10a_dsfd.TextGrid)
    - item_con: The condition. (e.g. a for exp_10a_dsfd.TextGrid)
    - subject_id: The subject id. (e.g. dsfd for exp_10a_dsfd.TextGrid)
    - response: The transcription of the speech. This is the second segment of the "words" tier.
    - rt: The onset of the speech.
    - notes: The content of the "notes"  tier. (This only checks the first segment of the tier.)


    Parameters
    ----------
    param1 : transcription_dir
        A python dictionary that maps file base names (e.g. "exp_11a_dfsa") onto transcription.
    param2 : output_path
        The path to the output csv file.

    Returns
    -------
    None
        This function does not return anything but generates TextGrid files.
    """
    import os
    import shutil
    import pandas as pd
    import numpy as np
    import textgrids

    filenames = [os.path.splitext(fn)[0] for fn in os.listdir(tg_dir) if ".TextGrid" in fn]
    item_id = [f.split("_")[1] for f in filenames]
    item_num = [i[:-1] for i in item_id]
    item_con = [i[-1] for i in item_id]
    subject_id = [f.split("_")[2] for f in filenames]


    rt = []
    response = []
    notes = []
    for tg_loc in [f for f in os.listdir(tg_dir) if ".TextGrid" in f]:
        tg = textgrids.TextGrid(os.path.join(tg_dir, tg_loc))
        rt.append(tg["words"][1].xmin)
        response.append(tg["words"][1].text)
        notes.append(tg["notes"][0].text)

    d = pd.DataFrame({"filenames": filenames, "item_id": item_id, "item_num":item_num, "item_con":item_con, "subject_id": subject_id, "response":response, "rt":rt, "notes":notes})
    d.to_csv(output_path, index = False)


### Keyword functions
def get_keywords(tg_dirs, combine_conditions = False):
    """This function generates a dictionary with keywords from hand-corrected TextGrid files.

    Parameters
    ----------
    param1 : tg_dirs
        A list of paths to directories with TextGrid files.

    param2 : combine_conditions
        Set True if you want to collapse different conditions before generating keywords.

    Returns
    -------
    keyword_set
        A python dictionary mapping item ID (e.g. "8b") onto a list of keywords.
    """
    import textgrids
    import os
    import collections

    response_list = dict()
    keyword_set = dict()
    dictkeys = dict()
    filepaths = []

    for d in tg_dirs:
        filepaths = filepaths + [os.path.join(d, i) for i in os.listdir(d) if (".TextGrid" in i)]


    for f in filepaths:

        item_id = os.path.splitext(os.path.basename(f))[0].split("_")[1]

        if combine_conditions == True:
            # Delete conditions from item ID if necessary
            item_key = item_id[0:-1]
        else:
            item_key = item_id


        tg = textgrids.TextGrid(f)
        if tg["words"][1].text != "NOT_RECOGNIZED":
            response_list[item_key] = response_list.get(item_key, []) + [tg["words"][1].text]

        # Keep the mapping from full item IDs (with condition) to item numbers
        dictkeys[item_id] =  item_key

    for k in dictkeys.keys():
        resp_count = collections.Counter(response_list[dictkeys[k]])
        keyword_set[k] = [r for r in resp_count.keys() if resp_count[r] > 1]

    return keyword_set




### For PCIbex

def extract_rows(raw_results, keywords, ignore = []):
    """Extract rows in a PCIbex result file which contains specific keywords, and create a pandas dataframe.

    This requires that the number of columns are the same across all the columns including the keywords.
    So the keywords should be a name of a PennController trial for example.

    Parameters
    ----------
    param1 : raw_results
        A python list with rows of the PCIbex results file, or a path to it
    param2 : keywords
        A python list with key words to be included
    param3 : ignore
        A python list with columns to be ignored. Sometimes there are columns (e.g. "Label") that have no values in the raw results file.
        The columns whose names are specified with this argument are ignored.


    Returns
    -------
    output_pd
        A pandas DataFrame with the rows including keywords, with column names
    """

    import re
    import pandas as pd

    # A regular expression to find the rows in the reulst file with the column names
    # For example: "# 11. Value."

    re_col = '#\s(\d+)\.\s(.+)\.'

    # If raw_results is string, interpret is as a path and read from a file
    if type(raw_results) == str:
        with open(raw_results, 'r') as f:
            raw_results = f.read().splitlines()

    # Set up a dictionary to save the colnames
    exit_colnames_full = dict()

    for r in raw_results:

        # Get the rows with colum names
        iscol = re.match(re_col, r)

        if iscol:
            # Map column ids to column names
            exit_colnames_full[int(iscol.group(1)) - 1] = iscol.group(2)

            # Save the id of the final column (actually, +1 for range())
            maxcol = int(iscol.group(1))

        if all([k in r for k in keywords]):
            # End if a relevant row is found
            break

    # Sometimes the result file contains blank rows that do not have any values, which results in wrong column name assignments
    # This part excludes those blank columns
    new_col = [exit_colnames_full[k] for k in range(maxcol) if exit_colnames_full[k] not in ignore]
    exit_colnames = dict(zip(range(len(new_col)), new_col))

    output_pd = pd.DataFrame([r.split(",") for r in raw_results if all([k in r for k in keywords])]).rename(columns = exit_colnames)

    if (len(output_pd.columns) + len(ignore) < maxcol):
        print("There might be blank columns in the original raw results data.")

    return output_pd

### Checking after transcription
