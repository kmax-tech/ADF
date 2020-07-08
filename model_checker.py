#create a little checker, whether the generated results from testinstances.py are identical

import pathlib

#Input are the files stored in testresults w.r.t. to each semantics we have two textfiles results for the two and three-valued approach.
#These files have a common naming pattern.

filepath = "./testresults/"
nameclass = "testinstances_class.txt" #textfiles, which store the data for the two-valued approach
nametri = "testinstances_tri.txt" #textfiles, which store the data for the three-valued approach

#the base names of the files are stored in namelist, together with filepath,nameclass and nametri the complete filepaths are created
namelist =["unitadmissibletest_","unitcompletetest_","unitpreferredtest_","unitgroundtest_"]

#loads two textfiles into a list for futher processing
def list_loader(path_to_classical,path_to_tri):
    class_representation = []
    tri_representation = []
    with open(path_to_classical,"r") as classical, open(path_to_tri,"r") as tri:
        for line in classical:
            class_representation.append(line)
        for line in tri:
            tri_representation.append(line)
    classical.close()
    tri.close()
    return([class_representation,tri_representation])

#compare interpretations
def compare_models(inp):
    class_representation = inp[0]
    tri_representation = inp[1]
    for idx,line in enumerate(class_representation):
        if line.startswith("#"):
            continue
        if line.startswith("Model:"):
            model_class = eval(line.replace("Model:",""))
            model_tri = eval(tri_representation[idx].replace("Model:",""))
            if model_class != model_tri:
                print("Problem comparing models")
                print(model_class)
                print(model_tri)
        else:
            line = line.replace("Result:","")
            line = line.replace("False", "0.0")
            line = line.replace("True", "1.0")
            line = line.replace("u", "0.5")
            testcase_class = eval(line)
            testcase_tri = eval(tri_representation[idx].replace("Result:",""))
            if testcase_class[:-1] == testcase_tri[:-1]:
                #print("Line {} Accep. Cond. check success".format(idx + 1))
                pass
            else:
                print("Line {} Result check failed".format(idx + 1))
                #print(testcase_class)
                #print(testcase_tri)

#checks several files for same models, if no specific information are printed, the files have the same models
def instance_checker(instancelist):
    for instance in instancelist:
        cmp_instances = list_loader(pathlib.Path(filepath + instance + nameclass), pathlib.Path(filepath + instance + nametri))
        print("Comparing Models for {} semantics".format(instance))
        print("Class File has {} lines | Tri file has {} lines".format(len(cmp_instances[0]),len(cmp_instances[1])))
        compare_models(cmp_instances)

#generates the filepaths and check the files
instance_checker(namelist)