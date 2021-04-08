from fingerprintBuilder import *
from audioIdentification import *
import itertools
import csv

# The list is in the format of [[width, width,...],[height, height,...],[delayTime, delayTime,...]]
parameters = [[2.4, 2.6, 2.8, 3.0, 3.2], [600, 800, 1000], [0.1, 0.2, 0.4, 0.6, 0.8]]

combinations = list(itertools.product(*parameters))

with open('resultfile.csv', mode='w') as resultfile:
    resultwriter = csv.writer(resultfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for c in combinations:
        t0= time.perf_counter()

        pathToDatabase = 'database_subset'
        pathToFingerprints = 'databaseSubset_fingerprints'
        fingerprintBuilder(pathToDatabase, pathToFingerprints, c[0], c[1], c[2])

        pathToQueryset = 'query_subset'
        pathToQueryFingerprints = 'querySubset_fingerprints'
        pathToOutputTxt = 'output.txt'
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

        # Calculate the recalls
        rank3 = 0
        rank2 = 0
        rank1 = 0
        for l in list_of_lists:
            correctSong = l[0][0:9]
            predict1 = l[1][0:9]
            predict2 = l[2][0:9]
            predict3 = l[3][0:9]
            # Check recall at rank 3
            if correctSong ==  predict1 or correctSong ==  predict2 or correctSong ==  predict3:
                rank3 += 1
            # Check recall at rank 2
            if correctSong ==  predict1 or correctSong ==  predict2:
                rank2 += 1
            # Check recall at rank 1
            if correctSong ==  predict1:
                rank1 += 1
        accuracy1 = rank1 / len(list_of_lists)
        accuracy2 = rank2 / len(list_of_lists)
        accuracy3 = rank3 / len(list_of_lists)
        # Store width, height, delayTime, time, recall with rank 1, recall with rank 2, and rank 3
        settingNresults = [c[0], c[1], c[2], t1, accuracy1, accuracy2, accuracy3]
        print(settingNresults)
        # Write the results into a table
        resultwriter.writerow(settingNresults)
        # remove songdatabase.db
        os.remove('songdatabase.db')
        # print("Time elapsed: ", t1)
