# This is a twisted plugin directory
try:
    from twisted.plugin import pluginPackagePaths
    __path__.extend(pluginPackagePaths(__name__))
except ImportError:
    # Twisted 2.5 doesn't include pluginPackagePaths
    import sys, os
    __path__.extend([os.path.abspath(os.path.join(x, 'hackabot', 'plugins'))
                     for x in sys.path])
__all__ = []
