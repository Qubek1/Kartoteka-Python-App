import xml.etree.ElementTree as ET
 
tree = ET.parse('12_24_3EFNF6_PL8216_0001_20250106201837.xml')
root = tree.getroot()

def tree_to_string(node, tabs = ""):
    t = tabs + node.tag[48:] + " " + str(node.attrib) + "\n"
    tabs += " "
    if len(node) == 0:
        if not node.text:
            return ""
        return t + tabs + node.text + "\n"
    for child in node:
        t += tabs + tree_to_string(child, tabs) + "\n"
    return t

#print(tree_to_string(root))
#print(root.findall("MsgId"))
print(root[0].tag)
print(root.findall("{urn:iso:std:iso:20022:tech:xsd:camt.053.001.02}BkToCstmrStmt")[0].tag)