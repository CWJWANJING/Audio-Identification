import os
import IPython.display as ipd
import numpy as np
import librosa
import librosa.display
from matplotlib import pyplot as plt
from skimage.feature import peak_local_max
from warnings import simplefilter

def fingerprintBuilder(pathToDatabase, pathToFingerprints):
    # Iterate the entire database and generate fingerprint for each of audio file
    for entry in os.scandir(pathToDatabase):
        # Load audio
        y, sr = librosa.load(os.path.join(entry.path))

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

        # Detect peaks from the spectrogram and plot constellation map
        # ignore all future warnings, particularly ignore that for peak_local_max
        simplefilter(action='ignore', category=FutureWarning)
        coordinates = peak_local_max(np.log(S, where=S > 0), min_distance=10,threshold_rel=0.05, indices = False)
        plt.figure(figsize=(10, 5))
        plt.imshow(coordinates,cmap=plt.cm.binary,origin='lower')

        # Simplify the audi file name
        filename = "".join(entry.name[:-4].split("."))

        # save the plotted spectrogram graph as a figure
        plot_filename = os.path.join(os.getcwd(), pathToFingerprints, filename)
        plt.savefig(plot_filename)

        # To prevent the runtimeWarning that more than 20 figures have been opened. 
        plt.close()

    return None

def audioIdentification(pathToQueryset, pathToFingerprints, pathToOutputtxt):
    # Generate the fingerprints for all the queries
    for entry in os.scandir(pathToQueryset):
        # Load audio
        y, sr = librosa.load(os.path.join(entry.name))

        # --------- Use mel spectrogram for time-frequency representations ---------

        # Compute and plot mel spectrogram
        # S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=1024, hop_length=512, win_length=1024, window='hann', n_mels=128)

        # --------- Use STFT spectrogram for time-frequency representations ---------

        # # Compute and plot STFT spectrogram
        S = np.abs(librosa.stft(y,n_fft=1024,window='hann',win_length=1024,hop_length=512))

        # --------- Use CQT spectrogram for time-frequency representations ---------

        # # Compute and plot CQT spectrogram
        # S = np.abs(librosa.cqt(y, sr=sr))

        # Detect peaks from the spectrogram and plot constellation map
        coordinates = peak_local_max(np.log(S), min_distance=10,threshold_rel=0.05,indices = False)
        plt.figure(figsize=(10, 5))
        plt.imshow(coordinates,cmap=plt.cm.binary,origin='lower')

        # Compare fingerprints
    return None

if __name__ == "__main__":
    pathToDatabase = '/Users/wanjing/Desktop/MSc_AI/semB/MI/cw2/database_recordings'
    pathToFingerprints = '/Users/wanjing/Desktop/MSc_AI/semB/MI/cw2/databaseFingerprints'
    fingerprintBuilder(pathToDatabase, pathToFingerprints)