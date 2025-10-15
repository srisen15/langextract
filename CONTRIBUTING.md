# Contributing to Enterprise Test Analyzer

Thank you for your interest in contributing to the Enterprise Test Analyzer! This guide will help you get started.

## 🚀 Quick Start for Contributors

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/enterprise-test-analyzer.git
   cd enterprise-test-analyzer
   ```

2. **Set Up Development Environment**
   ```bash
   # Run setup script
   .\scripts\setup.ps1
   
   # Or manual setup
   python -m venv test_analysis_env
   test_analysis_env\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 Python style guide
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Maximum line length: 100 characters

### Testing
- Write tests for new features
- Ensure existing tests pass
- Test with real Playwright log files
- Include edge cases

### Documentation
- Update README.md if adding new features
- Add docstrings to new functions
- Update configuration examples

## 🐛 Reporting Issues

When reporting issues, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Sample test log files (if relevant)

## 💡 Feature Requests

We welcome feature requests! Please:
- Check existing issues first
- Describe the use case
- Explain the benefits
- Provide implementation ideas if possible

## 🔧 Areas for Contribution

### High Priority
- Additional CI/CD platform integrations
- Enhanced failure pattern recognition
- Performance optimizations for large datasets
- Mobile app notification support

### Medium Priority
- Additional report formats (PowerBI, Tableau)
- Machine learning for failure prediction
- Integration with test management tools
- Advanced visualization dashboards

### Documentation
- More usage examples
- Video tutorials
- Best practices guide
- Troubleshooting documentation

## 📝 Pull Request Process

1. **Before Submitting**
   - Ensure your code follows the style guidelines
   - Add/update tests as needed
   - Update documentation
   - Test thoroughly

2. **Pull Request Template**
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Tests pass locally
   - [ ] Added new tests
   - [ ] Tested with real data

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   ```

3. **Review Process**
   - Maintainers will review within 48 hours
   - Address feedback promptly
   - Squash commits before merging

## 🏗️ Project Structure

```
src/
├── core/                    # Core analysis engine
├── integrations/            # External integrations
├── utils/                   # Utility functions
config/                      # Configuration files
scripts/                     # Setup and execution scripts
docs/                        # Documentation
tests/                       # Test files
```

## 💬 Communication

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Email**: For security issues

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub releases

Thank you for contributing! 🎉