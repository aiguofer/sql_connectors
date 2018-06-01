# -*- coding: utf-8 -*-

__all__ = [
    'extend_docs'
]

try:
    from inspect import cleandoc
    from pyment.docstring import DocString

    def extend_docs(orig_func, translate=False):
        """Decorator to extend the docstring with the docstring of the given function.

        :param orig_func: function to get docstring from
        """
        def wrapped(func):
            """
            Cleans doc from both functions and concatenates using 2 newlines in between.

            :param func: function whose docstring will be extended
            """
            orig_doc = orig_func.__doc__ or ""
            if translate:
                orig_doc = _parse_docstring(orig_doc)
            func.__doc__ = cleandoc(func.__doc__) + '\n\n' + cleandoc(orig_doc)
            return func
        return wrapped


    def _parse_docstring(docstring):
        docstring = DocString('', docs_raw=docstring, output_style='reST')
        docstring.parse_docs()
        return docstring.get_raw_docs().replace("'''", "")
except:
    def extend_docs(orig_func, translate=False):
        """Decorator to extend the docstring with the docstring of the given function.

        :param orig_func: function to get docstring from
        """
        def wrapped(func):
            """
            Cleans doc from both functions and concatenates using 2 newlines in between.

            :param func: function whose docstring will be extended
            """
            orig_doc = orig_func.__doc__ or ""
            if translate:
                print("Install pyment to translate the docs")
            func.__doc__ = cleandoc(func.__doc__) + '\n\n' + cleandoc(orig_doc)
            return func
        return wrapped
