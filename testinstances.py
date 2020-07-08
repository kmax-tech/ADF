import random,string,time, numpy
import ADFfinal as ADF

#script for generating testinstances and measuring the time

#class takes as input the length of nodes, max 26 nodes can be used, because letters of the alphabet are used
class formula_generator():
    def __init__(self,nbr_nodes):
        self.nbr_nodes = nbr_nodes
        self.alphabetic_representation = string.ascii_lowercase
        self.nodes = self.nodelist_creator()
        self.prob_neg = 0.5
        self.prob_and = 0.5

    def nodelist_creator(self):
        return [ self.alphabetic_representation[x] for x in range(0,self.nbr_nodes) ]

    #model a probability distribution, helps also to determine the number of nodes
    def acceptance_condition_node_selector(self):
        nodelist = []
        for x in range(0,self.nbr_nodes):
            gen_nbr = random.random()
            if (gen_nbr >= 0.5): #possible that nodelist is empty
                nodelist.append(x)
        return nodelist

    #specifies the used connectives
    def connective_determiner(self):
        gen_nbr = random.random()
        if (gen_nbr < self.prob_and):
            return ","
        else: return ";"

    #create the acceptance condition for a single node
    def acceptance_condition_node_writer(self,selected_nodes):
        node_acceptance_condition = ""
        if selected_nodes == []: #contradiction or verum is assumed at this point
            gen_nbr = random.random()
            if (gen_nbr >= 0.5):
                return "?"
            else: return "!"
        for x in selected_nodes:
            current_node = self.nodes[x]
            gen_nbr = random.random()
            if (gen_nbr < self.prob_neg):
                current_node = "#" + current_node
            node_acceptance_condition = node_acceptance_condition + current_node + self.connective_determiner()
        return node_acceptance_condition[:-1] #take out the last connective

    def acceptance_condition_creator(self):
        finalnodes_with_acceptancecondtion = []
        for node in self.nodes:
            acceptcond = self.acceptance_condition_node_writer(self.acceptance_condition_node_selector())
            finalnodes_with_acceptancecondtion.append([node,acceptcond])
        return finalnodes_with_acceptancecondtion

#create a single testinstance
#testinstance = formula_generator(8)
#print(testinstance.acceptance_condition_creator())

#function calculates an ADF given a model with semantics and measures the time
def testcondcalc(testinstance,semantics):
    x = ADF.ControlAndPrint(testinstance,semantics)
    start = time.time()
    interpretetations = x.interevaluator()
    end = time.time()
    time_experiment = end-start
    return [interpretetations,time_experiment]

#just get the time for a testinstance  of a special type for a specified nodesize
def time_tester(start,end,semantics):
    for nodenumber in range(start,end + 1):
        result = ""
        form_gen_instance = formula_generator(nodenumber).acceptance_condition_creator()
        result = testcondcalc(form_gen_instance, semantics)
        print("Calculated {} nodes in {} style within {} seconds".format(nodenumber,semantics,result[1]))
#time_tester(18,20,["tri","a"])

#measures the time between two-valued complnetion and three-valued approach for a specified semantics
def testwriter(start,end,trials,instance_name,semantics):
    file_class_inters = open(instance_name + "_testinstances_class.txt", "w")
    file_tri_inters = open(instance_name + "_testinstances_tri.txt","w")
    file_time_inters = open(instance_name + "_time_compare.txt","w")
    intro_sentence = "#Testing instances from nodesize {} till {} where each nodesize has {} testinstances. Tested are {} semantics \n".format(start,end,trials,semantics)
    help_text = "#Result: first entry is the number of the current testinstance, third entry is the needed calculation time, second one is a list, where the first entry are the admissible interpretations, followed by the complete, preferred and ground ones \n"
    file_class_inters.write(intro_sentence + help_text)
    file_tri_inters.write(intro_sentence + help_text)
    for number_nodes in range(start,end+1): #specify the beginning and end
        file_class_inters.write("#Testing nodesize {} \n".format(number_nodes))
        file_tri_inters.write("#Testing nodesize {} \n".format(number_nodes))
        time_class = []
        time_tri = []
        for number_experiment in range(1,trials + 1):
            print("Testing nodesize {} | Experiment Number {}".format(number_nodes,number_experiment))
            form_gen_instance = formula_generator(number_nodes).acceptance_condition_creator()
            inter_class_results = testcondcalc(form_gen_instance,semantics)
            inter_tri_results = testcondcalc(form_gen_instance,["tri"]+semantics)
            file_class_inters.write("Model: " + str(form_gen_instance) + "\n")
            file_tri_inters.write("Model: " + str(form_gen_instance) + "\n")
            file_class_inters.write("Result: " + str([number_experiment] + inter_class_results) + "\n")
            file_tri_inters.write("Result: " + str([number_experiment] + inter_tri_results) + "\n")
            time_class.append(inter_class_results[1])
            time_tri.append(inter_tri_results[1])
            print("Class time {} | Tri time {}".format(inter_class_results[1],inter_tri_results[1]))
        mean_class_time = numpy.mean(time_class)
        mean_tri_time = numpy.mean(time_tri)
        print("Finished nodes of size {}, with avg. class. time {} and avg. tri time {}".format(number_nodes,mean_class_time,mean_tri_time))
        file_time_inters.write(str([number_nodes,mean_class_time,mean_tri_time]) + "\n")
    file_class_inters.close()
    file_tri_inters.close()
    file_time_inters.close()

