import pprint
import re
import sys


_STRING = re.compile(r"^\s*u?(['\"])")
_FLOATING_NUMBER = re.compile(r"^\s*(\d+\.\d+)\s*")
_NUMBER = re.compile(r"^\s*(\d+L?)\s*")
_BOOLEAN = re.compile(r"^\s*(True|False)\s*")
_DETAILS_OMITTED = re.compile(r'''
    ^\s*\.\.\.    # start with ... (and maybe spaces)
    [^\s'",;\]>]* # consume anything up until a separator''',
    re.X)
_LIST = re.compile(r"^\s*\[")
_LIST_SEPARATOR = re.compile(r"^\s*,\s*")
_LIST_END = re.compile(r"^\s*]\s*")
_DICT = re.compile(r"^\s*([\w-]+)<")
_DICT_FIELD = re.compile(r"^\s*([\w-]+)\s*=\s*")
_DICT_SEPARATOR = _LIST_SEPARATOR
_DICT_END = re.compile(r"^\s*>\s*")


class _EmptyObject(str):
    """An "empty" object returning itself when indexed.
    Used to avoid KeyErrors and the like"""

    _INSTANCE = None

    def __unicode__(self):
        return u''

    def __nonzero__(self):
        return False

    def __getattr__(self, name):
        return _EmptyObject._INSTANCE

    def __getitem__(self, key):
        return _EmptyObject._INSTANCE

    def __iter__(self):
        return iter([])

    def __reversed__(self):
        return self

    def __contains__(self, item):
        return False

    def items(self):
        return {}.items()

    def iteritems(self):
        return {}.iteritems()

_EmptyObject._INSTANCE = _EmptyObject()


class _MaleableList(list):
    def __getitem__(self, key):
        if key < self.__len__():
            return super(_MaleableList, self).__getitem__(key)
        return _EmptyObject._INSTANCE


class _MaleableDict(dict):
    def __getitem__(self, key):
        result = self.get(key, _EmptyObject._INSTANCE)
        if result is not _EmptyObject._INSTANCE:
            return result

        lower_key = key.lower()
        for k, v in self.iteritems():
            if k.lower() == lower_key:
                 return v

        return _EmptyObject._INSTANCE

    def __contains__(self, item):
        return not isinstance(self.__getitem__(item), _EmptyObject)


def _consume_re(re, text):
    m = re.match(text)
    if not m:
        return None, text
    return m, text[m.end(0):]


def _parse_string(text, quote_char):
    end = text.index(quote_char)
    while end >= 0:
        if text[end-1] == "\\":
            end = text.index(quote_char, end+1)
            continue
        if end >= len(text):
            break
        if text[end+1] in ',;>]':
            break
        end = text.index(quote_char, end+2)
    return text[:end].decode('string_escape', 'ignore'), text[end+1:]


def _parse_list(text):
    result = _MaleableList()
    while True:
        m, text = _consume_re(_LIST_END, text)
        if m:
            return result, text
        element, text = _parse(text)
        if element: result.append(element)
        _, text = _consume_re(_LIST_SEPARATOR, text)


def _parse_dict(text, name):
    args = _MaleableList()
    kwargs = _MaleableDict()
    while True:
        m, text = _consume_re(_DICT_END, text)
        if m:
            if args and kwargs:
                obj = _MaleableDict({ 'args': args })
                obj.update(kwargs)
            elif args:
                obj = args if len(args) > 1 else args[0]
            elif kwargs:
                obj = kwargs
            else:
                obj = _EmptyObject._INSTANCE
            return _MaleableDict({name: obj}), text
        m, text = _consume_re(_DICT_SEPARATOR, text)
        if m:
            continue
        m, text = _consume_re(_DICT_FIELD, text)
        if m:
            element, text = _parse(text)
            if element: kwargs[ m.group(1).strip("_") ] = element
            continue
        element, text = _parse(text)
        args.append(element)


def _parse(text):
    if not text:
        return _EmptyObject._INSTANCE, ""
    m, text = _consume_re(_STRING, text)
    if m:
        return _parse_string(text, m.group(1))
    m, text = _consume_re(_FLOATING_NUMBER, text)
    if m:
        value = float(m.group(1))
        return value, text
    m, text = _consume_re(_NUMBER, text)
    if m:
        value = long(m.group(1)[:-1]) if m.group(1).endswith("L") else int(m.group(1))
        return value, text
    m, text = _consume_re(_BOOLEAN, text)
    if m:
        return m.group(1) == "True", text
    m, text = _consume_re(_DETAILS_OMITTED, text)
    if m:
        return _EmptyObject._INSTANCE, text
    m, text = _consume_re(_LIST, text)
    if m:
        return _parse_list(text)
    m, text = _consume_re(_DICT, text)
    if m:
        return _parse_dict(text, m.group(1))
    raise ValueError(text)


def unformat(text):
    result, remainder = _parse(text)
    assert remainder == ""
    return result


def main():
    from io import StringIO
    f = open('examples.txt', 'r')
    for line in f:
        result = unformat(line.strip())
        pprint.pprint(result)

        raw_input('cont?')
    f.close()

if __name__ == '__main__':
    main()
