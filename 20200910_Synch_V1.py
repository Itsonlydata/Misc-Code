import csv
import time
import datetime
from math import exp
from collections import Counter
import os
from operator import itemgetter

def isfloat(val):
    '''
    Returns True if the passed value can be coerced to float, otherwise returns False.
    Used to check if affective logits and probabilities are values or not.
    '''
    try:
        float(val)
        return True
    except ValueError:
        return False

def time_convert(data,dt_column,dt_format,tz_offset):
    '''
    Converts human-readable datetimes to UNIX timestamps.
    data: an array containing the datetimes to be converted.
    dt_column: the index position of the column containing the datetimes.
    dt_format: the expected format of the input datetimes
    tz_offset: time.mktime converts to UTC; tz_offset should adjust the result back to local time
    '''

    for i in data[1:]:
        i.append(int(time.mktime(datetime.datetime.strptime(i[dt_column],dt_format).timetuple()))-tz_offset)
    return data

def parse_empty_predictions(data):
    '''
    Sometimes, the affect prediction code spins up before the student starts recording data.
    In these cases, the predictions are always the same, and we parse them out of the set of affective predictions.
    '''
    output = [data[0]]

    for i in data[1:]:
        if float(i[10]) == -0.168 and float(i[11]) == 0.283 and float(i[12]) == 0.013 and float(
                i[13]) == 0.157 and float(i[15]) == 0.446:
            pass
        else:
            output.append(i)
    return output

def logit_to_prob(data,columns):
    '''
    Converts logit values for affective predictions into probabilities.
    data: an array containing the logits to be converted
    columns: a list of column indices containing the logits to be converted

    Some cases in the affect data report affective predictions of infinity, negative infinity, or NaN.
    In the event that a given value for a column is not a digit, we convert it to 0.
    '''
    exceptions = []

    print("Converting logit values to probabilities...")
    for i in data[1:]:
        for j in columns:
            if not isfloat(i[j]):
                exceptions.append(i[j])
                i[j] = 0
            else:
                i[j] = exp(float(i[j]))/(exp(float(i[j]))+1)

    for i in columns:
        print(f"Minimum value for column index {i}: {min([x[i] for x in data[1:]])}")
        print(f"Maximum value for column index {i}: {max([x[i] for x in data[1:]])}")

    return data

def trim_step_regression(data,columns):
    '''
    For affective labels produced via stepwise regression, converts predictions that fall outside [0,1] to 0 or 1.
    data: an array containing the probabilities to be trimmed
    columns: a list of columns containing the probabilities to be trimmed
    '''

    print("Thresholding stepwise regression values...")
    less0 = 0
    over1 = 0
    for i in data[1:]:
        for j in columns:
            if not isfloat(i[j]):
                i[j] = 0
            elif float(i[j]) < 0:
                i[j] = 0
                less0 += 1
            elif float(i[j]) > 1:
                i[j] = 1
                over1 += 1
            else:
                i[j] = float(i[j])

    for i in columns:
        print(f"Minimum value for column index {i}: {min([x[i] for x in data[1:]])}")
        print(f"Maximum value for column index {i}: {max([x[i] for x in data[1:]])}")

    return data

def get_affect_prediction(data):
    '''
    Generates an affective label based on the highest affective prediction.
    data: an array containing the probabilities to be trimmed
    '''

    print("Recalculating predicted affective label...")
    header = data[0]
    for i in data[1:]:
        i.append(header[i.index(max(i[10:16]))])
    print("Counts of affective predictions...")
    print(Counter([x[-1] for x in data[1:]]))
    return data

