#!/usr/bin/python3
# -*- coding: utf-8 -*-
#


__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "18.02.16"
__usage__ = "Boite à outils"
__version__ = "$Id: mmcTools.py,v 3.4 2018/02/09 15:59:00 mmc Exp $"
__srcloc__ = "ASD"

#------- import --------------
import functools
import inspect
import copy
import sys
import typing
import abc
import collections
import os
import sys
import functools
import logging, tempfile
import warnings
#-----------------------------

if sys.version_info[:2] < (3, 3):
    def signature(fonction):
        @functools.wraps(fonction)
        def enveloppe(*args, **kwrags):
            print("annotations are unvailable, so just ignore them")
            _r = fonction(*args, **kwargs)
            return _r
        return enveloppe
else:
    def signature(fonction):
        """
            adaptée de Python in Practice by Mark Summerfield 
            modifiée pour la gestion des instances de classes (et du self)
            utilisation des __annotations__ py3.4+

            Pour savoir si vous pouvez utiliser les annotations faites
            dans le shell:

            import platform
            platform.python_version_tuple() 

            >>> import platform
            >>> platform.python_version_tuple() 
            ('3', '4', '5')

        """
        annotations = fonction.__annotations__
        for k in annotations: # gestion du None à la volée
            if annotations[k] is None: annotations[k] = type(None)
        arg_spec = inspect.getfullargspec(fonction)
        has_return = True
        if "return" not in annotations:
            has_return = False
            warnings.warn("Warning: missing type for return value in {} signature"
                          "".format(fonction.__name__))
        if has_return and annotations['return'] == any: has_return = False

        for arg in arg_spec.args + arg_spec.kwonlyargs:
            if arg == 'self': continue
            if arg == 'cls': continue
            assert arg in annotations, "missing type for '{}'".format(arg)

        @functools.wraps(fonction)
        def enveloppe(*args, **kargs):
            for name, arg in (list(zip(arg_spec.args, args))+
                                list(kargs.items())):
                if name == 'self': continue # self est non typé
                if name == 'cls': continue # cls est non typé
                if annotations[name] == any: continue # any: tout est bon
                assert isinstance(arg, annotations[name]), \
                    ("expected argument {0} of type {1} got {2}"
                     " in function '{3}'".format(name, annotations[name], 
                                                 type(arg), fonction.__name__))
            _r = fonction(*args, **kargs)
            if has_return:
                """ ::TOBE FIXED typing.Union CHANGED in 3.6
                if issubclass(annotations["return"], typing.Union):
                    _ok = False
                    for x in annotations["return"].__union_params__:
                        if isinstance(_r, x) :
                            _ok = True ; break
                    assert _ok, ("{2}: expected return of {0} got {1}"
                                 "".format(annotations["return"], type(_r), 
                                           fonction.__name__))
                else: """
                
                assert isinstance(_r, annotations["return"]), \
                    ("{2}: expected return of {0} got {1}"
                     "".format(annotations["return"], type(_r), 
                               fonction.__name__))
            return _r
        return enveloppe

class Controle(object):
    """ 
        permet de faire un getter / setter avec verification
        @property_ : propriete a verifie
    """
    def __init__(self, property_=lambda *args: True, once=False, doc=None):
        self.__propriete = property_
        if doc is None:
            if once:  doc = "\nread-only attribute\n"
            else: doc="\nread-write attribute\n"
        self.__doc = doc
        self.__once = once
        self.__lock = False
    @property
    def propriete(self):
        if not self.lock:
            if self.__once: self.__lock = True
        return self.__propriete
    @property
    def doc(self): return self.__doc
    @property
    def lock(self): return self.__lock
        
def checkMe(cls):
    """ decorateur de classe genere des attributs Controle """
    _pref = '_'+cls.__name__
    def make_property(name, att):
        _prive = _pref+"__"+name
        def getMe(self): return getattr(self, _prive)
        def setMe(self, val):
            if hasattr(self, _prive):
                _old = getattr(self, _prive)
            else: _old = None

            if _old is None or not att.lock:
                if att.propriete(name, val): setattr(self, _prive, val)
                else: raise ValueError("cant set {} to {}".format(name, val))
            #die silently for readonly, uncomment if needed
            #else: raise AttributeError("read-only attribute {}".format(name))
        return property(getMe, setMe, doc=att.doc)
    for nm, at in cls.__dict__.items():
        if isinstance(at, Controle):
            setattr(cls, nm, make_property(nm, at))
    return cls

#===================== la propriété est-elle vérifiée =================#
def check_property(p, msg='default', letter='E'):
    """ permet de tester une propriété
    @input p: propriété à tester (vraie ou fausse)
    @input msg: message spécifique en cas d'erreur [defaut=default]
    @input letter: code d'erreur [defaut=E]
    @return letter (echec) . (succes)
    """
    try:
        assert( p ), '>>> failure %s' % msg
        _ = '.'
    except Exception as _e:
        if sys.version_info[:2] >= (3, 3): print(_e, flush=True)
        else: print(_e)
        _ = letter
        
    return _

