import os
import numpy as np
import librosa
import librosa.display
from matplotlib import pyplot as plt
from skimage.feature import peak_local_max
from warnings import simplefilter
import sqlite3
import pdb
import time
from collections import defaultdict
from fingerprintBuilder import singleFingerprint, hashing, targetZonePoints

def matches(hashingMatrix, pathToFingerprints):
    # Connect to the existing database
    con = sqlite3.connect(pathToFingerprints)
    cur = con.cursor()
    # Put all the unique hash values into a list
    hashvalues = [str(hm[0]) for hm in hashingMatrix]
    hashvalues = ",".join(hashvalues)
    hashvalues = "(" + hashvalues + ")"
    # Extract all the rows of the table from the database which have the same hashvalue as this query song
    cur.execute(f"SELECT hashPair, timeOffset, audioName FROM hashingMatrix WHERE hashPair IN {hashvalues}")
    results = cur.fetchall()
    hDict = {}
    for hashPair, timeOffset, _ in hashingMatrix:
        hDict[hashPair] = timeOffset
    # The dicitionary stores in this format: {audioName: [(timeOffset, hDict[hashPair]), ...}
    resultsDict = defaultdict(list)
    for r in results:
        resultsDict[r[2]].append((r[1], hDict[r[0]]))
    return resultsDict

def scoreAsong(timeOffset):
    binWidth = 0.5
    timeDeltas = []
    # Calculate the time differences
    for t in timeOffset:
        timeDeltas.append(t[0] - t[1])
    # Plot it to the histogram
    hist, _ = np.histogram(timeDeltas, bins=np.arange(int(min(timeDeltas)), int(max(timeDeltas))+binWidth+1, binWidth))
    return np.max(hist)

def top3matches(resultsDict):
    scoresNnames = {}
    top3Names = []
    for audioName, timeOffsets in resultsDict.items():
        score = scoreAsong(timeOffsets)
        scoresNnames[score] = audioName
    if bool(scoresNnames) != False:
        # Find the top 1 match
        maxscore = max(scoresNnames.keys())
        maxSongName = scoresNnames[maxscore]
        top3Names.append(maxSongName)
        # Find the top 2 match
        scoresNnames.pop(maxscore)
        # If the list is not empty
        if bool(scoresNnames) != False:
            maxscore = max(scoresNnames.keys())
            maxSongName = scoresNnames[maxscore]
            top3Names.append(maxSongName)
            # Find the top 3 match
            scoresNnames.pop(maxscore)
            if bool(scoresNnames) != False:
                maxscore = max(scoresNnames.keys())
                maxSongName = scoresNnames[maxscore]
                top3Names.append(maxSongName)
            else:
                top3Names.append("None")
        else:
            top3Names.append("None")
            top3Names.append("None")
    else:
        top3Names.append("None")
        top3Names.append("None")
        top3Names.append("None")
    return top3Names



def audioIdentification(pathToQueryset, pathToFingerprints,
                        pathToOutputTxt, width=3, height=800, delayTime=0.1):
    outputLines = []
    for entry in os.scandir(pathToQueryset):
        if entry.name[-4:] == '.wav':
            # Simplify the query audio file name
            queryname = "".join(entry.name[:-4].split("."))
            # Get all the peaks
            coordinates, sr = singleFingerprint(entry.path, queryname)
            # Hash the points
            hashingMatrix = hashing(coordinates, sr, entry.name, width, height, delayTime)
            # Find all the hash pairs that matches this song
            resultsDict = matches(hashingMatrix, pathToFingerprints)
            # Get the top three choices
            top3Choices = top3matches(resultsDict)
            outputLine = entry.name + " " + " ".join(top3Choices)
            outputLines.append(outputLine)
    # Store the results in the txt file
    with open(pathToOutputTxt, 'w') as output:
        for line in outputLines:
            output.write(line)
            output.write("\n")
    return None

if __name__ == "__main__":
    t0= time.perf_counter()
    # Set the parameters for the target zone
    width = 3
    height = 800
    delayTime = 0.1

    pathToQueryset = 'query_recordings'
    pathToFingerprints = 'songdatabase.db'
    pathToOutputTxt = 'output.txt'
    audioIdentification(pathToQueryset, pathToFingerprints,
                        pathToOutputTxt, width=width, height=height,
                        delayTime=delayTime)
    t1 = time.perf_counter() - t0
    print("Time elapsed: ", t1)
