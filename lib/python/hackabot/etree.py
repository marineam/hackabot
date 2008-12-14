# There are three different versions of ElementTree available but currently
# hackabot should be compatible with any of them, default to the version
# provided by >= python 2.5 since it is the least common denominator
try:
    from xml.etree import ElementTree
except ImportError:
    try:
        from elementtree import ElementTree
    except ImportError:
        try:
            from lxml import etree as ElementTree
        except ImportError:
            raise ImportError("ElementTree from Python 2.5, lxml, or the "
                    "original elementtree library is required.")
