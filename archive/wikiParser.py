import sys, os, re, cgi, glob, time

class Parser(object): 
   EOF = 0

   def __init__(self, write=None, error=None): 
      self.text = None
      self.pos = 0

      if write is None: 
         write = sys.stdout.write
      self.write = write

      if error is None: 
         # example: sys.stderr.write("%s: %s" % (e, msg))
         error = lambda e, msg: None
      self.error = error

   def find(self, tokens): 
      """For each token in tokens, if the current position matches one of 
         those tokens, return True. Return False otherwise."""
      for token in tokens: 
         if token == self.EOF: 
            if self.pos == len(self.text): 
               return True
         elif self.text[self.pos:].startswith(token): 
            return True
      return False

   def eat(self, token): 
      """Eat the length of token if token's an int, or the token itself."""
      if type(token) is int: 
         if (self.pos + token) > len(self.text): 
            self.error("UnexpectedEOF", "Reached end of file")
            return None
         s = self.text[self.pos:self.pos+token]
         self.pos += token
         return s
      else: 
         assert self.find([token])
         self.pos += len(token)
         if self.pos > len(self.text): 
            self.error("UnexpectedEOF", "Reached end of file")
            return None
         return token

   def get(self, tokens, start=None, finish=None): 
      if start is not None: 
         self.eat(start)
      content = ''
      while not self.find(tokens): 
         s = self.eat(1)
         if s is not None: 
            content += s
         else: return content # reached EOF
      if finish is not None: 
         self.eat(finish)
      return content

r_tag = re.compile(r'(?<!\{)\{(?!\{)([^}]+)\}')
r_name = re.compile(r'^[A-Za-z0-9-]+$')
r_uri = re.compile(r'^[A-Za-z][A-Za-z0-9+.-]*:[^<>"]+$')
r_emdash = re.compile(r'[A-Za-z0-9"]--(?=[A-Za-z0-9"{])')
r_alpha = re.compile(r'[A-Za-z]+')

def makeID(s, current): 
   s = (''.join(r_alpha.findall(s)) or 'id') + str(len(s))
   while s in current: 
      s += 'n'
   return s

