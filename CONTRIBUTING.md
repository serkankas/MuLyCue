# Contributing to MuLyCue

Thank you for your interest in contributing to MuLyCue! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect different viewpoints and experiences

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/MuLyCue/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Screenshots if applicable

### Suggesting Features

1. Check [Discussions](https://github.com/yourusername/MuLyCue/discussions) for similar ideas
2. Create a new discussion or issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the code style guidelines
   - Add tests for new features
   - Update documentation

4. **Test your changes**
   ```bash
   pytest
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add: brief description of changes"
   ```
   
   Commit message format:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for updates to existing features
   - `Refactor:` for code refactoring
   - `Docs:` for documentation changes

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide clear description of changes
   - Reference related issues
   - Include screenshots for UI changes

## Development Setup

1. Clone your fork:
```bash
git clone https://github.com/yourusername/MuLyCue.git
cd MuLyCue
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run tests:
```bash
pytest
```

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Add docstrings to all functions and classes
- Maximum line length: 100 characters

Example:
```python
def transpose_chord(chord_str: str, semitones: int, prefer_sharp: bool = True) -> Optional[str]:
    """
    Transpose a chord string by semitones.
    
    Args:
        chord_str: Chord string (e.g., "Am7", "Fmaj7")
        semitones: Number of semitones to transpose
        prefer_sharp: Use sharp notation if True, flat if False
        
    Returns:
        Transposed chord string or None if parsing fails
    """
    # Implementation here
```

### JavaScript
- Use ES6+ features
- Use meaningful variable names
- Add JSDoc comments for functions
- Use `const` and `let`, avoid `var`

Example:
```javascript
/**
 * Transpose a chord by semitones
 * @param {string} chord - Chord string
 * @param {number} semitones - Number of semitones
 * @returns {string} Transposed chord
 */
function transposeChord(chord, semitones) {
    // Implementation here
}
```

### CSS
- Use CSS variables for colors and spacing
- Follow BEM naming convention for classes
- Mobile-first responsive design

## Testing

- Write tests for all new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

Run tests:
```bash
# All tests
pytest

# Specific test file
pytest tests/test_chord.py

# With coverage
pytest --cov=src tests/
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all Python functions
- Update API documentation for endpoint changes
- Include code examples where helpful

## Questions?

Feel free to ask questions in:
- [GitHub Discussions](https://github.com/yourusername/MuLyCue/discussions)
- [Issues](https://github.com/yourusername/MuLyCue/issues)

Thank you for contributing to MuLyCue! 🎵

