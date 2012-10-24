import unittest

import maya.mel as mel
import pymel.core as pm

import pymel.tools.py2mel as py2mel

WRAPPED_CMDS = {}

class MyClassNoArgs(object):
    def noArgs(self):
        return "foo"
    
    def oneArg(self, arg1):
        return arg1 * 2
    
    def oneKwarg(self, kwarg1='default'):
        return kwarg1 * 2

    def oneArgOneKwarg(self, arg1, kwarg1='default'):
        return arg1 + kwarg1
    
    def oneArgTwoKwarg(self, arg1, kwarg1='ate', kwarg2='trex'):
        return '%s %s %s!' % (arg1, kwarg1, kwarg2)

class testCaseClassWrap(unittest.TestCase):
    def wrapClass(self, toWrap, cmdName, *args, **kwargs):
        global WRAPPED_CMDS
        if cmdName not in WRAPPED_CMDS:
            py2mel.py2melCmd(toWrap, commandName=cmdName, *args, **kwargs)
            WRAPPED_CMDS[cmdName] = toWrap
        elif WRAPPED_CMDS[cmdName] != toWrap:
            raise RuntimeError('error - already another command called %s' % cmdName)

    def test_autoName(self):
        self.wrapClass(MyClassNoArgs, None)
        self.assertEqual(mel.eval('''MyClassNoArgs -noArgs'''), 'foo')
    
    def test_noArgs(self):
        self.wrapClass(MyClassNoArgs, 'myCls')
        self.assertEqual(mel.eval('''myCls -noArgs'''), 'foo')
        
    def test_oneArg(self):
        self.wrapClass(MyClassNoArgs, 'myCls')
        self.assertEqual(mel.eval('''myCls -oneArg stuff'''), 'stuffstuff')
        
    def test_oneKwarg(self):
        self.wrapClass(MyClassNoArgs, 'myCls')
        self.assertEqual(mel.eval('''myCls -oneKwarg goober'''), 'goobergoober')
        
    def test_oneKwarg_notEnoughArgsErr(self):
        self.wrapClass(MyClassNoArgs, 'myCls')
        # tried catch/catchQuiet, but they always return 0...
        self.assertEqual(mel.eval('''myCls -oneKwarg'''), None)
        
    def test_oneArgOneKwarg(self):
        self.wrapClass(MyClassNoArgs, 'myCls')
        self.assertEqual(mel.eval('''myCls -oneArgOneKwarg stuff thing'''), 'stuffthing')
        
    def test_oneArgOneKwarg_notEnoughArgsErr(self):
        self.wrapClass(MyClassNoArgs, 'myCls')
        self.assertEqual(mel.eval('''myCls -oneArgOneKwarg'''), None)
        self.assertEqual(mel.eval('''myCls -oneArgOneKwarg stuff'''), None)
        
    def test_nameTooShort(self):
        class ShortFuncCls(object):
            def go(self):
                return 'Manitoba'
        self.wrapClass(ShortFuncCls, 'myShort')
        self.assertEqual(mel.eval('''myShort -goxx'''), 'Manitoba')
        self.assertEqual(mel.eval('''myShort -g'''), 'Manitoba')
        
    def test_excludeFlag(self):
        self.wrapClass(MyClassNoArgs, 'myCls2', excludeFlags=['oneKwarg'])
        self.assertEqual(mel.eval('''myCls2 -oneArg stuff'''), 'stuffstuff')
        self.assertEqual(mel.eval('''myCls2 -oneKwarg goober'''), None)
        
    def test_excludeFlagArg(self):
        self.wrapClass(MyClassNoArgs, 'myCls3', excludeFlagArgs={'oneKwarg':['kwarg1']})
        self.assertEqual(mel.eval('''myCls3 -oneKwarg'''), 'defaultdefault')
        self.assertEqual(mel.eval('''myCls3 -oneKwarg goober'''), None)
        
    def test_excludeFlagArg_orderChanged(self):
        self.wrapClass(MyClassNoArgs, 'myCls3', excludeFlagArgs={'oneArgTwoKwarg':['kwarg1']})
        self.assertEqual(mel.eval('''myCls3 -oneArgTwoKwarg foo'''), None)
        self.assertEqual(mel.eval('''myCls3 -oneArgTwoKwarg "Little Bo PeeP" Batman'''), 'Little Bo PeeP ate Batman!')
        self.assertEqual(mel.eval('''myCls3 -oneArgTwoKwarg defenestrated You Spiderman'''), None)