class TextParser(Parser): 
   LIST = 0
   HEADING = 1
   PRE = 2
   QUOT = 3
   PARAGRAPH = 4

   LI_START = '* '
   LI_OPEN = '\n* '
   PRE_START = '{{{\n'
   PRE_END = '\n}}}'
   QUOT_START = '[[[\n'
   QUOT_END = '\n]]]'
   H_START = '@ '
   SEPERATOR = '\n\n'

   def __init__(self, write=None, error=None, exists=None): 
      Parser.__init__(self, write=write, error=error)

      if exists is None: 
         exists = lambda: True
      self.exists = exists
      self.rawlinks = []
      self.ids = []

   def __call__(self, s): 
      self.text = s
      self.normalize()
      self.parse()

   def normalize(self): 
      self.text = self.text.strip() # ('\t\r\n ')
      self.text = self.text.replace('\r\n', '\n')
      self.text = self.text.replace('\r', '\n')
      self.text = re.sub(r'(?sm)\n[ \t]*\n', '\n\n', self.text)

   def parse(self): 
      blocks = []

      while 1: 
         blocks.append(self.blockElement())
         if self.find([Parser.EOF]): break

      for block in blocks: 
         blocktype, values = block[0], block[1:]
         {self.LIST: self.listElement, 
          self.HEADING: self.headingElement, 
          self.PRE: self.preElement, 
          self.QUOT: self.quotElement, 
          self.PARAGRAPH: self.paragraphElement
         }[blocktype](*values)

   def blockElement(self): 
      self.whitespace()

      if self.find([self.LI_START]): 
         content = self.get([self.SEPERATOR, Parser.EOF], self.LI_START)
         content = tuple(content.split('\n* '))
         return (self.LIST,) + content
      elif self.find([self.H_START]): 
         content = self.get(['\n', Parser.EOF], self.H_START)
         return (self.HEADING, content)
      elif self.find([self.PRE_START]): 
         content = self.get([self.PRE_END], self.PRE_START, self.PRE_END)
         return (self.PRE, content)
      elif self.find([self.QUOT_START]): 
         content = self.get([self.QUOT_END], self.QUOT_START, self.QUOT_END)
         if self.find([' - ']): 
            citation = self.get(['\n', Parser.EOF], ' - ')
            if not (r_uri.match(citation) and citation): 
               self.error('CitationURIError', # @@ allow other stuff?
                          'Citation (%s) must be a URI.' % citation)
         else: citation = None
         return (self.QUOT, content, citation)
      else: return (self.PARAGRAPH, self.get([self.SEPERATOR, Parser.EOF]))

   def whitespace(self): 
      while self.find(' \t\n'): 
         self.eat(1)

   def listElement(self, *items): 
      self.write('<ul>')
      self.write('\n')

      for item in items: 
         self.write('<li>')
         self.write(self.wikiParse(item))
         self.write('</li>')
         self.write('\n')

      self.write('</ul>')
      self.write('\n')

   def headingElement(self, content): 
      content = self.wikiParse(content)

      newid = makeID(content, self.ids)
      self.ids.append(newid)

      self.write('<h2 id="%s">' % newid)
      self.write(content)
      self.write('</h2>')
      self.write('\n')

   def preElement(self, content): 
      self.write('<pre>')

      self.write('\n')
      self.write(self.wikiParse(content, level=0))
      self.write('\n')

      self.write('</pre>')
      self.write('\n')

   def quotElement(self, content, cite): 
      self.write('<blockquote')
      if cite: 
         cite = self.iriParse(cite)
         cite = cgi.escape(cite, quote=1) # @@
         self.write(' cite="%s"' % cite)
      self.write('>')
      self.write('\n')

      self.write('<pre class="quote">') # @@
      self.write('\n')
      self.write(self.wikiParse(content, level=0))
      self.write('\n')
      self.write('</pre>')
      self.write('\n')

      self.write('</blockquote>')
      self.write('\n')

   def paragraphElement(self, content): 
      self.write('<p>')
      self.write(self.wikiParse(content))
      self.write('</p>')
      self.write('\n')

   def wikiParse(self, s, level=None): 
      if level is None: 
         level = 1
      # @@ use a proper parser, or catch the matches
      pos, result = 0, ''
      while pos < len(s): 
         m = r_tag.match(s[pos:])
         if m: 
            span = m.span()
            result += self.tag(s[pos:pos+span[1]], level=level)
            pos += span[1] - span[0]
         else: 
            m = r_emdash.match(s[pos:])
            if m and (level > 0): # unicode must be explicit in <pre>
               result += s[pos] + '&#8212;' # u'\u2014'.encode('utf-8')
               pos += 3
            elif (s[pos] == '{') and (s[pos+1:pos+2] != '{') and (level > 0): 
               if (s < 10): area = s[0:pos+10]
               else: area = s[pos-10:pos+10]
               msg = "The '{' must be escaped as '{{' in %r" % area
               raise "WikiParseError", msg
            elif (s[pos:pos+2] == '{{'): # d8uv bug "and (level > 0): "
               result += '{'
               pos += 2
            elif s[pos] == '&': 
               result += '&amp;'
               pos += 1
            elif s[pos] == '<': 
               result += '&lt;'
               pos += 1
            else: 
               result += s[pos]
               pos += 1
      return result

   def iriParse(self, uri): 
      r_unicode = re.compile(r'\{U\+([1-9A-F][0-9A-F]{1,5})\}')
      def escape(m): 
         bytes = unichr(int(m.group(1), 16)).encode('utf-8')
         return ''.join(['%%%02X' % ord(s) for s in bytes])
      return r_unicode.sub(escape, uri)

   def unicodeify(self, s): 
      if len(s) not in (2, 4, 6): 
         raise ValueError, 'Must be of length 2, 4, or 6'
      for letter in 'abcdef': 
         if letter in s: 
            raise ValueError, 'Unicode escapes must be lower-case'
      i = int(s.lstrip('0'), 16)
      raw = [0x9, 0xA, 0xD] + list(xrange(0x20, 0x7E))
      del raw[raw.index(0x2D)], raw[raw.index(0x5D)], raw[raw.index(0x7D)]
      if i in raw: return chr(i) # printable - '-]}'
      elif i > 0x10FFFF: 
         raise ValueError, 'Codepoint is out of range'
      return '&#x%s;' % s

   def tag(self, s, level=None): 
      if level is None: 
         level = 1 # @@ { {U+..}?
      s = s[1:-1] # @@ or s.strip('{}')
      if s.startswith('U+'): 
         try: result = self.unicodeify(s[2:])
         except ValueError: result = cgi.escape('{%s}' % s)
      elif s == '$timenow': 
         result = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
      elif s == '$datenow': 
         result = time.strftime('%Y-%m-%d', time.gmtime())
      elif level < 1: 
         result = '{' + self.wikiParse('%s}' % s)
      elif s.startswith('* '): 
         result = '<strong>%s</strong>' % s[2:]
      elif s.startswith('#'): 
         i = s.find(' ')
         href, title = s[:i], s[i+1:]
         result = '<a href="%s">%s</a>' % (href, title)
      elif not re.compile(r'[A-Za-z0-9_.-]').match(s): 
         result = cgi.escape('{%s}' % s)
      else: 
         self.rawlinks.append(s)
         words = s.split(' ')
         words = [word.strip() for word in words if word.strip()]
         if ('/' not in words[0]) and (':' not in words[0]): # @@!
            wn = ''.join(words)
            uri = './%s' % wn
            if not self.exists(wn): 
               cls = ' class="nonexistent"'
            else: cls = ''
         else: uri, s, cls = words[0], ' '.join(words[1:]), ''
         uri, s = cgi.escape(uri, quote=1), cgi.escape(s)
         result = '<a href="%s"%s>%s</a>' % (uri, cls, s)
      return result