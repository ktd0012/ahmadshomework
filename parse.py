#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from syntax import *


# I *Ahmad Elgazzar* have written all of this project myself, without any
# unauthorized assistance, and have followed the academic honor code.


def lex(s):
    seq = []
    while s:
        whitespace = re.match(r"^( +)|(\n)+",s)
        if whitespace != None:
            s = s[len(whitespace.group(0)):]
        keyword = re.match(r"^proc|if|else|while|print|ret",s)
        if keyword != None:
            seq.append(keyword.group(0))
            s = s[len(keyword.group(0)):]  
        num = re.match(r"^([0-9]+|[0-9]*[.][0-9]+)",s)
        if num != None:
            seq.append(num.group(0))
            s = s[len(num.group(0)):]  
        id = re.match(r"^([_A-Za-z][_A-Za-z0-9]*)|(>)+|(\.)+",s)
        if id != None:
            seq.append(id.group(0))
            s = s[len(id.group(0)):]
        symbol = re.match(r"^\+|\-|\/|\*|\^|\,|\:|\=|\<|\{|\}|\(|\)|\;",s)
        if symbol != None:
            seq.append(symbol.group(0))
            s = s[len(symbol.group(0)):]
    return seq

# print(lex("// we pass fact to itself as otherwise fact is not closed over its own binding, fact -> proc...if m < 2 {1           }/***/else/**/{"))

def parse(toks):
    # print(toks) 
    def isId(s):
        # TODO: return true iff string s is not a keyword but is an identifier (as defined in the Canvas announcement on Project 3). X?
        if s != "proc" or s!= "if" or s!= "else" or s != "while" or s != "print" or s!= "ret":
            m = re.match("^([_A-Za-z][_A-Za-z0-9]*)|(>)+|(\.)+", s)
            if m:
                return True
            else:
                return False
        else:
            return False
    def isNum(s):
        return re.match(r"^([0-9]+|[0-9]*[.][0-9]+)", s) != None
    def peek(n):
        nonlocal toks
        if len(toks) > n:
            return toks[n]
        else:
            return ""
    def expect(s):
        nonlocal toks
        # print(s)
        # print(peek(0))
        if peek(0) == s:
            toks = toks[1:]
            # print(s)
            # print(peek(0))
        else:
            print("Error: expected a token")
            exit(1)

    def parseP():
        s = parseS()
        while peek(0) == ";":
            expect(";")
            s = SeqStmt(s,parseS()) # See: syntax.py
        return s

    def parseS():
        if peek(0) == "proc":
            expect("proc")
            if not isId(peek(0)):
                print("Error expected name of defined function: Expected %s" % (peek(0)))
            func = Var(peek(0))
            expect(peek(0))
            expect("(")
            param = []
            if peek(0) != ")":
                param = [Var(peek(0))]
                expect(peek(0))
                while peek(0) == ",":
                    expect(",")
                    if not isId(peek(0)):
                        print("Error expected variable in paramater list but observed: %s" % (peek(0)))
                    param.append(Var(peek(0)))
                    expect(peek(0))
            expect(")")
            expect("{")
            body = parseP()
            expect("}")
            return ProcStmt(func, param, body)
        elif peek(0) == "if":
            expect("if")
            ge = parseC()
            expect("{")
            tbody = parseP()
            expect("}")
            expect("else")
            expect("{")
            fbody = parseP()
            expect("}")
            return IfStmt(ge, tbody, fbody)
        elif peek(0) == "while":
            g = parseC()
            expect("{")
            bdy = parseP()
            expect("}")
            return WhileStmt(g, bdy)
        elif peek(0) == "print":
            expect("print")
            return PrintStmt(parseC())
        else:
            return parseC()
    
    def parseC():
        e = parseE()
        while peek(0) == "<" or peek(0) == "=":
            if peek(0) == "<":
                expect("<")
                e = LessThan(e,parseE())
            elif peek(0) == "=":
                expect("=")
                e = Equal(e,parseE())
            else:
                print("Error expected variable in paramater list but observed: %s" % (peek(0)))
        return e

    def parseE():
        a = parseT()
        while peek(0) == "+" or peek(0) == "-":
            if peek(0) == "+":
                expect("+")
                a = Plus(a,parseT()) 
            else:
                expect("-")
                a = Minus(a,parseT())
        return a
    
    def parseT():
        a = parseF()
        while peek(0) == "*" or peek(0) == "/":
            if peek(0) == "*":
                expect("*")
                a = Mult(a,parseF()) 
            else:
                expect("/")
                a = Div(a,parseF())
        return a
    
    def parseF():
        a = parseA()
        if peek(0) == "^":
            expect("^")
            return Expo(a,parseF())
        else:
            return a

    def parseA():
        if peek(0) == "(":
            expect("(")
            c = parseC()
            expect(")")
            return c
        elif isId(peek(0)):
            term = Var(peek(0))
            expect(peek(0))
            if peek(0) == ":":
                expect(":")
                expect("=")
                a = parseC()
                return Assign(term, a)
            elif peek(0) == "(":
                expect("(")
                if peek(0) != ")":
                    param = [parseC()]
                    while peek(0) == ",":
                        expect(",")
                        param.append(parseC())
                    return Call(term, param)
                expect(")")
            else:
                return term
        elif isNum(peek(0)):
            print(peek(0))
            expect(peek(0))
            print(peek(0))
            return Lit(peek(0))
    
    # TODO: parse and return an AST node or ErrorMsg object (also in syntax.py)
    # TODO: parse and return an AST node or ErrorMsg object
    return parseP()

    
    # tok_list = []
    # s = str(s)
    # s = re.split(r"[ \n]",s)
    # while("" in s):
    #     s.remove("")
    # while s:
    #     if s[0] == "proc" or s[0] == "if" or s[0] == "else" or s[0] == "while" or s[0] == "print" or s[0] == "ret":
    #         tok_list.append(s[0])
    #         s.remove(s[0])
    #     elif s[0] == "+" or s[0] == "-" or s[0] == "/" or s[0] == "^" or s[0] == "," or s[0] == ":" or s[0] == "=" or s[0] == "<" or s[0] == "{" or s[0] == "}" or s[0] == "(" or s[0] == ")" or s[0] == ";":
    #         tok_list.append(s[0])
    #         s.remove(s[0])
    #     elif s[0].isdigit():
    #         tok_list.append(s[0])
    #         s.remove(s[0])
    #     elif re.match("[_A-Za-z][_A-Za-z0-9]*", s[0]) != None:
    #         m = re.match("[_A-Za-z][_A-Za-z0-9]*", s[0])
    #         tok_list.append(m.group(0))
    #         s.insert(1, s[0][len(m.group(0)):])
    #         s.remove(s[0])
    #     else:
    #         for j in range(len(s[0])):
    #             tok_list.append(s[0][j])
    #         s.remove(s[0])
    # return tok_list