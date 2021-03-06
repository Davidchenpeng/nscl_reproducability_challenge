__all__ = ['CLEVRDefinition', 'QuestionTypes']

from enum import Enum


class CLEVRDefinition(object):
    attribute_concept_map = {
        'color': ['gray', 'red', 'blue', 'green', 'brown', 'purple', 'cyan', 'yellow'],
        'material': ['rubber', 'metal'],
        'shape': ['cube', 'sphere', 'cylinder'],
        'size': ['small', 'large']
    }

    concept_attribute_map = {
        'gray': 'color',
        'red': 'color',
        'blue': 'color',
        'green': 'color',
        'brown': 'color',
        'purple': 'color',
        'cyan': 'color',
        'yellow': 'color',
        'rubber': 'material',
        'metal': 'material',
        'cube': 'shape',
        'sphere': 'shape',
        'cylinder': 'shape',
        'small': 'size',
        'large': 'size'
    }

    relation_concept_map = {
        'spatial': ['left', 'right', 'front', 'behind']
    }

    @staticmethod
    def get_all_attributes():
        return CLEVRDefinition.attribute_concept_map.keys()

    @staticmethod
    def get_all_relations():
        return CLEVRDefinition.relation_concept_map.keys()

    @staticmethod
    def get_all_concepts():
        return [c for concepts in CLEVRDefinition.attribute_concept_map.values() for c in concepts]

    @staticmethod
    def get_all_relation_concepts():
        return [c for concepts in CLEVRDefinition.relation_concept_map.values() for c in concepts]

    @staticmethod
    def get_attribute_concept_map(attribute):
        return CLEVRDefinition.attribute_concept_map(attribute)

    @staticmethod
    def get_relation_concept_map(relation):
        return CLEVRDefinition.relation_concept_map(relation)
        
class QuestionTypes(Enum):
    BOOLEAN = 1
    ATTRIBUTE = 2
    COUNT = 3
