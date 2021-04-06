from fingerprintBuilder import *
from audioIdentification import *
import itertools

# The list is in the format of [[width, width,...],[height, height,...],[delayTime, delayTime,...]]
parameters = [[1.6, 1.8, 2, 2.2, 2.4], [200, 400, 600, 800, 1000], [0.1, 0.2, 0.4, 0.6, 0.8]]

combinations = list(itertools.product(*parameters))

for c in combinations:
    t0= time.perf_counter()

    pathToDatabase = '/Users/wanjing/Desktop/MSc_AI/semB/MI/cw2/database_subset'
    pathToFingerprints = '/Users/wanjing/Desktop/MSc_AI/semB/MI/cw2/databaseSubset_fingerprints'
    fingerprintBuilder(pathToDatabase, pathToFingerprints, c[0], c[1], c[2])

    pathToQueryset = '/Users/wanjing/Desktop/MSc_AI/semB/MI/cw2/query_subset'
    pathToQueryFingerprints = '/Users/wanjing/Desktop/MSc_AI/semB/MI/cw2/querySubset_fingerprints'
    pathToOutputTxt = '/Users/wanjing/Desktop/MSc_AI/semB/MI/cw2/output.txt'
    audioIdentification(pathToQueryset, pathToQueryFingerprints, pathToOutputTxt, c[0], c[1], c[2])

    t1 = time.perf_counter() - t0
    # Get the results
    a_file = open("output.txt", "r")

    list_of_lists = []
    for line in a_file:
        stripped_line = line.strip()
        line_list = stripped_line.split()
        list_of_lists.append(line_list)

    a_file.close()

    correctlyLabeled = 0
    for l in list_of_lists:
        correctSong = l[0][0:9]
        predict1 = l[1][0:9]
        predict2 = l[2][0:9]
        predict3 = l[3][0:9]
        if correctSong ==  predict1 or correctSong ==  predict2 or correctSong ==  predict3:
            correctlyLabeled += 1
    accuracy = correctlyLabeled / len(list_of_lists)
    settingNresults = [c[0], c[1], c[2], t1, accuracy]
    print(settingNresults)
    # remove songdatabase.db 
    os.remove('/Users/wanjing/Desktop/MSc_AI/semB/MI/cw2/songdatabase.db')
    # Store width, height, delayTime, time, accuracy, recall
    # print("Time elapsed: ", t1)