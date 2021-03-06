import numpy as np
from bregman.suite import *
from cjade import cjade

def cseparate(x, M=None, N=4096, H =1024, W=4096, max_iter=200):
    """
    complex-valued frequency domain separation by independent components
    using relative phase representation
    
    inputs:
      x - the audio signal to separate (1 row)
      M - the number of sources to extract
    options:
      N - fft length in samples [4096]
      H - hop size in samples   [1024]
      W - window length in samples (fft padded with N-W zeros) [4096]
      max_iter - maximum JADE ICA iterations [200]
    output:
      xhat - the separated signals (M rows)
      xhat_all - the M separated signals mixed (1 row)
    
    Copyright (C) 2014 Michael A. Casey, Bregman Media Labs, 
    Dartmouth College All Rights Reserved
    """
    M = 20 if M is None else M

    phs_rec = lambda rp,dp: (np.angle(rp)+np.tile(np.atleast_2d(dp).T,rp.shape[1])).cumsum(1)

    F = LinearFrequencySpectrum(x, nfft=N, wfft=W, nhop=H)
    U = F._phase_map()    
    X = np.absolute(F.STFT) * np.exp(1j * np.array(F.dPhi)) # Relative phase STFT

    A,S = cjade(X.T, M, max_iter) # complex-domain JADE by J. F. Cardoso

    AS = np.array(A*S).T # Non hermitian transpose avoids complex conjugation
    Phi_hat = phs_rec(AS, F.dphi)
    x_hat_all = F.inverse(X_hat=np.absolute(AS), Phi_hat=Phi_hat, usewin=True)
    
    x_hat = []
    for k in np.arange(M):
        AS = np.array(A[:,k]*S[k,:]).T
        Phi_hat = phs_rec(AS, F.dphi)
        x_hat.append(F.inverse(X_hat=np.absolute(AS), Phi_hat=Phi_hat, usewin=True))

    return x_hat, x_hat_all

        