def link_qrf_intcode(qrf_location,transcript_data):
    '''
    Links transcription codes to relevant QRF observations.
    qrf_location: the path where qrf log files are located
    transcript_data: an array containing codes for transcribed interviews
    '''
    qrf_logs = os.listdir(qrf_location)
    qrf_dt_format = "%Y.%m.%d.%H.%M.%S.%f"
    matches = 0  # tracking successful links
    transcript_data = [x for x in transcript_data if x[0] != '']  # removing empty rows at the end of the file
    output = [["Filename", "Observation Assigned", "Observation Started", "Observation ID", "Unique ID",
              "Student ID", "Emotion", "Behavior", "Type"]]
    output[0].extend(transcript_data[0][1:])
    output[0].extend(['Observation Assigned (UNIX)', 'Observation Started (UNIX)'])

    print("Linking transcript codes to relevant QRF observations...")
    for i in transcript_data[1:]:
        bits = i[0].split('2019')
        filename = bits[0]
        ts_obs = '2019' + bits[1]
        temp_junk = bits[2].split('_')
        ts_start = '2019' + temp_junk[0].replace('audioindex','')
        obs_num = temp_junk[-1].replace('.3gp','')

        for j in qrf_logs:
            if filename in j:
                with open(qrf_input+"\\"+j,'r') as openfile:
                    qrf_read = list(csv.reader(openfile))
                for k in qrf_read:
                    if k[2] == ts_obs and k[7].split(':')[-1] == obs_num:
                        matches += 1  # double duty as unique identifier
                        student_id, emotion, behavior, type = k[9].split(':')[-1], \
                                                              k[11].split(':')[-1], \
                                                              k[12].split(':')[-1], \
                                                              k[13].split(':')[-1]

                        match = [filename, ts_obs, ts_start, obs_num, matches, student_id, emotion, behavior, type]
                        match.extend(i[1:])
                        output.append(match)
                        break  # we found our match, we can exit the loop

    output = time_convert(output,1,qrf_dt_format,0)
    output = time_convert(output,2,qrf_dt_format,0)
    print(f"Matched {matches} observations of a possible {len(transcript_data)-1}.")
    return output


def synchronization_main(log_data,qrf_data,affect_data,output_name):
    '''
    Takes multiple data sources and synchronizes based on timestamp alignment.
    log_data: an array containing student log data from Betty's Brain
    qrf_data: an array containing linked qrf and transcript code data
    affect_data: an array containing student affect data
    '''
    print("Preparing to synchronize files...")
    linked = 0
    qrf_s = []
    aff_s = []

    writer = csv.writer(open(output_name, 'w', newline=""))
    writer.writerow(['Special Event Marker'] + log_data[0] + affect_data[0] + qrf_data[0])

    log_data = [x for x in log_data if x[0] not in ['test1', 'test2', 'test3', 'test6']]  # removing test IDs
    affect_data = [x for x in affect_data if x[0] not in ['test1', 'test2', 'test3', 'test6']]  # removing test IDs

    unique_log = set([x[0] for x in log_data[1:]])
    unique_qrf = set([x[5] for x in qrf_data[1:]])
    unique_affect = set([x[1] for x in affect_data[1:]])

    log_data = [[""] + x + [""] * 46 for x in log_data]

    print(f"Found {len(unique_log)} student IDs in log data.")
    print(f"Found {len(unique_affect)} student IDs in affect data.")
    print(f"Found {len(unique_qrf)} student IDs in transcript and QRF data.")

    print(f"The following student IDs are present in log data, but not in affect data: {unique_log-unique_affect}.")
    print(f"The following student IDs are present in log data, but not in transcripts: {unique_log-unique_qrf}.")

    for sid in list(unique_log):
        if sid not in unique_qrf:
            sid_subset = [x for x in log_data[1:] if x[1] == sid]
            writer.writerows(sid_subset)
            continue

        log_subset = [x for x in log_data[1:] if x[1] == sid]
        aff_subset = [x for x in affect_data[1:] if x[1] == sid]
        qrf_subset = [x for x in qrf_data[1:] if x[5] == sid]

        log_subset.sort(key=itemgetter(7))
        aff_subset.sort(key=itemgetter(0))
        qrf_subset.sort(key=itemgetter(-2))

        aff_i = 0
        tscr_i = 0

        for n, i in enumerate(log_subset):
            i[7] = int(i[7])

            if n == len(log_subset)-1:
                break

            if sid in unique_qrf:
                while int(i[7]) > int(qrf_subset[tscr_i][-1])*1000 + (3600*1000) and tscr_i < len(qrf_subset)-1:
                    if tscr_i == len(qrf_subset)-1:
                        continue
                    else:
                        tscr_i += 1

            while int(i[7]) > int(aff_subset[aff_i][9]) and aff_i < len(aff_subset)-1:
                if aff_i == len(aff_subset)-1:
                    continue
                else:
                    aff_i += 1

            while int(aff_subset[aff_i][9]) - int(i[7]) > 20000 and int(aff_subset[aff_i][9]) < int(log_subset[n+1][7]):
                if aff_i == len(aff_subset)-1 or n == len(log_subset)-1:
                    continue

                dummy_logs = ['Unpaired Affective Prediction',i[1]]
                dummy_logs.extend(['']*63)
                dummy_logs.extend(aff_subset[aff_i])
                writer.writerow(dummy_logs)
                aff_i += 1

            if n < len(log_subset)-1:
                if sid in unique_qrf:
                    if int(i[7]) <= int(qrf_subset[tscr_i][-2])*1000 + 3600*1000 <= int(log_subset[n + 1][7]):
                        i[82:] = qrf_subset[tscr_i]
                        i[0] = "Observation Assigned"

                    if int(i[7]) <= int(qrf_subset[tscr_i][-1])*1000 + 3600*1000 <= int(log_subset[n + 1][7]):
                        i[82:] = qrf_subset[tscr_i]
                        i[0] = "Observation Started"
                        qrf_s.append(qrf_subset[tscr_i])

                if 0 <= int(aff_subset[aff_i][9]) - int(i[7]) <= 20000:
                    i[65:82] = aff_subset[aff_i]
                    aff_s.append(aff_subset[aff_i])

            writer.writerow(i)

    qrf_set = set(tuple(x) for x in qrf_data[1:])
    syn_set = set(tuple(x) for x in qrf_s)
    inters = qrf_set - syn_set
    print(f"QRF log observations that have not been synched: {len(inters)}.")
    print(f"Total QRF log observations: {len(qrf_set)}.")

    aff_set = set(tuple(x) for x in affect_data[1:])
    syn_set = set(tuple(x) for x in aff_s)

    inters = aff_set - syn_set
    print(len([x for x in inters if x[1] == "A50"]))
    print(f"Affective observations that have not been synched: {len(inters)}.")
    print(f"Total affective observations: {len(aff_set)}.")

