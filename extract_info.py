#this script extract specific information about each entity and returns it in a dictionary
#this dictionary is then used to put all the information in a sqlite file

import rdflib
import rdfextras
import json

#load the ontology
rdfextras.registerplugins()
g=rdflib.Graph()

#the workfile is the single rdf file holding the whole graph
g.parse("workfile.rdf")


#declaring all the types
#life_types = ["kingdom","phylum","class","order","family","genus","species"]
life_types = ["kingdom","phylum","superclass","class","superorder","order","suborder","infraorder","superfamily","family","tribe","genus","species"]

#define the prefixes
PREFIX = ''' PREFIX dc:<http://purl.org/dc/terms/> 
             PREFIX wo:<http://purl.org/ontology/wo/> 
             PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
             PREFIX dc:<http://purl.org/dc/terms/> 
	     PREFIX wo:<http://purl.org/ontology/wo/> 
	     PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
	     PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
	     PREFIX foaf:<http://xmlns.com/foaf/0.1/>
	     PREFIX po:<http://purl.org/ontology/po/>
	     PREFIX owl:<http://www.w3.org/2002/07/owl#>
	     PREFIX dctypes:<http://purl.org/dc/dcmitype/>
         '''
#this gonna execute the sparql on the whole rdf graph
def exe(query):
	query = PREFIX + query
	return g.query(query)

#the life object is something static and its information is obtained from this
#url http://www.bbc.co.uk/nature/life
def getLifeObject():
	lifeObject = {}

	lifeObject["label"] = "Life"

	description = ''' Biologists classify life into a hierarchical family tree at the top of which animals that are similar to each other are grouped together. As you travel down the branches of the tree, so the organisms become more closely related.

At the top of the tree are the kingdoms - the major groups into which all living things are categorised - and at the bottom are individual species. Navigating from one of the major kingdoms, and following through the groups, takes you on a journey through the history of life. '''
	
	lifeObject["description"] = description
	
	lifeObject["image"] = "http://theserpent.files.wordpress.com/2008/10/dna-scientific.jpg?w=360&h=360"
	lifeObject["thumbnail"] = "http://theserpent.files.wordpress.com/2008/10/dna-scientific.jpg?w=104&h=83"

	#getting direct subclasses
	direct_subclasses = []

	#adding animal
	animal = {}
	animal["entity_type"] = "kingdom"
	animal["label"] = "Animals"
	animal["entity"] = "Animal"

	#adding plants
	plant = {}
	plant["entity_type"] = "kingdom"
	plant["label"] = "Plants"
	plant["entity"] = "Plant"


	#adding fungus
	fungus = {}
	fungus["entity_type"] = "kingdom"
	fungus["label"] = "Fungus"
	fungus["entity"] = "Fungus"

	#adding chromista
	chromista = {}
	chromista["entity_type"] = "kingdom"
	chromista["label"] = "Chromista"
	chromista["entity"] = "Chromista"

	direct_subclasses.append(animal)	
	direct_subclasses.append(plant)	
	direct_subclasses.append(fungus)	
	direct_subclasses.append(chromista)	

	lifeObject["direct_subclasses"] = direct_subclasses
	
	return str(json.dumps(lifeObject))