#====================== sz tests réussis ? =========================#
def has_failure(string, sz=1):
    """ vérifie si les sz derniers tests ont échoué """
    sz = min(len(string), sz)
    return string[-sz:] != '.'*sz
    
#========================= attributs ro ? ===========================#
def subtest_readonly(obj, lattr):
    """ vérification de chaque attribut de obj en lecture seule 
    
    Principe: on sauvegarde dans oldv la valeur courante
    on cherche à affecter un entier, un float, une liste, une chaine
    si ça marche -> erreur + remise en place de l'ancienne valeur

    """
    _s = '' ; _msg =''
    lattr = lattr.split() if isinstance(lattr, str) else lattr
    for att in lattr:
        _msg += "test attribut {}".format(att)
        try:
            oldv = copy.deepcopy(getattr(obj, att))
        except:
            continue
        try:
            _s += '.'
            setattr(obj, att, 421)
            if oldv != getattr(obj, att): _s += 'E'
        except Exception:
            _s += '.'
        if has_failure(_s, 2):
            _msg += '\n\tavant %s apres %s\n' % (oldv, getattr(obj, att))
            setattr(obj, att, oldv)

        try:
            _s += '.'
            setattr(obj, att, 42.24)
            if oldv != getattr(obj, att): _s += 'E'
        except Exception:
            _s += '.'
        if has_failure(_s, 2):
            _msg += '\n\tavant %s apres %s\n' % (oldv, getattr(obj, att))
            setattr(obj, att, oldv)
            
        try:
            _s += '.'
            setattr(obj, att, [-1, 0, 1, 'a'])
            if oldv != getattr(obj, att): _s += 'E'
        except Exception:
            _s += '.'
        if has_failure(_s, 2):
            _msg += '\n\tavant %s apres %s\n' % (oldv, getattr(obj, att))
            setattr(obj, att, oldv)
            
        try:
            _s += '.'
            setattr(obj, att, "gasp")
            if oldv != getattr(obj, att): _s += 'E'
        except Exception:
            _s += '.'
        if has_failure(_s, 2):
            _msg += '\n\tavant %s apres %s\n' % (oldv, getattr(obj, att))
            setattr(obj, att, oldv)
            
        _msg += _s+'\n'
        _s = ''
    return _msg

#=================== pas de variables publiques ni protégées ===============#
def check_validity(mymodule, klassname, obj=None, lattr=[], zapit=None):
    """ 
    en entrée :
    - un module
    - un nom de classe
    - un objet (default None)
    - des atributs demandés (default [])
    en sortie:
    - le nombre d'attributs protégés (interdits)
    - le nombre d'attributs publiques (interdits)
    renvoie les interdits
    """
    public = set([])
    protected = set([])
    private = set([])
    klass = getattr(mymodule, klassname)
    subKlass = None if zapit is None else getattr(mymodule, zapit)
    if obj is None:
        try:
            obj = klass()
        except:
            obj = klass
    allPref = []
    allPref.append('_'+klassname+'__')
    if zapit is not None: allPref.append('_'+zapit+'__')

    for x in dir(obj):
        #print("analyzing {} ... status ".format(x), end='')
        status = -1
        found = False
        if x.startswith('__'): status = 0 
        elif x in lattr: status = 1 
        elif x[0] == '_' and x[1].isalpha():
            for pref in allPref:
                if x.startswith(pref):
                    status = 3
                    private.add(x[len(pref):])
                    found = True
                    break
        elif not found and x in lattr: status = 4
        else: status = 5 ; public.add(x)
        #print(status)
        
    for x in public.copy() :
        if hasattr(klass, x) and isinstance(getattr(klass, x), property):
            public.discard(x)
            continue
        if zapit is not None and hasattr(subKlass,x) and isinstance(getattr(subKlass, x), property):
            public.discard(x)
            continue
        
        try:
            if callable(getattr(obj,x)): public.discard(x)
        except AttributeError as _0:
            warnings.warn("Warning uninitialized attribute")
            print(_0)
            public.discard(x)
        except Exception as _e:
            print(_e)
            
    for x in protected.copy() :
        if hasattr(klass, x) and isinstance(getattr(klass, x), property):
            protected.discard(x)
            continue
        if zapit is not None and hasattr(subKlass, x) and isinstance(getattr(subKlass, x), property):
            protected.discard(x)
            continue
        try:
            if callable(getattr(obj,x)): public.discard(x)
        except AttributeError as _0:
            warnings.warn("Warning uninitialized attribute")
            print(_0)
            public.discard(x)
        except Exception as _e:
            print(_e)

    badV = set([])
    badV.update(protected, public)

    for val in badV.copy():
        sz = len("test attribut {}".format(val))
        _diagnostic = subtest_readonly(obj, val)
        if _diagnostic.count('E') - val.count('E') == 0: badV.discard(val)
    return len(badV), badV


#------------------------- coroutining untested ---------------------#
def coroutine(fun):
    @functools.wraps(fun)
    def enveloppe(*args, **kwargs):
        generateur = fun(*args, **kwargs)
        next(generateur)
        return generateur
    return enveloppe
