#this file uses the extract_information.py, retrieves the json from the big rdf files 
#and insert the data into an sqlite database
import sqlite3
import extractinfo
#this is the sqlite file which will hold the whole database
conn = sqlite3.connect('life.sqlite')
c = conn.cursor()
#the all_names files contains the names of all entities,
#and we will use name in our sparql to query our information
f = open('all_names')
lines = f.readlines()
f.close()
for line in lines:
	print line
	entity = line.split("/")[1].replace("\n","")
	entity_type = line.split("/")[0]
	sql_beg = 'INSERT INTO life (entity,entity_type,label,direct_subclasses,description,common_names,scientific_names,kingdomname,phylumname,classname,ordername,familyname,genusname,superordername,superfamilyname,infraordername,tribename,superclassname,subordername,image,thumbnail,sound) '
	sql=' VALUES ("entity","entity_type","label","direct_subclasses","description","common_names","scientific_names","kingdomName","phylumName","className","orderName","familyName","genusName","superorderName","superfamilyName","infraorderName","tribeName","superclassName","suborderName","image","thumbnail","sound")'

	columns = ["entity_type","entity","label","description","kingdomName","phylumName","genusName","superorderName","superfamilyName","infraorderName","tribeName","superclassName","suborderName","className","orderName","familyName","image","thumbnail","sound","direct_subclasses","common_names","scientific_names"]
	details = v1.getEntity(entity_type,entity)
	for column in columns:
		if (column == "direct_subclasses"):
			sql = sql.replace("direct_subclasses","<directSubclass>".join(details["direct_subclasses"]))
		elif (column == "common_names"):
			sql = sql.replace("common_names","<common_names>".join(details["common_names"]))
		elif (column == "scientific_names"):
			sql = sql.replace("scientific_names","<scientific_names>".join(details["scientific_names"]))
		else:
			if (not(column in details)):
				value = ""
			else:
				value = details[column]
			sql = sql.replace(column,value)
	final_sql = sql_beg + sql
	c.execute(final_sql)
conn.commit()
conn.close()