#return an entity
def getEntity(entity_type,entity):
	lifeObject = {}

	columns = ["entity","entity_type","label","direct_subclasses","description","common_names","scientific_names","kingdomName","phylumName","className","orderName","familyName","genusName","image","thumbnail","sound"]
	
	for column in columns:
		lifeObject[column] = ""

	

	lifeObject["entity"] = entity
	lifeObject["entity_type"] = entity_type
	

	#getting the type of the entity
	entity_url = "<file:///nature/life/" + entity + "#" + entity_type.lower() +">"
	name_entity_url = "<file:///nature/" + entity_type.lower() +"/"+ entity + "#name>"

	#getting the label of the requested entity
        query = "SELECT ?label WHERE { entity_url rdfs:label ?label }"
	query = query.replace("entity_url",entity_url)
        result_set = exe(query)
        for row in result_set:
                lifeObject["label"] = row[0].toPython()

	

	#the types the subclasses will be 
	subclass_types = life_types[life_types.index(entity_type)+1:]

	#the variable what will hold all the subclass types we need
	search_subclass_types = ""
	for subclass_type in subclass_types:
		search_subclass_types = search_subclass_types + "wo:"+ subclass_type.capitalize()+","		
	search_subclass_types = search_subclass_types[:len(search_subclass_types)-1]


	#getting the direct subclasses
	objs = []
	query = " select ?label ?x ?type where { ?x ?y entity_url . ?x rdf:type ?type . ?x rdfs:label ?label FILTER (?type in ("+search_subclass_types+") && regex(str(?x), '"+entity_type+"','i') ) }"
	query = query.replace("entity_url",entity_url)
	
	result_set = exe(query)
        temp_labels = []
        for row in result_set:
                obj = {}
                label = row[0]
                entity = row[1]
                obj["label"] = label
                obj["entity"] = entity[entity.rfind("/")+1:entity.index("#")]
		obj["entity_type"] = row[2][row[2].rfind("/")+1:].lower()
                objs.append(obj["label"]+"<label>"+obj["entity"])
	lifeObject["direct_subclasses"] = objs

	#getting the description
	query = ''' SELECT ?description 
		    WHERE { ''' + entity_url + ''' dc:description ?description . }'''
	result_set = exe(query)
	for row in result_set:
		description = row[0].n3()				
		lifeObject["description"] = description.replace("\"","")	

	#querying the names
	query = ''' SELECT ?x ?y
		WHERE {
		    ''' + name_entity_url + ''' ?x ?y } '''
	common_names = []
	scientific_names = []
	result_set = exe(query)
	for row in result_set:
		relationName = (str(row[0].toPython())).lower()
		name = row[1].lower()
		if (relationName == "http://purl.org/ontology/wo/commonname"):
			common_names.append(name)
		elif (relationName == "http://purl.org/ontology/wo/scientificname"):
			scientific_names.append(name)
		elif (relationName == "http://purl.org/ontology/wo/kingdomname" and entity_type != "kingdom"):
			lifeObject["kingdomName"] = name
		elif (relationName == "http://purl.org/ontology/wo/phylumname" and entity_type != "phylum"):
			lifeObject["phylumName"] = name
		elif (relationName == "http://purl.org/ontology/wo/classname" and entity_type != "class"):
			lifeObject["className"] = name
		elif (relationName == "http://purl.org/ontology/wo/ordername" and entity_type != "order"):
			lifeObject["orderName"] = name
		elif (relationName == "http://purl.org/ontology/wo/familyname" and entity_type != "family"):
			lifeObject["familyName"] = name
		elif (relationName == "http://purl.org/ontology/wo/genusname" and entity_type != "genus"):
			lifeObject["genusName"] = name
		elif (relationName == "http://purl.org/ontology/wo/speciesname"):
			lifeObject["speciesName"] = name
		
		elif (relationName == "http://purl.org/ontology/wo/superordername"):
			lifeObject["superorderName"] = name
	lifeObject["common_names"] = common_names
	lifeObject["scientific_names"] = scientific_names

	#getting the proper names
	#because the names obtained above are scientific names
	#for some, the common names exist, e.g. for kingdom, we'll get animalia instead of animals
	#when the object animalia exist and thus animals can be retrieved
	#getting the label of the requested entity
        query = '''SELECT ?relation ?label 
		    WHERE { entity_url  ?relation ?obj. ?obj rdfs:label ?label FILTER (?relation in (wo:kingdom,wo:phylum,wo:class,wo:order,wo:family,wo:genus,wo:species,wo:superorder,wo:superfamily,wo:infraorder,wo:tribe,wo:suborder,wo:superclass))}'''

	query = query.replace("entity_url",entity_url)
	result_set = exe(query)
        for row in result_set:
		relationName = (str(row[0].toPython())).lower()
		name = (str(row[1].toPython())).lower().capitalize()
		if (relationName == "http://purl.org/ontology/wo/kingdom"):
			lifeObject["kingdomName"] = name
		elif (relationName == "http://purl.org/ontology/wo/phylum"):
			lifeObject["phylumName"] = name
		elif (relationName == "http://purl.org/ontology/wo/class"):
			lifeObject["className"] = name
		elif (relationName == "http://purl.org/ontology/wo/order"):
			lifeObject["orderName"] = name
		elif (relationName == "http://purl.org/ontology/wo/family"):
			lifeObject["familyName"] = name
		elif (relationName == "http://purl.org/ontology/wo/genus"):
			lifeObject["genusName"] = name
		elif (relationName == "http://purl.org/ontology/wo/species"):
			lifeObject["speciesName"] = name
		elif (relationName == "http://purl.org/ontology/wo/superorder"):
			lifeObject["superorderName"] = name
		elif (relationName == "http://purl.org/ontology/wo/superfamily"):
			lifeObject["superfamilyName"] = name
		elif (relationName == "http://purl.org/ontology/wo/infraorder"):
			lifeObject["infraorderName"] = name
		elif (relationName == "http://purl.org/ontology/wo/tribe"):
			lifeObject["tribeName"] = name
		elif (relationName == "http://purl.org/ontology/wo/suborder"):
			lifeObject["suborderName"] = name
		elif (relationName == "http://purl.org/ontology/wo/superclass"):
			lifeObject["superclassName"] = name

	if ("speciesName" in lifeObject):
		lifeObject["scientific_names"] = []
		lifeObject["scientific_names"].append(lifeObject["speciesName"])
	
	#querying the images
	query = "SELECT ?image ?thumbnail WHERE {"+entity_url+" foaf:depiction ?image . ?image foaf:thumbnail ?thumbnail}"
	result_set = exe(query)
	for row in result_set:
		lifeObject["image"] = row[0].toPython()
		lifeObject["thumbnail"] = row[1].toPython()
	
	#quering the sound
	entity_url = entity_url.replace("life",entity_type.lower())
	query = "SELECT ?x WHERE {?x rdf:type dctypes:Sound . ?x dc:subject "+entity_url+" }"
	result_set = exe(query)
	for row in result_set:
		lifeObject["sound"] = row[0].toPython()

	return lifeObject