#--------------------- duck typing for abstract class -----------------------#
if sys.version_info[:2] >= (3, 3):
    def has_methods(*methods):
        def decorator(Base):
            def __subclasshook__(Class, Subclass):
                if Class is Base:
                    attributes = collections.ChainMap(*(Superclass.__dict__
                            for Superclass in Subclass.__mro__))
                    if all(method in attributes for method in methods):
                        return True
                return NotImplemented
            Base.__subclasshook__ = classmethod(__subclasshook__)
            return Base
        return decorator
else:
    def has_methods(*methods):
        def decorator(Base):
            print(Base, methods)
            def __subclasshook__(Class, Subclass):
                if Class is Base:
                    needed = set(methods)
                    for Superclass in Subclass.__mro__:
                        for meth in needed.copy():
                            if meth in Superclass.__dict__:
                                needed.discard(meth)
                        if not needed:
                            return True
                return NotImplemented
            Base.__subclasshook__ = classmethod(__subclasshook__)
            return Base
        return decorator

#======== lovely debug handler =========================================#
if __debug__: # Programming in Python3 by Mark Summerfield
    logger = logging.getLogger("Trace")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(os.path.join(tempfile.gettempdir(),
                                               "trace.log"))
    logger.addHandler(handler)
    def tracing(fonction):
        @functools.wraps(fonction)
        def enveloppe(*args, **kw):
            log = "called: " + fonction.__name__ + "("
            log += ", ".join(["{0!r}".format(_) for _ in args] +
                             ["{0!s} = {1!r}".format(k, v)
                              for k, v in kw.items()])
            result = exception = None
            try:
                result = fonction(*args, **kw)
                return result
            except Exception as _e:
                exception = _e
            finally:
                log += (") -> "+str(result) if exception is None
                             else ") {0}: {1}".format(type(exception),
                                                      exception))
                logger.debug(log)
                if exception is not None:
                    raise exception
        return enveloppe
else:
    def tracing(fonction):
        return fonction

if __name__ == "__main__":
    print("="*3, "petits tests sur l'utilisation de @signature", "="*3)
    @tracing
    @signature
    def fun(x: int, y: int) -> any : return x+y
    try:
        print('fun(3, 4) =', end=' ')
        print(fun(3, 4))
        print('fun(3., 4) =', end=' ')
        print(fun(3., 4))
    except Exception as _e:
        print("failure\n", _e)
    @signature
    def gun(x: int, y: float = 1.2) -> int: y**x # genere une erreur 
    try:
        print('gun(3)', gun(3))
        print('gun(3., 4)', gun(3., 4))
    except Exception as _e:
        print(_e)

    @checkMe
    class XX:
        a = Controle(lambda _, x: isinstance(x, int))
        b = Controle(lambda _, x: isinstance(x, int), True)
        def __init__(self, v):
            self.a = v
            self.b = v
            
        def __str__(self): return "a = {0.a}, b = {0.b}".format(self)
    
    print("\n\n")
    print("="*3, "petit test sur attribut de la classe", XX.__name__, "="*3)
    u = XX(42)
    print("a", XX.a.__doc__)
    print("b", XX.b.__doc__)    
    print(u)
    print('u.__dict__', u.__dict__)
    print('modification de u.a = 124', end=' ')
    u.a = 124
    print('reussite', u)
    print('modification de u.b = 24', end=' ')
    u.b = 24
    print('echec', u)

    print("\n\n")
    print("="*3, "petit test avec check_property", "="*3)
    print(check_property(1 == 1//3, "test idiot //", "X"))
    print(check_property(1 == 1%3, "test idiot modulo", "X"))

    print("\n\n")
    print("="*3, "les attributs sont-ils readonly", "="*3)
    print(subtest_readonly(u, 'a b a'))


    print("meilleure compréhension de has_methods, faut une abstract classe")
    @has_methods(* "gagnant perdant adversaire".split())
    class Bidon(metaclass=abc.ABCMeta): pass

    class Fake:
        def __init__(self): pass
        def gagnant(self): return True
        def perdant(self): return False
        def adversaire(self): return "gloups"

    class Fake2:
        def __init__(self): pass
        def gagnant(self): return True
        def perdant(self): return False

    class Fake3(Bidon): pass
    class Fake4(Fake2):
        def adversaire(self): return None

    for klass in (Fake, Fake2, Fake3, Fake4):
        a = klass()
        print("{:<7s} obj instance of Bidon ? {}".format(a.__class__.__name__,
                                                     isinstance(a, Bidon)))

    print("même question mais ce coup ci sans metaclass")
    @has_methods(* "gagnant perdant adversaire".split())
    class Bidon: pass

    class Fake:
        def __init__(self): pass
        def gagnant(self): return True
        def perdant(self): return False
        def adversaire(self): return "gloups"

    class Fake2:
        def __init__(self): pass
        def gagnant(self): return True
        def perdant(self): return False

    class Fake3(Bidon): pass
    class Fake4(Fake2):
        def adversaire(self): return None

    for klass in (Fake, Fake2, Fake3, Fake4):
        a = klass()
        print("{:<7s} obj instance of Bidon ? {}".format(a.__class__.__name__,
                                                     isinstance(a, Bidon)))
        
