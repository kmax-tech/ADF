#This script calculates the semantics of ADFs,therefore the variables nodes and chooseinterpretations have to be edited by the user
import itertools, re, functools, time

#enter each node (n) and its acceptance condition (ac) as a list [n,ac] into the variable nodes
#syntax: (,) for logical and, (;) for logical or, (#) for negation, also parentheses are allowed
nodes = [["b","#w,b"],["h","(w;b)"],["r","?"],["s","h,b"],["w","#r,#b"]]

#specify the interpretations, which shall be calculated: a - admissible, c - complete, p - preferred, g - ground, tri - use Kleene's strong three-valued logic
chooseinterpretations= ["a","c"]

class ParseAndPrepare():  #class for the nodes and the acceptance conditions
    def __init__(self,inp,chooseinterpretations):
        self.chooseinterpretations = chooseinterpretations
        self.formulas = inp
        self.nodenames = self.nodenameFunc(self.formulas)
        self.lengthnodes = len(self.nodenames)  #number of nodes used
        self.trivalues = ["0.0", "0.5", "1.0"] #for calculation with Kleene's strong three-valued logic
        self.twovalues = ["False", "u", "True"] #for calculation with Python build-in boolean logic
        self.twovaluedconnectives = [(",", " and "), (";", " or "), ("#", " not "), ("!", " True "), ("?", " False ")]
        self.trivaluedconnectives = [(",", " & "), (";", " | "), ("#", " ~ "), ("!", " ThreeLogics(1) "), ("?", " ThreeLogics(0) ")]
        if "tri" in self.chooseinterpretations:
            self.interpretations = self.interpretCreate(self.trivalues)
            self.preparedformulas = self.listReplacer(self.formulaPrepare(), self.trivaluedconnectives)
            self.undefinednode = "0.5"
        else:
            self.interpretations = self.interpretCreate(self.twovalues)
            self.preparedformulas = self.listReplacer(self.formulaPrepare(), self.twovaluedconnectives)
            self.undefinednode = "u"

    def nodenameFunc(self, inp):
        nodenames = set()
        [nodenames.add(x[0]) for x in inp]
        return list(sorted(nodenames))

    def interpretCreate(self,x):
        for interpretation in itertools.product(x, repeat=self.lengthnodes):
            testit = dict(zip(self.nodenames, interpretation))  #use generator because of possible list size
            yield testit

    def listReplacer(self,inp,connectives): #replace logical connectives with their corresponding connective
        for x in inp:
            for ind,lit in enumerate(x[1]):
                x[1][ind] = (functools.reduce(lambda x, y: x.replace(y[0], y[1]), ([lit] + connectives)))
        return inp

    def listTeardown(self, input):  #teardown a string to a list
        regex = "|".join(sorted(self.nodenames, key=len, reverse=True))
        nodespositions = tuple(x.span() for x in re.finditer(regex, input))
        otherpositions = list(map(lambda x, y: (x[1], y[0]), ((0, 0),) + nodespositions, nodespositions + ((None, None),)))
        return [input[x:y] for x, y in sorted(itertools.chain(list(nodespositions), otherpositions))]

    def lookup(self, input):  #for an efficient replacement of the interpretation value the positions of all nodes in an acceptance condition are marked
        startindex = {node: [] for node in self.nodenames if node in input}  #an empty dictionary for the formula
        [startindex[node].append(position) for position, node in enumerate(input) if node in startindex]  #add the positions of the formulas
        return startindex

    def formulaMarkNodes(self, node, formula):
        subs = self.listTeardown(formula)
        return ([node, subs, self.lookup(subs)])

    def formulaPrepare(self): #sort according to the amount of nodes in an acceptance condition
        return sorted([self.formulaMarkNodes(node, formula) for node, formula in self.formulas],key=lambda form: len(form[2]))

class ThreeLogics: #an implementation of Kleenes strong three-valued logic
    def __init__(self, a):
        self.a = float(a)
    def __str__(self):
            return str(self.a)
    def __and__(self, o):
        return ThreeLogics(min(self.a,o.a))
    def __or__(self, o):
        return ThreeLogics(max(self.a,o.a))
    def __invert__(self):
        return ThreeLogics(1 - self.a)

