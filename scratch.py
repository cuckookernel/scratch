from collections.abc import Callable

from dadadada import Area, Array, Matrix, Price, Table, double
from scipy.optimize import minimize


def estimate_price(x: Area) -> Price:
    """Calcula precio de un apto
    (en $MM) dada su area en m2
    """
    return 3 * x + 0.0


def total_err( x: Array, y: Array, w: Array ) \
        -> double:
    """x, y son los datos reales
    w los parámetros del modelo
    """
    n = len(x)
    y_hat = [ 0.0 ] * n
    err = [ 0.0 ] * n

    for i in range(len(x)):
        y_hat[i] = w[1] * x[i] + w[0]
        err[i] = abs( y_hat[i] - y[i] )

    return sum(err)


def total_err_pd( w: Array, x: Matrix,
                  y: Array ) -> double:
    """x, y son los datos reales
    w los parámetros del modelo
    """
    n, p = x.shape; y_hat = [0.0] * n
    err = [0.0] * n

    for i in n:  # cycle over rows / cases
        y_hat[i] = estimate_price( w, x[i] )
        err[i] = abs( y_hat[i] - y[i] )

    return err.sum()


from scipy.optimize import minimize


def train( data: Table ) \
    -> Callable[[Array], double]:
    """Given training data return
    the best (linear) estimator function
    """
    x = data[['x1', ...]]  # vars. predictoras
    y = data['y']  # variable objetivo

    def tot_err( w: Array ):
        return total_err_pd( w, x, y )

    best_w = minimize( tot_err )

    def best_estimator( x_query: Array ):
        return estimate_price( best_w, x_query )

    return best_estimator


# noinspection PyArgumentList,PyMissingOrEmptyDocstring
def minimize_error( x: Array, y: Array ) \
        -> Array:
    from scipy.optimize import minimize

    def tot_err( w: Array ) -> double:
        return total_err( x, y, w)

    best_w = minimize(tot_err)
    return best_w


def classify_v2(x1, x2) -> int:
    if x1 >= 7.7:
        return 0  # Dog
    else:
        if x2 >= 15.1:
            return 1  # Cat
        else:
            return 0  # Dog


# noinspection PyMissingOrEmptyDocstring
def classify_v3(x1, x2) -> int:
    if x1 >= 7.7:
        if x2 >= 27:
            if x1 >= 13:
                return 0
            else:
                return 1
        else:
            return 0
    else:
        if x2 >= 15.1:
            return 1
        else:
            return 0


# noinspection PyPep8Naming
def main( data):

    from sklearn import tree

    clf = tree.DecisionTreeClassifier()

    X = data[['x1', 'x2']]
    y = data['class']
    clf.fit( X, y )

    y_pred = clf.predict( [ 10, 40] )


    return y_pred


# noinspection PyRedeclaration
def estimate_price( w: Array, x: Array ) -> Price:
    """This is the 'model'
    x ~ dim p,  w ~ dim p + 1
    """
    return ( w.zip( x )
             .map( lambda par: par[0] * par[1] )
             .sum()
             + w[len(x)] )
