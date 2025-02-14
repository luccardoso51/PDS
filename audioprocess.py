import scipy.io.wavfile as wav
import numpy as np
import matplotlib.pyplot as plt
import sys
import tkinter as tk
import scipy.fftpack as fourier
import sklearn.metrics as metrics
from tkinter import filedialog
from scipy.signal import butter, lfilter, freqz, decimate, buttord, resample, iirdesign

def plotting(sig, modSig, n):
    fig, ax = plt.subplots(2, 1)
    ax[0].plot(n,sig)
    ax[0].set_xlabel('Time')
    ax[0].set_ylabel('Amplitude')
    ax[1].plot(n,modSig,'g') 
    ax[1].set_xlabel('Modulated Signal')
    plt.show()

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a
def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def modula(carrier, sig):
    mod = carrier * sig
    return mod

def demodula(sig, carrier):
    demod = sig * carrier
    return demod

#Inicializando
root = tk.Tk()
file_path1 = filedialog.askopenfilename()

(freq,sig) = wav.read(file_path1)
Fs = freq
audlength1 = len(sig)/freq
Fc1 = 100000 #Frequência do Carrier
Ac = 0.06 #Amplitude do Carrier


factor = int(input("Escreva o fator de dizimação:"))
n = np.arange(0, audlength1/factor, 1/Fs)
mult = np.cos(2*np.pi*Fc1*n)

carrier = (Ac * mult)
"""Gráfico do sinal Carrier
plt.title('Sinal Portador')
plt.plot(n, carrier)
plt.grid()
plt.show()
"""
decSig = decimate(sig, factor)
modulatedSig = modula(carrier, decSig)
print(Fs)
print(factor)
wav.write("modulated1.wav", Fs, modulatedSig)
wav.write("carrier1.wav", Fs, carrier)
plotting(decSig, modulatedSig, n) #Plota o primeiro sinal e a sua versão modulada

print("==Segundo arquivo==")
file_path2 = filedialog.askopenfilename()
(freq, sig2) = wav.read(file_path2)
Fs = freq
audlength2 = len(sig2)/freq
n = np.arange(0, audlength2/factor, 1/Fs)
Fc2 = 50000 # Frequência do segundo carrier, que será descartado

mult = np.cos(2*np.pi*Fc2*n)
carrier = (Ac * mult)
"""Gráfico do sinal Carrier
plt.title('Sinal Portador')
plt.plot(n, carrier)
plt.grid()
plt.show()
"""

decSig2 = decimate(sig2, factor)
modulatedSig2 = modula(carrier, decSig2)
print(Fs)
print(factor)
wav.write("modulated2.wav", Fs, modulatedSig2)
wav.write("carrier2.wav", Fs, carrier)

plotting(decSig2, modulatedSig2, n)

#Iguala o comprimento dos sinais, cortando o 'resto' do maior
if len(decSig) > len(decSig2):
    modulatedSig = modulatedSig[:len(modulatedSig2)]
    audlength1 = audlength2
if len(decSig) < len(decSig2):
    modulatedSig2 = modulatedSig2[:len(modulatedSig)]
    audlength2 = audlength1

#Soma os sinais modulados
modulatedSig = modulatedSig + modulatedSig2
mult = np.cos(2*np.pi*Fc1*n)
carrier = (Ac * mult)
wav.write("audiosomado.wav", Fs, modulatedSig)

#passSig = passafaixa(modulatedSig, Fs)
passSig = butter_bandpass_filter(modulatedSig, 2500.0, 3000.0, 8000)

demodulatedSig = demodula(passSig, carrier) #Retira o Carrier 1
plt.plot(n, demodulatedSig)
plt.title('Sinal demodulado')
plt.xlabel('n')
plt.ylabel('Amplitude')
plt.show()


plotting(modulatedSig, demodulatedSig, np.arange(0, (len(passSig)/Fs), 1/Fs))

#Upsampling do sinal
passSig = resample(demodulatedSig, len(sig))

input("Aperte enter para continuar.")
plotting(sig, passSig, np.arange(0, len(sig)/Fs, 1/Fs))

print(metrics.mean_squared_error(sig, passSig))

wav.write("audiofinal1.wav", Fs, passSig)
