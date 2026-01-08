from os.path import dirname, join

src = dirname(dirname(__file__))
jon = lambda x: join(src, *x) if isinstance(x, list) else join(src, x)
