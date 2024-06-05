
# Algos implemented directly from
# https://en.wikipedia.org/wiki/Levenshtein_distance
import numpy as np
import cython

cimport numpy as np
# %%

NP_INT32 = np.int32

ctypedef np.int32_t NP_INT32_t


def levenshtein_dist_mat_v0(s: str, t: str) -> cython.int:
    # for all i and j, d[i ,j] will hold the Levenshtein distance between
    # the first i characters of s and the first j characters of t
    cdef int m = len(s)
    cdef int n = len(t)
    # set each element in d to zero
    cdef np.ndarray d = np.zeros( (m+1, n+1), dtype=NP_INT32 )
    # source prefixes can be transformed into empty string by
    # dropping all characters
    for i in range(1, m + 1):
        d[i, 0] = i

    # target prefixes can be reached from empty source prefix
    # by inserting every character
    for j in range(1, n + 1):
        d[0, j] = j

    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                subst_cost = 0
            else:
                subst_cost = 1

            d[i, j] = min(d[ i - 1, j] + 1,     # deletion
                          d[ i, j - 1] + 1,       # insertion
                          d[ i - 1, j - 1] + subst_cost)  #  substitution

    return d[m, n]


@cython.boundscheck(False)
@cython.wraparound(False)
def levenshtein_dist_mat_v1(s: str, t: str) -> cython.int:
    # for all i and j, d[i ,j] will hold the Levenshtein distance between
    # the first i characters of s and the first j characters of t
    cdef int m = len(s)
    cdef int n = len(t)
    # set each element in d to zero
    cdef np.ndarray d = np.zeros( (m + 1, n + 1), dtype=np.int32 )
    # source prefixes can be transformed into empty string by
    # dropping all characters
    for i in range(1, m + 1):
        d[i, 0] = i

    # target prefixes can be reached from empty source prefix
    # by inserting every character
    for j in range(1, n + 1):
        d[0, j] = j

    for j, t_j in enumerate(t):  # j ranges over columns
        for i, s_i in enumerate(s): # i ranges over rows
            subst_cost = 0 if s_i == t_j else 1
            d[i+1, j+1] = min(d[i, j + 1] + 1,     # deletion
                              d[i + 1, j] + 1,       # insertion
                              d[i, j] + subst_cost)  #  substitution

    return d[m, n]


@cython.boundscheck(False)
@cython.wraparound(False)
def levenshtein_dist_vec_v0( s:str, t: str) -> cython.int:
    #  create two work vectors of integer distances
    cdef int m = len(s)
    cdef int n = len(t)
    cdef np.ndarray v0 = np.zeros( n + 1, dtype=np.int32 )
    cdef np.ndarray v1 = np.zeros( n + 1, dtype=np.int32 )

    # initialize v0 (the previous row of distances)
    #  this row is A[0][i]: edit distance from an empty s to t;
    # that distance is the number of characters to append to  s to make t.
    for j in range( n + 1 ):
        v0[j] = j    # d[0, j] = j

    for i, s_i in enumerate(s):
        # calculate v1 (current row distances) from the previous row v0

        # first element of v1 is A[i + 1][0]
        #   edit distance is delete (i + 1) chars from s to match empty t
        v1[0] = i + 1

        # use formula to fill in the rest of the row
        for j, t_j in enumerate(t):
            #  calculating costs for A[i + 1][j + 1]
            del_cost = v0[j + 1] + 1  # d[i + 1, j + 1] + 1
            ins_cost = v1[j] + 1      # d[i, j+1] + 1
            subst_cost = v0[j] + (0 if s_i == t_j else 1)

            # d[i + 1, j + 1] =...
            v1[j + 1] = min([del_cost, ins_cost, subst_cost])

        # copy v1 (current row) to v0 (previous row) for next iteration
        # since data in v1 is always invalidated, a swap without copy could be more efficient
        # swap v0 with v1
        tmp = v0
        v0 = v1
        v1 = tmp

    #  after the last swap, the results of v1 are now in v0
    return v0[n]
