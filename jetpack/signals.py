"""
Signals
-------

Tools for signal processing

"""

import sys
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
from scipy.linalg import sqrtm, inv

__all__ = ['peakdet', 'smooth', 'norms', 'sfthr', 'sfrct', 'sq', 'arr',
           'whiten', 'canoncorr']


def peakdet(v, delta, x=None):
    """
    Finds local optima (maxima and minima) of a 1D signal.

    Usage
    -----
    maxtab, mintab = peakdet(v, delta=0.5)

    Parameters
    ----------
    v : array_like
        The 1D signal in which we wish to find local optima

    delta : float
        Optima are accepted if they are at least delta greater than neighboring
        values

    x : array_like, optional
        Used to return the x-values of the optima. If None (default), indices
        into the `v` array are returned.

    Returns
    -------
    maxtab : array_like
        (N x 2) array, where the first column are the maxima and the second
        column are the locations of those maxima.

    mintab : array_like
        (N x 2) array, where the first column are the minima and the second
        column are the locations of those minima.

    Notes
    -----
    Converted from MATLAB script at http://billauer.co.il/peakdet.html

    """

    maxtab = []
    mintab = []

    if x is None:
        x = np.arange(len(v))

    v = np.asarray(v)

    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')

    if not np.isscalar(delta):
        sys.exit('Input argument delta must be a scalar')

    if delta <= 0:
        sys.exit('Input argument delta must be positive')

    mn, mx = np.Inf, -np.Inf
    mnpos, mxpos = np.NaN, np.NaN

    lookformax = True

    for i in np.arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]

        if lookformax:
            if this < mx-delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn+delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True

    return np.array(maxtab), np.array(mintab)


def smooth(x, sigma=1.0):
    """
    Smooths a 1D signal with a gaussian filter

    Parameters
    ----------
    x : array_like
        The array to be smoothed

    sigma : float, optional
    The width of the gaussian filter (default: 1.0)

    Returns
    -------
    xs : array_like
        A smoothed version of the input signal

    """

    return gaussian_filter1d(x, sigma, axis=0)


def norms(x, order=2):
    """
    Normalize a set of filters according to the given norm.
    If a matrix is given, each column is centered and normalized.

    Parameters
    ----------
    x : array_like
        The array (or matrix) to be normalized.

    order : {non-zero int, inf, -inf, 'fro'}, optional
        Order of the norm to use when normalizing the input. (default: 2)

    Returns
    -------
    xn : array_like
        The input array scaled to have unit norm columns.

    Notes
    -----
    For values of ``ord <= 0``, the result is, strictly speaking, not a
    mathematical 'norm', but it may still be useful for various numerical
    purposes.

    The following norms can be calculated:

    =====  ==========================
    order  norm for vectors
    =====  ==========================
    None   2-norm
    inf    max(abs(x))
    -inf   min(abs(x))
    0      sum(x != 0)
    other  sum(abs(x)**ord)**(1./ord)
    =====  ==========================

    """

    return x / np.linalg.norm(x, axis=0, ord=order)


def canoncorr(X, Y):
    """
    canonical correlation between two subspaces
    (computed via the QR decomposition)

    Parameters
    ----------
    X, Y : array_like
        The subspaces to compare. They should be of the same size.

    Returns
    -------
    corr : array_like
        The magnitude of the overlap between each dimension of the subspace.

    """

    # Orthogonalize each subspace
    qu, qv = np.linalg.qr(X)[0], np.linalg.qr(Y)[0]

    # singular values of the inner product between the orthogonalized spaces
    return np.linalg.svd(qu.T.dot(qv), compute_uv=False, full_matrices=False)


def sfthr(x, threshold):
    """
    Soft thresholding function

    Parameters
    ----------
    x : array_like
        The input array to the soft thresholding function

    threshold : float
        The threshold of the function

    Returns
    -------
    y : array_like
        The output of the soft thresholding function

    """

    return np.sign(x) * np.maximum(np.abs(x) - threshold, 0)


def sfrct(x, threshold):
    """
    Soft rectification function

    y = log(1 + exp(x - threshold))

    Parameters
    ----------
    x : array_like
        The input array to the soft thresholding function

    threshold : float
        The threshold of the function

    Returns
    -------
    y : array_like
        The output of the soft thresholding function

    """

    return np.log1p(np.exp(x - threshold))


def whiten(X):
    """
    Whitens an (N x M) matrix consisting of M samples of N-dimensional vectors

    Parameters
    ----------
    X : array_like
        Matrix where each column is a sample from an N-dimensional distribution

    Returns
    -------
    W : array_like
        Matrix where the columns are whitened version of the input vectors

    """

    return inv(sqrtm(np.cov(X))).dot(X)



def sq(x):
    """
    Reshape vector to a square image

    """

    if np.sqrt(x.size)**2 != x.size:
        raise ValueError('Error: the input size is inconsistent with a square')

    return x.reshape(int(np.sqrt(x.size)), -1)


def arr(x):
    """
    Converts a generator to a numpy array
    """
    return np.array(list(x))