#old testcaseinstances
#testwriter(1,10,100,"completetest",["c"])
#testwriter(1,10,100,"admissible_completetest",["a","c"])
#testwriter(1,10,100,"groundtest",["g"])
#testwriter(1,10,100,"preferredtest",["p"])
#testwriter(1,10,100,"admissible_complete_preferredtest",["a","c","p"])
#testwriter(1,10,100,"admissibletest",["a"])
#testwriter(1,10,100,"completetest",["c"])



#a new testcase instance, which tests a list of specified semantics on the same test instances,
# each file gets therefore a class
class sem_writer():
    def __init__(self,inp,sem):
        self.class_inters = open(inp + "_testinstances_class.txt", "w")
        self.tri_inters = open(inp + "_testinstances_tri.txt", "w")
        self.time_inters = open(inp + "_time_compare.txt", "w")
        self.semantics = sem
        self.time_class = [] #here the needed time is appended
        self.time_tri = []  # here the needed time is appended

    def close (self):
        self.class_inters.close()
        self.tri_inters.close()
        self.tri_inters.close()

def mult_testwriter(start,end,trials,instance_names_with_semantics):
    instance_list = []
    for instance_name in instance_names_with_semantics:
        x = sem_writer(instance_name[0],instance_name[1])
        instance_list.append(x)
    for unit in instance_list:
        intro_sentence = "#Testing instances from nodesize {} till {} where each nodesize has {} testinstances. Tested are {} semantics \n".format(start, end, trials, unit.semantics)
        help_text = "#Result: first entry is the number of the current testinstance, third entry is the needed calculation time, second one is a list, where the first entry are the admissible interpretations, followed by the complete, preferred and ground ones. \n"
        unit.class_inters.write(intro_sentence + help_text)
        unit.tri_inters.write(intro_sentence + help_text)
    for number_nodes in range(start,end+1): #specify the beginning and end
        for unit in instance_list:
            unit.class_inters.write("#Testing nodesize {} \n".format(number_nodes))
            unit.tri_inters.write("#Testing nodesize {} \n".format(number_nodes))
        for number_experiment in range(1,trials + 1):
            form_gen_instance = formula_generator(number_nodes).acceptance_condition_creator()
            print("Testing nodesize {} | Experiment Number {}".format(number_nodes, number_experiment))
            for unit in instance_list:
                inter_class_results = testcondcalc(form_gen_instance,unit.semantics)
                inter_tri_results = testcondcalc(form_gen_instance,["tri"]+unit.semantics)
                unit.class_inters.write("Model: " + str(form_gen_instance) + "\n")
                unit.tri_inters.write("Model: " + str(form_gen_instance) + "\n")
                unit.class_inters.write("Result: " + str([number_experiment] + inter_class_results) + "\n")
                unit.tri_inters.write("Result: " + str([number_experiment] + inter_tri_results) + "\n")
                unit.time_class.append(inter_class_results[1])
                unit.time_tri.append(inter_tri_results[1])
                print("Sem {} | Class time {} | Tri time {}".format(unit.semantics,inter_class_results[1],inter_tri_results[1]))
        for unit in instance_list:
            mean_class_time = numpy.mean(unit.time_class)
            mean_tri_time = numpy.mean(unit.time_tri)
            print("Sem {} | Finished nodes of size {}, with avg. class. time {} and avg. tri time {}".format(unit.semantics,number_nodes,mean_class_time,mean_tri_time))
            unit.time_inters.write(str([number_nodes,mean_class_time,mean_tri_time]) + "\n")
            unit.time_class = []
            unit.time_tri = []
    for unit in instance_list:
        unit.close()

#this function was used to create the testfiles in testresults
mult_testwriter(1,10,100,[["unitadmissibletest",["a"]],["unitcompletetest",["c"]],["unitpreferredtest",["p"]],["unitgroundtest",["g"]] ]  )


