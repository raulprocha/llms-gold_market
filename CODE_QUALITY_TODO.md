# Code Quality Improvements TODO

## ✅ Completed
- [x] Added docstrings to all `__init__.py` files
- [x] Created proper package structure with `__all__` exports

## 🔄 In Progress - Language Standardization

### Files with Portuguese content to translate:

1. **pipelines/sentiment_analysis/process.py**
   - Line 19: "Pasta:" → "Directory:"
   - Line 38: "Tokenizer carregado" → "Tokenizer loaded"
   - Line 40: "Modelo carregado" → "Model loaded"
   - Line 72: "Erro na linha" → "Error at row"

2. **pipelines/model_training/model.py**
   - Line 45: Comment "nem todo modelo expõe isso" → "not all models expose this"

3. **pipelines/model_training/data.py**
   - Line 10: Comment "constrói colunas prompt/target_json" → "builds prompt/target_json columns"

4. **pipelines/headline_rewriter/process.py**
   - Line 33: "Pasta:" → "Directory:"

## 📝 Missing Documentation Standards

### Type Hints (PEP 484)
Files needing complete type hints:
- [ ] pipelines/sentiment_analysis/process.py
- [ ] pipelines/sentiment_analysis/finbert_utils.py
- [ ] pipelines/headline_rewriter/process.py
- [ ] pipelines/headline_rewriter/llm_utils.py
- [ ] pipelines/model_training/train.py
- [ ] pipelines/model_training/data.py
- [ ] pipelines/model_training/evaluate.py
- [ ] pipelines/inference/inference.py
- [ ] pipelines/inference/utils.py

### Docstrings (Google/NumPy style)
Files needing comprehensive docstrings:
- [ ] pipelines/sentiment_analysis/finbert_utils.py
- [ ] pipelines/headline_rewriter/llm_utils.py
- [ ] pipelines/model_training/train.py
- [ ] pipelines/model_training/data.py
- [ ] pipelines/model_training/prompts.py
- [ ] pipelines/inference/utils.py

### Decorator Documentation
Functions that could benefit from decorators:
- [ ] Add `@staticmethod` where appropriate
- [ ] Add `@property` for getter methods
- [ ] Add `@functools.lru_cache` for expensive computations
- [ ] Add logging decorators for debugging

## 🎯 Priority Actions

### High Priority
1. Translate all Portuguese strings to English
2. Add type hints to all function signatures
3. Add module-level docstrings to files missing them

### Medium Priority
4. Add comprehensive function docstrings (Args, Returns, Raises)
5. Add class docstrings with Attributes section
6. Document complex algorithms with inline comments

### Low Priority
7. Add decorators for better code organization
8. Add examples in docstrings for complex functions
9. Add type aliases for complex types

## 📋 Code Quality Standards

### Docstring Format (Google Style)
```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of function.
    
    Longer description if needed, explaining the purpose
    and behavior of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is not an integer
        
    Example:
        >>> function_name("test", 42)
        True
    """
    pass
```

### Type Hints Best Practices
```python
from typing import List, Dict, Optional, Union, Tuple

def process_data(
    data: List[Dict[str, Union[str, int]]],
    config: Optional[Dict[str, str]] = None
) -> Tuple[List[str], int]:
    """Process data with optional configuration."""
    pass
```

## 🔧 Automated Fixes

Run these tools to auto-fix some issues:
```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy src/ pipelines/

# Linting
pylint src/ pipelines/

# Docstring coverage
interrogate -v src/ pipelines/
```

## 📊 Current Status
- **Docstrings**: ~40% coverage
- **Type Hints**: ~60% coverage  
- **English**: ~85% (needs translation)
- **PEP 8**: ~90% compliant
