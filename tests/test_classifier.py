"""Tests for the classifier module."""

from pathlib import Path
import tempfile
import yaml
from estate_pdf_organizer.classifier import LLMClassifier, Classification

def test_classification():
    """Test Classification dataclass."""
    classification = Classification(
        category="Important Documents",
        filename="will.pdf",
        confidence=0.95
    )
    assert classification.category == "Important Documents"
    assert classification.filename == "will.pdf"
    assert classification.confidence == 0.95

def test_llm_classifier_initialization():
    """Test LLMClassifier initialization."""
    # Create a temporary taxonomy file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
        taxonomy = {
            'categories': [
                'Important Documents',
                'Financial',
                'Property',
                'Unorganized'
            ]
        }
        yaml.dump(taxonomy, f)
        f.flush()
        
        classifier = LLMClassifier(Path(f.name))
        assert classifier.categories == taxonomy['categories']

def test_llm_classifier_classify():
    """Test document classification."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
        taxonomy = {
            'categories': [
                'Important Documents',
                'Financial',
                'Property',
                'Unorganized'
            ]
        }
        yaml.dump(taxonomy, f)
        f.flush()
        
        classifier = LLMClassifier(Path(f.name))
        classification = classifier.classify("This is a test document")
        
        assert isinstance(classification, Classification)
        assert classification.category in taxonomy['categories']
        assert isinstance(classification.filename, str)
        assert 0 <= classification.confidence <= 1 