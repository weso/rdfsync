""" Module to get the names of each subject, predicate, object of a triple individually"""

def get_triple_subject_str(subject):
    subject_to_string = str(subject).rsplit("/", 1)[-1]
    subject_name = subject_to_string.rpartition("#")[2]
    return subject_name

def get_triple_predicate_str(predicate):
    predicate_to_string = str(predicate).rsplit("/", 1)[-1]
    prd_name = predicate_to_string.rpartition("#")[2]
    return prd_name

def get_triple_object_str(object):
    object_to_string = str(object).rsplit("/", 1)[-1]
    obj_name = object_to_string.rpartition("#")[2]
    return obj_name

def get_namespace(link_string):
    if '#' in link_string :
        i = link_string.index('#')
        return link_string[:i + len('#')]
    else:
        link_string.rsplit('/', 1)
        return link_string.rsplit('/', 1)[0] + '/'

