"""
Utility functions for loading and handling Script instances
"""
from jobserver.app import scripts


def load_script_func(module, name):
    """Load the correct function

    The correct process function is loaded from the specified module and
    returned as Python callable. Can be processed by a Process instance.

    Parameters
    ----------
    module : str
        The script module to be loaded from global.
    name : str
        The name of the function to be loaded from module.

    Returns
    -------
    func : function
        A Python function that will be processed by a Process instance.

    """
    # switch the module
    if module == 'scripts':
        mod = scripts
    else:
        try:
            mod = globals()[module]
        except KeyError:
            raise ValueError('The script module %s is not imported.'
                             % module)
    try:
        func = getattr(mod, name)
    except KeyError:
        raise ValueError('A function %s cannot be found in %s.'
                         % (name, module))

    return func