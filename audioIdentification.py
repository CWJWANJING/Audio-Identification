import os
import IPython.display as ipd
import numpy as np
import librosa
import librosa.display
from matplotlib import pyplot as plt
from skimage.feature import peak_local_max
from warnings import simplefilter

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

def hashing(anchor, width, height, delayTime, peaks, audioName):
    "Create a matrix of peaks hashed as: [[freq_anchor, freq_other, delta_time], time_anchor, songID]"
    hashingMatrix = np.zeros((len(peaks)*100, 4)) 
    index = 0 
    for m in range(0,len(peaks)):
        anchor = peaks[m]
        adjacents = targetZonePoints(anchor, width, height, delayTime, peaks)
        for n in range(0,len(adjacents)):
            # Store the pair of the anchor and the target zone point
            hashingMatrix[index][0] = hash((anchor[m][1], adjacents[n][1]))
            # Store the time difference between the anchor and the target zone point, i.e. delta_time
            hashingMatrix[index][1] = adjacents[n][0]-anchor[m][0]
            # Store the time offset
            hashingMatrix[index][2] = anchor[0]
            # Store the name of the song
            hashingMatrix[index][3] = audioName
            index=index+1
    
    # hashMatrix = hashMatrix[~np.all(hashMatrix==0,axis=1)]
    # hashMatrix = np.sort(hashMatrix,axis=0)
        
    return hashingMatrix

def singleFingerprint(audioPath):
    # Load audio
    y, sr = librosa.load(os.path.join(audioPath))

    # --------- Use mel spectrogram for time-frequency representations ---------

    # Compute and plot mel spectrogram
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=1024, hop_length=512, win_length=1024, window='hann', n_mels=128)

    # --------- Use STFT spectrogram for time-frequency representations ---------

    # # Compute and plot STFT spectrogram
    # S = np.abs(librosa.stft(y,n_fft=1024,window='hann',win_length=1024,hop_length=512))

    # --------- Use CQT spectrogram for time-frequency representations ---------

    # # Compute and plot CQT spectrogram
    # S = np.abs(librosa.cqt(y, sr=sr))

    # Plot spectrogram
    # plt.figure(figsize=(100, 50))
    # librosa.display.specshow(librosa.amplitude_to_db(S,ref=np.max),y_axis='linear', x_axis='time',cmap='gray_r',sr=sr)

    # ignore all future warnings, particularly ignore that for peak_local_max
    simplefilter(action='ignore', category=FutureWarning)
    # Detect peaks from the spectrogram and plot constellation map
    coordinates = peak_local_max(np.log(S, where=S > 0), min_distance=10,threshold_rel=0.05, indices = False)
    return coordinates

def fingerprintBuilder(pathToDatabase, pathToFingerprints):
    # Iterate the entire database and generate fingerprint for each of audio file
    for entry in os.scandir(pathToDatabase):
        # Get all the peaks
        coordinates = singleFingerprint(entry.path)
        plt.figure(figsize=(10, 5))
        plt.imshow(coordinates,cmap=plt.cm.binary,origin='lower')
        # Simplify the audi file name
        filename = "".join(entry.name[:-4].split("."))
        # save the plotted spectrogram graph as a figure
        plot_filename = os.path.join(os.getcwd(), pathToFingerprints, filename)
        plt.savefig(plot_filename)
        # To prevent the runtimeWarning that more than 20 figures have been opened. 
        plt.close()
        # Hash the points
        width = 
        height = 
        delayTime = 
        for anchor in coordinates:
            hashingMatrix = hashing(anchor, width, height, delayTime, coordinates, entry.name)
            print(hashingMatrix)
        
        # Store the hashing Matrix for each song
        # TODO

    return None

def audioIdentification(pathToQueryset, pathToFingerprints, pathToOutputtxt):
    # Generate the fingerprints for all the queries
    for entry in os.scandir(pathToQueryset):
        # Get all the peaks
        coordinates = singleFingerprint(entry.path)
        plt.figure(figsize=(10, 5))
        plt.imshow(coordinates,cmap=plt.cm.binary,origin='lower')
        # Compare fingerprints

    return None

if __name__ == "__main__":
    pathToDatabase = '/Users/wanjing/Desktop/MSc_AI/semB/MI/cw2/database_recordings'
    pathToFingerprints = '/Users/wanjing/Desktop/MSc_AI/semB/MI/cw2/databaseFingerprints'
    fingerprintBuilder(pathToDatabase, pathToFingerprints)