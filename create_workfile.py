import rdflib
import rdfextras
import json

#create the graph 
rdfextras.registerplugins()
g=rdflib.Graph()

#files_work contains all the rdf files for all organisms
#files contains the names of all the rdf files, this is just to simply, this file is generated using this commans ls | grep rdf >> files
#opens a file which contains a list of all files in files_work
#can be done differently, that is dynamically get the list of files from file work via system api
allFiles = open('files_work/files','r')

files = allFiles.readlines()
for current_file in files:
        current_file = current_file.replace('\n','')
        #printing is done just to make the process a little more verbose
	print current_file 
        g.parse("files_work/"+current_file)

graph = g.serialize()
f = open('workfile.rdf', 'w')
f.write(graph)
f.close()

