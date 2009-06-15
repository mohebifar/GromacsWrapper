# $Id$
"""\
Gromacs shell
=============

A thin shell around the Gromacs tools for light-weight integration into python
scripts or interactive use in ``ipython``.


Modules
-------

gromacs:     
     The top level module contains all gromacs tools; each tool can be run
     directly or queried for its documentation.

gromacs.cbook:
     The Gromacs cook book contains typical applications of the tools. In many
     cases this not more than just an often-used combination of parameters for
     a tool.

gromacs.tools:
     Contains classes that wrap the gromacs tools. They are automatically
     generated from the list of tools in ``gromacs.tools.gmx_tools``.

gromacs.analysis:
     A package that collects whole analysis tasks. It uses the gromacs but is
     otherwise only loosely coupled with the rest. See the package documentation.


Examples
--------

Getting help
............

In python
   help(gromacs.g_dist)
   gromacs.g_dist.help()
   gromacs.g_dist.help(long=True)

In ``ipython``:
   gromacs.g_dist ?


Simple usage
............

Gromacs flags are given as python keyword arguments:
   gromacs.g_dist(v=True, s='topol.tpr', f='md.xtc', o='dist.xvg', dist=1.2)

Input to stdin of the command can be supplied:
   gromacs.make_ndx(f='topol.tpr', o='md.ndx', 
                    input=('keep "SOL"', '"SOL" | r NA | r CL', 'name 2 solvent', 'q'))

Output of the command can be caught in a variable and analyzed:
   rc, output, junk = gromacs.grompp(..., stdout=False)        # collects command output
   for line in output.split('\n'):
       line = line.strip()
       if line.startswith('System has non-zero total charge:'):
             qtot = float(line[34:])
             break
(See ``gromacs.cbook.grompp_qtot`` for a more robust implementation of this
application.)


"""

__all__ = ['tools', 'cbook', 'analysis']

class GromacsError(EnvironmentError):
    """Error raised when a gromacs tool fails.

    Returns error code in the errno attribute and a string in strerror.
    """
    # TODO: return status code and possibly error message
    pass

class GromacsFailureWarning(Warning):
    """Warning about failure of a Gromacs tool."""
    pass

class GromacsImportWarning(ImportWarning):
    """Warns about problems with using a gromacs tool."""
    pass

# Add gromacs command **instances** to the top level.
# These serve as the equivalence of running commands in the shell.
# (Note that each gromacs command is actually run when the instance is
# created in order to gather the documentation string.)
import tools

# Ignore warnings from a few programs that do not produce
# documentation when run with '-h' (only applies when the default for
# failuremode of core.GromacsCommand is changed to 'warn')
import warnings
warnings.simplefilter("ignore", GromacsFailureWarning)
_have_g_commands = []
_missing_g_commands = []
for clsname, cls in tools.registry.items():
    name = clsname[0].lower() + clsname[1:]    # instances should start with lower case
    try:
        locals()[name] = cls()                 # add instance of command for immediate use
        _have_g_commands.append(name)
    except GromacsError:                       # ignore missing -h for doc extraction
        pass
    except OSError:
        _missing_g_commands.append(name)
warnings.simplefilter("default", GromacsFailureWarning)

warnings.simplefilter("default", GromacsImportWarning)
_have_g_commands.sort()
_missing_g_commands.sort()
if len(_missing_g_commands) > 0:
    warnings.warn("Some Gromacs commands were NOT found; "
                  "maybe source GMXRC first? The following are missing:\n%r\n" % _missing_g_commands,
                  category=GromacsImportWarning)

del name, cls, clsname
