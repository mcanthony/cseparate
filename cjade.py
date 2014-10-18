import numpy as np
from scipy.linalg import eig, sqrtm, inv

def cjade(X,m=None):
    # EXPERIMENTAL - Translation of Complex JADE to Python
    # Michael A. Casey - Bregman Media Labs
    # NOT FINISHED - DO NOT USE
    #
    # Source separation of complex signals with JADE.
    # Jade performs `Source Separation' in the following sense:
    #   X is an n x T data matrix assumed modelled as X = A S + N where
    # 
    # o A is an unknown n x m matrix with full rank.
    # o S is a m x T data matrix (source signals) with the properties
    #    	a) for each t, the components of S(:,t) are statistically
    #    	   independent
    # 	b) for each p, the S(p,:) is the realization of a zero-mean
    # 	   `source signal'.
    # 	c) At most one of these processes has a vanishing 4th-order
    # 	   cumulant.
    # o  N is a n x T matrix. It is a realization of a spatially white
    #    Gaussian noise, i.e. Cov(X) = sigma*eye(n) with unknown variance
    #    sigma.  This is probably better than no modeling at all...
    #
    # Jade performs source separation via a 
    # Joint Approximate Diagonalization of Eigen-matrices.  
    #
    # THIS VERSION ASSUMES ZERO-MEAN SIGNALS
    #
    # Input :
    #   * X: Each column of X is a sample from the n sensors
    #   * m: m is an optional argument for the number of sources.
    #     If ommited, JADE assumes as many sources as sensors.
    #
    # Output :
    #    * A is an n x m estimate of the mixing matrix
    #    * S is an m x T naive (ie pinv(A)*X)  estimate of the source signals
    #
    #
    # Version 1.6.  Copyright: JF Cardoso.  
    #
    # See notes, references and revision history at the bottom of this file



    # Copyright (c) 2013, Jean-Francois Cardoso
    # All rights reserved.
    #
    #
    # BSD-like license.
    # Redistribution and use in source and binary forms, with or without modification, 
    # are permitted provided that the following conditions are met:
    #
    # Redistributions of source code must retain the above copyright notice, 
    # this list of conditions and the following disclaimer.
    #
    # Redistributions in binary form must reproduce the above copyright notice,
    # this list of conditions and the following disclaimer in the documentation 
    # and/or other materials provided with the distribution.
    #
    #
    # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS 
    # OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
    # AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER 
    # OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
    # DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
    # DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER 
    # IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT 
    # OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

    if type(X) is not numpy.matrixlib.defmatrix.matrix:
        X = matrix(X)
    n,T = X.shape

    #  source detection not implemented yet !
    m = n if m is None else m

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # A few parameters that could be adjusted
    nem = m # number of eigen-matrices to be diagonalized
    seuil = 1/np.sqrt(T)/100. # a statistical threshold for stopping joint diag

    if m < n :  # assumes white noise
            D, U 	= eig((X*X.H)/T)
            puiss = np.diag(D)
            k = np.argsort(puiss)
            puiss = puiss[k]
            ibl 	= np.sqrt(puiss[n-m:n]-puiss[:n-m+1].mean())
            bl 	= np.ones(m,1) / ibl 
            W	= (matrix(np.diag(bl))*U[:n,k[n-m:n]]).H
            IW 	= matrix(U[:n,k[n-m:n+1]])*np.diag(ibl)
    else:    # assumes no noise
            IW 	= sqrtm((X*X.H)/T)
            W	= inv(IW)
    Y	= W * X

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%% Cumulant estimation


    R = (Y*Y.H)/T
    C = (Y*Y.T)/T

    Yl = np.zeros((1,T))
    Ykl = np.zeros((1,T))
    Yjkl = np.zeros((1,T))

    Q = zeros((m*m*m*m),1)
    index = 0

    for lx in np.arange(m):
        Yl = Y[lx,:]
        for kx in np.arange(m):
            Ykl = np.multiply(Yl, Y[kx,:].conj()) # element-wise multiply
            for jx in np.arange(m):
                Yjkl = np.multiply(Ykl, Y[jx,:].conj())
                for ix in np.arange(m):
                    Q[index] = np.multiply(Yjkl, Y[ix,:].T)/T -  R[ix,jx]*R[lx,kx] -  R[ix,kx]*R[lx,jx] -  C[ix,lx]*C[jx,kx].conj()  
                    index += 1

    #% If you prefer to use more memory and less CPU, you may prefer this
    #% code (due to J. Galy of ENSICA) for the estimation the cumulants
    #ones_m = ones(m,1) ; 
    #T1 	= kron(ones_m,Y); 
    #T2 	= kron(Y,ones_m);  
    #TT 	= (T1.* conj(T2)) ;
    #TS 	= (T1 * T2.')/T ;
    #R 	= (Y*Y')/T  ;
    #Q	= (TT*TT')/T - kron(R,ones(m)).*kron(ones(m),conj(R)) - R(:)*R(:)' - TS.*TS' ;



    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%computation and reshaping of the significant eigen matrices

    D, U = eig(Q.reshape(m*m,m*m))
    la = np.absolute(np.diag(D))
    K = np.argsort(la)
    la = la[K]

    # reshaping the most (there are `nem' of them) significant eigenmatrice
    M = np.zeros((m,nem*m)) # array to hold the significant eigen-matrices
    Z = np.zeros(m) # buffer
    h = m*m
    for u in np.arange(0, nem*m, m): 
        Z[:] = U[:,K[h]]
        M[:,u:u+m-1] = la[h]*Z
        h -= 1 



    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%% joint approximate diagonalization of the eigen-matrices


    #% Better declare the variables used in the loop :
    B = np.matrix([ [1, 0, 0], [0, 1, 1], [0, -1j, 1j ]])
    Bt = B.H
    Ip = np.zeros((1,nem))
    Iq = np.zeros((1,nem))
    g = np.zeros((3,nem))
    G = np.zeros((2,2))
    vcp = np.zeros((3,3))
    D = np.zeros((3,3))
    la = np.zeros((3,1))
    K = np.zeros((3,3))
    angles = np.zeros((3,1))
    pair = np.zeros((1,2))
    c = 0 
    s = 0 

    # init
    encore	= 1
    V = np.eye(m) 

    # Main loop
    while encore:
        encore=0
        for p in np.arange(m-1):
            for q in np.arange(p+1, m):
                Ip = np.arange(p, nem*m, m)
                Iq = np.arange(q, nem*m, m)

                # Computing the Givens angles
                g = np.r_[ M[p,Ip]-M[q,Iq], M[p,Iq], M[q,Ip] ]
                D, vcp = eig(real(B*(g*g.H)*Bt))
                K = np.argsort(diag(D))
                la = diag(D)[k] 
                angles	= vcp[:,K[2]]
                angles = -angles if angles[0]<0 else angles
                c = np.sqrt(0.5+angles[0]/2.0)
                s = 0.5*(angles[1]-1j*angles[2])/c
                if abs(s) > seuil: # updates matrices M and V by a Givens rotation
                    encore = 1
                    pair = np.r_[p,q]
                    G = np.r_[ np.c_[c, -conj(s)], np.c_[s, c] ]
                    V[:,pair] = V[:,pair] * G
                    M[pair,:]	= G.H * M[pair,:]
                    M[:,np.array([Ip,Iq])] = np.r_[c*M[:,Ip]+s*M[:,Iq], -conj(s)*M[:,Ip]+c*M[:,Iq] ]


    #%%estimation of the mixing matrix and signal separation
    A= IW*V
    S = V.H*Y

    return A,S

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
    # Note 1: This version does *not* assume circularly distributed
    # signals as 1.1 did.  The difference only entails more computations
    # in estimating the cumulants
    #
    #
    # Note 2: This code tries to minimize the work load by jointly
    # diagonalizing only the m most significant eigenmatrices of the
    # cumulant tensor.  When the model holds, this avoids the
    # diagonalization of m^2 matrices.  However, when the model does not
    # hold, there is in general more than m significant eigen-matrices.
    # In this case, this code still `works' but is no longer equivalent to
    # the minimization of a well defined contrast function: this would
    # require the diagonalization of *all* the eigen-matrices.  We note
    # (see the companion paper) that diagonalizing **all** the
    # eigen-matrices is strictly equivalent to diagonalize all the
    # `parallel cumulants slices'.  In other words, when the model does
    # not hold, it could be a good idea to diagonalize all the parallel
    # cumulant slices.  The joint diagonalization will require about m
    # times more operations, but on the other hand, computation of the
    # eigen-matrices is avoided.  Such an approach makes sense when
    # dealing with a relatively small number of sources (say smaller than
    # 10).
    #
    #
    # Revision history
    #-----------------
    #
    # Version 1.6 (August 2013) : 
    # o Added BSD-like license
    #
    # Version 1.5 (Nov. 2, 97) : 
    # o Added the option kindly provided by Jerome Galy
    #   (galy@dirac.ensica.fr) to compute the sample cumulant tensor.
    #   This option uses more memory but is faster (a similar piece of
    #   code was also passed to me by Sandip Bose).
    # o Suppressed the useles variable `oui'.
    # o Changed (angles=sign(angles(1))*angles) to (if angles(1)<0 ,
    #   angles= -angles ; end ;) as suggested by Iain Collings
    #   <i.collings@ee.mu.OZ.AU>.  This is safer (with probability 0 in
    #   the case of sample statistics)
    # o Cosmetic rewriting of the doc.  Fixed some typos and added new
    #   ones.
    #
    # Version 1.4 (Oct. 9, 97) : Changed the code for estimating
    # cumulants. The new version loops thru the sensor indices rather than
    # looping thru the time index.  This is much faster for large sample
    # sizes.  Also did some clean up.  One can now change the number of
    # eigen-matrices to be jointly diagonalized by just changing the
    # variable `nem'.  It is still hard coded below to be equal to the
    # number of sources.  This is more economical and OK when the model
    # holds but not appropriate when the model does not hold (in which
    # case, the algorithm is no longer asymptotically equivalent to
    # minimizing a contrast function, unless nem is the square of the
    # number of sources.)
    #
    # Version 1.3 (Oct. 6, 97) : Added various Matalb tricks to speed up
    # things a bit.  This is not very rewarding though, because the main
    # computational burden still is in estimating the 4th-order moments.
    # 
    # Version 1.2 (Mar., Apr., Sept. 97) : Corrected some mistakes **in
    # the comments !!**, Added note 2 `When the model does not hold' and
    # the EUSIPCO reference.
    #
    # Version 1.1 (Feb. 94): Creation
    #
    #-------------------------------------------------------------------
    #
    # Contact JF Cardoso for any comment bug report,and UPDATED VERSIONS.
    # email : cardoso@sig.enst.fr 
    # or check the WEB page http://sig.enst.fr/~cardoso/stuff.html 
    #
    # Reference:
    #  @article{CS_iee_94,
    #   author = "Jean-Fran\c{c}ois Cardoso and Antoine Souloumiac",
    #   journal = "IEE Proceedings-F",
    #   title = "Blind beamforming for non {G}aussian signals",
    #   number = "6",
    #   volume = "140",
    #   month = dec,
    #   pages = {362-370},
    #   year = "1993"}
    #
    #
    #  Some analytical insights into the asymptotic performance of JADE are in
    # @inproceedings{PerfEusipco94,
    #  HTML 	= "ftp://sig.enst.fr/pub/jfc/Papers/eusipco94_perf.ps.gz",
    #  author       = "Jean-Fran\c{c}ois Cardoso",
    #  address      = {Edinburgh},
    #  booktitle    = "{Proc. EUSIPCO}",
    #  month 	= sep,
    #  pages 	= "776--779",
    #  title 	= "On the performance of orthogonal source separation algorithms",
    #  year 	= 1994}
    #_________________________________________________________________________
    # jade.m ends here


