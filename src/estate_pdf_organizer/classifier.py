"""Document classification module for the Estate PDF Organizer."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


@dataclass
class ClassificationResult:
    """Result of document classification."""
    
    def __init__(
        self,
        document_type: str,
        confidence: float,
        page_start: int,
        page_end: int,
        suggested_filename: str | None = None
    ):
        self.document_type = document_type
        self.confidence = confidence
        self.page_start = page_start
        self.page_end = page_end
        self.suggested_filename = suggested_filename
        
        if not 0 <= confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")

class DocumentClassifier(ABC):
    """Abstract base class for document classifiers."""
    
    @abstractmethod
    def classify(self, text: str) -> list[ClassificationResult]:
        """Classify a document based on its text content.
        
        Args:
            text: The text content of the document
            
        Returns:
            Classification object containing the category, suggested filename, and confidence
        """
        pass

class LLMClassifier:
    """Document classifier using an LLM."""
    
    def __init__(self, taxonomy_path: Path, api_key: str | None = None):
        """Initialize the classifier.
        
        Args:
            taxonomy_path: Path to YAML file containing document taxonomy
            api_key: OpenAI API key. If None, will use OPENAI_API_KEY environment variable.
        """
        # Load taxonomy
        with open(taxonomy_path) as f:
            taxonomy = yaml.safe_load(f)
        
        if not isinstance(taxonomy, dict) or "categories" not in taxonomy:
            raise ValueError("Taxonomy must contain categories")
        
        if not isinstance(taxonomy["categories"], list):
            raise ValueError("categories must be a list")
        
        self.categories = taxonomy["categories"]
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0,
            api_key=api_key
        )
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a document classification assistant. Your task is to analyze text 
             from a number of documents which have been scanned together and determine:
1. The boundaries of the document(s) you find
2. What type of document each is
3. How confident you are in your classification (0-1)
4. A suggested filename for the document(s)

Available document types:
{categories}

Respond with a JSON array. Each array element should be an object with:
- document_type: The type of document (must be one of the available types)
- confidence: A number between 0 and 1 indicating your confidence in the classification
- page_start: The page number where the document starts
- page_end: The page number where the document ends
- suggested_filename: A suggested filename for the document. 
             Please add the most relevant date if you find one

Example response:
[
{{
    "document_type": "Will",
    "confidence": 0.95,
    "page_start": 5,
    "page_end": 6,
    "suggested_filename": "will_glenn_meacham.pdf"
}}]"""),
            ("user", "Text to analyze:\n{text}")
        ])
        
        # Initialize output parser
        self.parser = JsonOutputParser()
    
    def classify(self, text: str) -> list[ClassificationResult]:
        """Classify a document.
        
        Args:
            text: Text to classify
            
        Returns:
            ClassificationResult object
            
        Raises:
            ValueError: If the text is empty or the LLM response is invalid
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Format prompt
        formatted_prompt = self.prompt.format_messages(
            categories="\n".join(f"- {cat}" for cat in self.categories),
            text=text
        )
        
        # Get response from LLM
        response = self.llm.invoke(formatted_prompt)
        
        try:
            result = json.loads(response.content.replace('```json', '').replace('```', ''))

            classification_results = []
            for r in result:
                if r["document_type"] not in self.categories:
                    raise ValueError(f"Invalid document type: {r['document_type']}")

                classification_results.append(ClassificationResult(
                    document_type=r["document_type"],
                    confidence=float(r["confidence"]),
                    page_start=r["page_start"],
                    page_end=r["page_end"],
                    suggested_filename=r.get("suggested_filename")
                ))
            return classification_results
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from LLM: {e}") from e
        except KeyError as e:
            raise ValueError(f"Missing required field in LLM response: {e}") from e
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid confidence value in LLM response: {e}") from e
