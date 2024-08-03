import re

# For testing!!
ALL_TRANSITIVE_RELATIONS = False


ID = "[a-zA-Z0-9_]*"
REL_TYPES = "[a-zA-Z0-9_|]*"
regex_pattern_with_col = (
    rf"<?-\[{ID}?:({REL_TYPES})(\*?)[0-9]*\.?\.?[0-9]*\]-?"
)
# if no : then everything inside the [] is the rel name
regex_pattern_without_col = (
    rf"<?-\[({REL_TYPES})(\*?)[0-9]*\.?\.?[0-9]*\]->?"
)
# 
# 4th capture is *

def update_relations_with_col(match):

    print("match", match.group(0))
    rel_type = match.group(1)
    astriks = match.group(2)
    if astriks:
        return match.group(0)
    else:
        # no astriks 
        if is_transitive(rel_type):
            return match.group(0).replace(f":{rel_type}", f":{rel_type}*")
    


def update_relations_without_col(match):
    rel_type = match.group(1)
    astriks = match.group(2)
    if astriks:
        return match.group(0)
    else:
        # no astriks 
        if is_transitive(rel_type):
            return match.group(0).replace(f"[{rel_type}]", f"[{rel_type}*]")




def update_query(q, force=False):
    global ALL_TRANSITIVE_RELATIONS
    ALL_TRANSITIVE_RELATIONS = force
    non_matching_kw = ["CALL","CREATE","DELETE","DETACH","FOREACH","LOAD","MERGE","OPTIONAL","REMOVE","RETURN","SET","START","UNION","UNWIND","WITH"]
    matching_kw = ["MATCH"]
    isMatching = False
    updated_query = ""
    for word in q.split():
        # only update query for maching_kw. Otherwise, return the query as is
        if word.upper() in matching_kw:
            isMatching = True
            new = word
        elif word.upper() in non_matching_kw:
            isMatching = False
            new = word
        # check if contain relationships
        if isMatching:
            new = word
            new = re.sub(regex_pattern_with_col, update_relations_with_col, word)
            new = re.sub(regex_pattern_without_col, update_relations_without_col, new)
        else:
            new = word
        updated_query += new + " "
    # remove the last space
    return updated_query[:-1]

    




def is_transitive(q):
    if ALL_TRANSITIVE_RELATIONS == True:
        return True
    else:
        return True


def extract_relations():
    pass
