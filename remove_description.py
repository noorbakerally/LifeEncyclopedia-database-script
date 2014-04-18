import sys
import libxml2
current_file = libxml2.parseFile(sys.argv[1])
context = current_file.xpathNewContext()
context.xpathRegisterNs("dc", "http://purl.org/dc/terms/")
element_description = context.xpathEval('//dc:description')[0]
description = element_description.getContent().replace("\n",'')
element_description.setContent(description)
f = open(sys.argv[1],'w')
current_file.saveTo(f)
f.close()