class EvaluateAndInterprete(ParseAndPrepare): #this class inherits the prepared formulas from parseandprepare and evaluates the interpretations
    def __init__(self, formulas, chooseinterpretations):
        ParseAndPrepare.__init__(self,formulas,chooseinterpretations)
        if self.undefinednode == "u":
            self.pre = ""
            self.post = ""
        else:
            self.pre = " ThreeLogics("
            self.post = ") "

    def formEval(self, interpretation):  #evaluates all nodes, given an interpretation
        #print("formevalinp",interpretation)
        calculatedinterpretation = {}  #we start with an empty dictionary for the final interpretations
        for formula in self.preparedformulas:
            for node, index in formula[2].items():
                for position in index:
                        formula[1][position] = self.pre + interpretation[node] + self.post
            calculatedinterpretation.update({formula[0]: str(eval("".join(formula[1])))})
        #print("eval",calculatedinterpretation)
        return calculatedinterpretation

    def gammaopTwoval(self, interpretation):  #evaluates according to the gamma operator with the Python built in two-valued logic
        #print("Gamma using interpretation", interpretation)
        undefinednodes = []  #to mark the nodes which are undefined in an interpretation
        usednodes = [node for node in self.nodenames]  #to mark the nodes, which have been already used
        twovaluedinterpretation = {}
        finalgammaint = {}
        for node, value in interpretation.items(): #filter out nodes, which don't have the value undefined
            if value != "u":  #for other values than u, the completion has the exact same values
                twovaluedinterpretation.update({node: value})
            else:
                undefinednodes.append(node)
        if undefinednodes == []:  #means that we have no undefined values in the interpretation and need no two-valued completions
            #print("exting here")
            return self.formEval(twovaluedinterpretation)
        #print("Gamma two-valued interpretation",twovaluedinterpretation,"undefined",undefinednodes)
        interpretationgenerator = itertools.product(["True", "False"], repeat=len(undefinednodes)) #for the undefined nodes the two-valued completions are generated
        item = next(interpretationgenerator)
        gammabase = self.formEval({**twovaluedinterpretation, **dict(zip(undefinednodes, item))})  #the first two-valued interpretation for the comparison
        #print("gammabase",gammabase)
        for values in interpretationgenerator:
            intupdatenodes = dict(zip(undefinednodes, values))
            #print("update",{**twovaluedinterpretation, **intupdatenodes})
            currentint = self.formEval({**twovaluedinterpretation, **intupdatenodes})  #the current calculated two-valued interpretation
            #print("currentint",currentint)
            if usednodes != []:
                differenceinterpretations = set(gammabase.items()) - set(
                    currentint.items())  #find interpretations, which are different in the two sets
                [finalgammaint.update({node: "u"}) for node, value in differenceinterpretations if node in usednodes] #for the nodes in differenceinterpretations the value of the gammaoperatos is "u"
                [usednodes.remove(node) for node, value in finalgammaint.items() if node in usednodes] #remove the nodes to mark that the gamma interpretation of them has been found
                #print("usdendoes",usednodes)
            else:  #means that we found every evaluation for the gamma interpreter
                #print("leaving")
                break
        [finalgammaint.update({node: str(value)}) for node, value in gammabase.items() if node in usednodes]  #for the case that usednodes is not empty
        return finalgammaint

    def gammaopTrival(self,interpretation): #faster method for calculation
        #print("Gamma using tri-valued interpretation", interpretation)
        #print("Gamma tri-valued interpretation evaluated",self.formEval(interpretation))
        return self.formEval(interpretation)

    def groundCalc(self,x):
        #print("Welcome to the grounded calculation")
        interpretation = dict(zip(self.nodenames,[self.undefinednode] * self.lengthnodes)) #we start with the interpretation, where everything is set to undefined
        print("interpretation", interpretation)
        gammainterpretation = x(interpretation)
        #print("gammaint", gammainterpretation)
        while (interpretation != gammainterpretation):
            interpretation = gammainterpretation
            gammainterpretation = x(gammainterpretation)
            #print("gammaint", gammainterpretation)
        return gammainterpretation

    def ordprint(self, inlist):  #prints the ordered interpretations
        for index, x in enumerate(inlist):
            print("Nr.{}".format(index + 1) , [node + ":" + value for node,value in sorted(x.items())], "\n")

    def gammacompare(self, interp, gammainterp):  #compares two evaluations
        #print("gammacompare",interp,gammainterp)
        for node in self.nodenames:
            if (interp[node] != self.undefinednode) and (interp[node] != gammainterp[node]):
                return 0
        return gammainterp