if __name__ == "__main__":
    # affect_input = "D:\\BettyBrain\\Project Data\\Affect Data\\Dec_2018_affect_cleaned_Oct20.csv"
    affect_input = "D:\\BettyBrain\\Project Data\\Affect Data\\Feb_2019_affect_cleaned_Oct20.csv"

    # qrf_input = "D:\\BettyBrain\\Project Data\\QRF Logs\\Dec2018_Corrected"
    qrf_input = "D:\\BettyBrain\\Project Data\\QRF Logs\\Feb2019_Corrected"

    # logs_input = "D:\\BettyBrain\\Project Data\\System Log Data\\detailed-action-csv-data-Dec_2018_climate_change.csv"
    logs_input = "D:\\BettyBrain\\Project Data\\System Log Data\\detailed-action-csv-data-Feb_2019_thermoregulation.csv"

    # transcript_code_input = "D:\\BettyBrain\\Project Data\\Transcriptions\\Diff-Help-Int-Strat-and-triggers(Dec)-recode.csv"
    transcript_code_input = "D:\\BettyBrain\\Project Data\\Transcriptions\\BB_Feb_Interview_Codes - All codes.csv"

    # synch_output = "D:\\BettyBrain\\Project Data\\20201113_Dec2018_SynchronizedOutput.csv"
    synch_output = "D:\\BettyBrain\\Project Data\\20201113_Feb2019_SynchronizedOutput.csv"

    # affect_format_old = "%m/%d/%Y %H:%M:%S"
    affect_format = "%Y-%m-%d %H:%M:%S"

    with open(affect_input,'r') as f:
        reader = list(csv.reader(f))
        reader[0].append('Predicted Affect')

    print(f"Affective records before parsing empty predictions: {len(reader)}.")
    reader = parse_empty_predictions(reader)
    print(f"Affective records after parsing empty predictions: {len(reader)}.")
    # reader = time_convert(reader,7,affect_format,21600)
    # new affect data is UTC; converting datetime to timestamp is legacy
    # new timestamp index is 9
    reader = logit_to_prob(reader,[10,11,12,13,15])
    reader = trim_step_regression(reader,[14])
    reader = get_affect_prediction(reader)
    affect = reader

    with open(transcript_code_input,'r') as f:
        reader = list(csv.reader(f))
        qrf = link_qrf_intcode(qrf_input,reader)

    with open(logs_input,'r') as f:
        logs = list(csv.reader(f))

    synchronization_main(logs, qrf, affect, synch_output)

'''
    with open(synch_output,'r') as f:
        reader = list(csv.reader(f))
        a101 = [x for x in reader if x[1] == "A101"]
        print(f"Records for student A101: {len(a101)}.")

        writer = csv.writer(open("Debug Output.csv",'w',newline=""))
        writer.writerow(reader[0])
        writer.writerows([x for x in reader if x[1] == "A101"])
'''

    # affect logs prepared at this point

