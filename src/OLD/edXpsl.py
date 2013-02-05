from plasTeX import Base
class edXcourse(Base.Environment):
    args = '[ number ] [ name ] self'

class edXchapter(Base.Environment):
    args = '[ name ] self'

class edXsection(Base.Environment):
    args = '[ name ] self'

class edXsequential(Base.Environment):
    args = 'self'

class edXabox(Base.Command):
    args = 'self'

class includegraphics(Base.Command):
    args = '[ width ] self'

class edXscript(Base.Command):
    args = 'self'

class edXmath(Base.Environment):
    args = 'self'

class edXproblem(Base.Environment):
    args = '[ name ] [ points ] self'

class edXsolution(Base.Environment):
    args = 'self'