class ControlAndPrint(EvaluateAndInterprete):
    def __init__(self, formulas,chooseinterpretations):
        EvaluateAndInterprete.__init__(self, formulas,chooseinterpretations)

    def intmaxadmissible(self,interpretation1, interpretation2):
        marker = []
        for node in interpretation1:
            if (interpretation1[node]) != self.undefinednode and (interpretation1[node] == interpretation2[node]):
                continue
            if (interpretation1[node]) != self.undefinednode and (interpretation1[node] != interpretation2[node]):
                return -1  #here interpretation2 is not more admissible than interpretation1
            if (interpretation1[node]) == self.undefinednode and (interpretation2[node] != self.undefinednode):
                marker.append("x")
            else:
                continue
        return 1  #interpretation2 is more admissible

    def preferred(self,interpretations):
        leninters = len(interpretations) - 1
        prefinterpretations = []  #we start with an empty list
        for index, testval in enumerate(interpretations):
            checkinterpretation = 0
            for testinterpretation in (interpretations[0:index] + interpretations[index + 1:]):
                calcvalue = self.intmaxadmissible(testinterpretation, testval)
                if calcvalue == 1:
                    checkinterpretation += 1
                if calcvalue == -1:
                    if self.intmaxadmissible(testval, testinterpretation) == -1:
                        checkinterpretation += 1
                    else:
                        break  #we found an counterexample which is more admissible, that's why the search can be stopped here
            if (checkinterpretation == leninters):  #testval is more admissible than any other interpretation
                prefinterpretations.append(testval)
                continue
        return prefinterpretations

    def interevaluator(self):
        intadm = [] #list of final interpretations, admissible, complete, preferred, ground
        intcomp = []
        intpref = []
        intground = []
        if "tri" in self.chooseinterpretations:
            gamma = self.gammaopTrival
        else:
            gamma = self.gammaopTwoval
        if (("a" in self.chooseinterpretations) or ("c" in self.chooseinterpretations) or ("p" in self.chooseinterpretations)):
            for interpretation in self.interpretations:
                gammatemp = self.gammacompare(interpretation, gamma(interpretation))
                if "a" in self.chooseinterpretations:
                    if gammatemp != 0:
                        intadm.append(interpretation)
                if (("p" in self.chooseinterpretations) or ("c"in self.chooseinterpretations)):
                    if gammatemp == interpretation:
                        intcomp.append(interpretation)
            if "p" in self.chooseinterpretations:
                intpref = (self.preferred(intcomp))
        if "g" in self.chooseinterpretations:
            intground.append(self.groundCalc(gamma))
        #print([intadm, intcomp, intpref, intground])
        return [intadm, intcomp, intpref, intground]

    def interprinter(self):
        inter = self.interevaluator()
        if "a" in self.chooseinterpretations:
            print("Admissible Interpretations \n")
            self.ordprint(inter[0])
        if "c" in self.chooseinterpretations:
            print("Complete Interpretations \n")
            self.ordprint(inter[1])
        if "p" in self.chooseinterpretations:
            print("Preferred Interpretations \n")
            self.ordprint(inter[2])
        if "g" in self.chooseinterpretations:
            print("Ground Interpretations \n")
            self.ordprint(inter[3])

if __name__ == "__main__":
    x = ControlAndPrint(nodes,chooseinterpretations)
    print("Formatted Formula \n")
    print(x.preparedformulas, "\n")
    start = time.time()
    x.interprinter()
    end = time.time()
    print("Total Time")
    print(end - start)





