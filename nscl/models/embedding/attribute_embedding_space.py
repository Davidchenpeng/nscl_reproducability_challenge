import torch
import torch.nn as nn

__all__ = ['AttributeOperator', 'ConceptEmbedding', 'AttributeEmbeddingSpace']


class AttributeOperator(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.map = nn.Linear(input_dim, output_dim)

    def forward(self, feature: torch.Tensor):
        out = self.map(feature)
        return out


class ConceptEmbedding(nn.Module):
    def __init__(self, dim, num_attributes, attribute_id):
        super().__init__()
        self.concept_vector = nn.Parameter(torch.randn(dim), requires_grad=True)
        self.belong_vector = torch.zeros(num_attributes, requires_grad=False)
        self.belong_vector[attribute_id] = 1.0
        self.belong_vector = self.belong_vector.unsqueeze(0)


class AttributeEmbeddingSpace(nn.Module):

    def __init__(self, attribute_concept_map, input_dim, output_dim, margin=0.85, tau=0.25):
        super().__init__()
        self.all_attributes = attribute_concept_map.keys()
        self.all_concepts = []
        self.attribute_operators = nn.Module()
        self.concept_embeddings = nn.Module()
        self.attribute_concept_map = attribute_concept_map

        for (attr_id, attr) in enumerate(attribute_concept_map.keys()):
            self.attribute_operators.add_module(attr, AttributeOperator(input_dim, output_dim))
            for concept in attribute_concept_map[attr]:
                self.all_concepts.append(concept)
                self.concept_embeddings.add_module(concept,
                                                   ConceptEmbedding(output_dim, len(self.all_attributes), attr_id))

        self.margin = margin
        self.tau = tau

    """
        object_features : 2D tensor containing visual features of all objects in the scene
                    [
                        [.., .., .., ..], //obj_1 features
                        [.., .., .., ..], //obj_2 features
                        ...
                    ]
        return : 3D tensor representing the objects in all embedding space
    """
    def map_to_embeddings(self, object_features: torch.Tensor):
        all_operators = [getattr(self.attribute_operators, attr) for attr in self.all_attributes]
        object_embeddings = torch.stack([operator(object_features) for operator in all_operators], dim=-1)
        object_embeddings = object_embeddings / object_embeddings.norm(p=2, dim=-1, keepdim=True)
        return object_embeddings

    """
        object_embeddings : 3D tensor representing the objects in all embedding space
        concept : concept to filter(red, green, large ....)
        return : 1D tensor representing the probability of each object has a given concept
    """
    def similarity(self, object_embeddings: torch.Tensor, concept: str) -> torch.Tensor:
        concept_embedding = getattr(self.concept_embeddings, concept)
        concept_vector = concept_embedding.concept_vector / concept_embedding.concept_vector.norm(p=2)
        concept_vector = torch.stack([concept_vector for i in range(len(self.all_attributes))],
                                     dim=-1) # Extend dimension so it can be broadcasted
        cosine_sim = ((object_embeddings * concept_vector).sum(dim=-2) - self.margin) / self.tau

        belong_vector = concept_embedding.belong_vector.to(object_embeddings.device)
        similarity = (belong_vector * cosine_sim).sum(dim=-1)  # Remove irrelevant attribute
        logits = torch.sigmoid(similarity)
        return logits

    """
        return : 1D tensor representing the propbability of an object belonging to each concept in attribute
    """
    def get_attribute(self, object_embedding: torch.Tensor, attribute: str) -> torch.Tensor:
        all_concepts = self.attribute_concept_map[attribute]
        all_concept_pr = torch.cat([self.similarity(object_embedding.unsqueeze(0), c) for c in all_concepts])
        all_concept_pr = all_concept_pr / all_concept_pr.sum(dim=-1)
        return all_concept_pr
