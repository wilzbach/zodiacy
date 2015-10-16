"""
Copyright (c) 2011, Giuseppe Tribulato.
License: MIT (see http://www.opensource.org/licenses/mit-license.php for details)
URL: http://www.gtsystem.eu/blog/2011/11/bottle-decorator-for-validate-query-parameters/
"""

from bottle import request
import functools
import inspect


def checkParams(**types):
    def decorate(f):
        farg, _, _, def_params = inspect.getargspec(f)
        if def_params is None:
            def_params = []
        farg = farg[:len(farg) - len(def_params)]

        param_info = [(par, ptype, par in farg)
                      for par, ptype in types.items()]

        @functools.wraps(f)
        def wrapper(*args, **kargs):
            getparam = request.GET.get
            for par, ptype, required in param_info:
                value = getparam(par)
                if not value:  # None or empty str
                    if required:
                        error = "%s() requires the parameter %s" % (wrapper.__name__, par)
                        raise TypeError(error)
                    continue
                try:
                    kargs[par] = ptype(value)
                except:
                    error = "Cannot convert parameter %s to %s" % (
                        par, ptype.__name__)
                    raise ValueError(error)

            return f(*args, **kargs)

        return wrapper
    return decorate
