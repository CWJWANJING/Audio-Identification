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

def singleFingerprint(audioPath, filename, pathToFingerprints):
    # Load audio
    y, sr = librosa.load(os.path.join(audioPath))

    # --------- Use mel spectrogram for time-frequency representations ---------

    # Compute and plot mel spectrogram
    # S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=1024, hop_length=512, win_length=1024, window='hann', n_mels=128)

    # --------- Use STFT spectrogram for time-frequency representations ---------

    # # Compute and plot STFT spectrogram
    S = np.abs(librosa.stft(y,n_fft=1024,window='hann',win_length=1024,hop_length=512))

    # --------- Use CQT spectrogram for time-frequency representations ---------

    # # Compute and plot CQT spectrogram
    # S = np.abs(librosa.cqt(y, sr=sr))

    # Plot spectrogram
    # plt.figure(figsize=(10, 5))
    # librosa.display.specshow(librosa.amplitude_to_db(S,ref=np.max),y_axis='linear', x_axis='time',cmap='gray_r',sr=sr)

    # ignore all future warnings, particularly ignore that for peak_local_max
    simplefilter(action='ignore', category=FutureWarning)
    # Detect peaks from the spectrogram and plot constellation map
    coordinates = peak_local_max(np.log(S, where=S > 0), min_distance=10,threshold_rel=0.05)
    plt.figure(figsize=(10, 5))
    coordinates = np.array(coordinates)
    plt.scatter(coordinates[:,0], coordinates[:,1])
    # save the plotted constellation map graph as a figure
    plot_filename = os.path.join(os.getcwd(), pathToFingerprints, filename)
    plt.savefig(plot_filename)
    # To prevent the runtimeWarning that more than 20 figures have been opened. 
    plt.close()
    return coordinates, sr

def targetZonePoints(anchor, width, height, delayTime, peaks):
    # Initialize the adjacent points
    adjacents = []
    # Set the horizontal range
    xMin = anchor[0] + delayTime
    xMax = xMin + width
    # Set the vertical range
    yMin = anchor[1] - (height*0.5)
    yMax = anchor[1] + (height*0.5)
    # Get all the points that are in the target zone
    for p in peaks:
        if (p[0] > xMin and p[0] < xMax) and (p[1] > yMin and p[1] < yMax):
            adjacents.append(p)
    return adjacents

def hashing(peaks, sr, audioName):
    width = 5
    height = 200
    delayTime = 0.5
    # Create a matrix of peaks hashed as: 
    # Anchor frequency,	Adjacent points frequency, Time delta, Anchor time,	audioName"
    hashingMatrix = []
    for m in range(0,len(peaks)):
        anchor = peaks[m]
        adjacents = targetZonePoints(anchor, width, height, delayTime, peaks)
        for n in range(0,len(adjacents)):
            hashes = []
            # Store the pair of the anchor and the target zone point, and their time difference as a hash
            hashes.append(hash((anchor[1], adjacents[n][1], (adjacents[n][0]-anchor[0])/sr)))
            # Store the time offset
            hashes.append(anchor[0]/sr)
            # Store the name of the song
            hashes.append(audioName)
            hashingMatrix.append(hashes)
    return hashingMatrix


def fingerprintBuilder(pathToDatabase, pathToFingerprints):
    # Prepare to store the hashing matrix into database
    # Create a Connection object that represents the database
    con = sqlite3.connect('songdatabase.db')
    cur = con.cursor()
    # Create table
    cur.execute('''CREATE TABLE IF NOT EXISTS hashingMatrix
                (hashPair int, timeOffset float, audioName text)''')

    # Iterate the entire database and generate fingerprint for each of audio file
    for entry in os.scandir(pathToDatabase):
        if entry.name[-4:] == '.wav':
            # Simplify the audi file name
            filename = "".join(entry.name[:-4].split("."))
            # Get all the peaks
            coordinates, sr = singleFingerprint(entry.path, filename, pathToFingerprints)         
            # Hash the points
            hashingMatrix = hashing(coordinates, sr, entry.name)
            # Insert the matrix into the database
            cur.executemany('''insert into hashingMatrix values (?, ?, ?)''', hashingMatrix)
            # Save (commit) the changes
            con.commit()
    # Close the connection.
    con.close()
    return None

if __name__ == "__main__":
    t0= time.clock()
    
    pathToDatabase = '/Users/wanjing/Desktop/MSc_AI/semB/MI/cw2/database_subset'
    pathToFingerprints = '/Users/wanjing/Desktop/MSc_AI/semB/MI/cw2/databaseSubset_fingerprints'
    fingerprintBuilder(pathToDatabase, pathToFingerprints)

    t1 = time.clock() - t0
    print("Time elapsed: ", t1)