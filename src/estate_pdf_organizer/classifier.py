"""Document classification module for the Estate PDF Organizer."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import yaml

@dataclass
class Classification:
    """Represents a document classification result."""
    category: str
    filename: str
    confidence: float

class DocumentClassifier(ABC):
    """Abstract base class for document classifiers."""
    
    @abstractmethod
    def classify(self, text: str) -> Classification:
        """Classify a document based on its text content.
        
        Args:
            text: The text content of the document
            
        Returns:
            Classification object containing the category, suggested filename, and confidence
        """
        pass

class LLMClassifier(DocumentClassifier):
    """Document classifier using an LLM."""
    
    def __init__(self, taxonomy_path: Path):
        """Initialize the LLM classifier.
        
        Args:
            taxonomy_path: Path to the YAML file containing the taxonomy
            
        Raises:
            FileNotFoundError: If the taxonomy file doesn't exist
            ValueError: If the taxonomy file has an invalid structure
        """
        if not taxonomy_path.exists():
            raise FileNotFoundError(f"Taxonomy file not found: {taxonomy_path}")
            
        try:
            with open(taxonomy_path) as f:
                taxonomy = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in taxonomy file: {str(e)}")
            
        if not isinstance(taxonomy, dict):
            raise ValueError("Taxonomy file must contain a dictionary")
            
        if 'categories' not in taxonomy:
            raise ValueError("Taxonomy file must contain a 'categories' key")
            
        if not isinstance(taxonomy['categories'], list):
            raise ValueError("'categories' must be a list")
            
        if not taxonomy['categories']:
            raise ValueError("'categories' list cannot be empty")
            
        for category in taxonomy['categories']:
            if not isinstance(category, str):
                raise ValueError("All categories must be strings")
                
        self.categories = taxonomy['categories']
        
        # TODO: Initialize LangChain with appropriate model
        # For now, just store the categories
        self._categories = self.categories

    def classify(self, text: str) -> Classification:
        """Classify a document using the LLM.
        
        Args:
            text: The text content of the document
            
        Returns:
            Classification object containing the category, suggested filename, and confidence
            
        Raises:
            ValueError: If the text is empty
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
            
        # TODO: Implement actual classification using LangChain
        # For now, just return a dummy classification
        return Classification(
            category="Unorganized",
            filename="document.pdf",
            confidence=1.0
        ) 