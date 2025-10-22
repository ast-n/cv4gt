Contributing
============

We welcome contributions to CV4GT! This document provides guidelines for contributing to the project.

Getting Started
---------------

1. **Fork** the repository
2. **Clone** your fork:

   .. code-block:: bash

      git clone https://github.com/your-username/cv4gt.git
      cd cv4gt

3. **Create** a branch:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

4. **Make** your changes
5. **Test** thoroughly
6. **Submit** a pull request

Development Setup
-----------------

Follow the installation instructions in :doc:`getting_started`, then:

.. code-block:: bash

   # Install development dependencies
   pip install -r requirements.txt
   pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

Code Style
----------

Python
~~~~~~

- Follow PEP 8 style guide
- Use Google-style docstrings
- Type hints are encouraged
- Maximum line length: 100 characters

.. code-block:: python

   def example_function(param1: str, param2: int) -> bool:
       """Short description.

       Longer description if needed.

       Args:
           param1 (str): Description of param1.
           param2 (int): Description of param2.

       Returns:
           bool: Description of return value.
       """
       return True

JavaScript/Vue
~~~~~~~~~~~~~~

- Use ES6+ syntax
- Follow Vue 3 composition API patterns
- Use Tailwind CSS for styling

Documentation
~~~~~~~~~~~~~

- Update docstrings for any modified functions/classes
- Add/update relevant ``.rst`` files in ``docs/``
- Build and verify documentation:

  .. code-block:: bash

     cd docs
     make html

Testing
-------

Before submitting:

1. **Test** with video file input
2. **Test** with RealSense camera (if available)
3. **Verify** frontend displays correctly
4. **Check** for console errors
5. **Build** documentation without errors

Pull Request Process
--------------------

1. **Update** documentation for any new features
2. **Ensure** your code follows the style guide
3. **Write** a clear PR description:

   - What does this change?
   - Why is it needed?
   - How was it tested?

4. **Reference** related issues (e.g., "Fixes #123")
5. **Wait** for review and address feedback

Areas for Contribution
----------------------

High Priority
~~~~~~~~~~~~~

- GPS integration (currently placeholder)
- Additional object classes
- Performance optimizations
- Cross-platform testing

Medium Priority
~~~~~~~~~~~~~~~

- Unit tests for core modules
- CI/CD pipeline
- Docker containerization
- Additional camera support

Documentation
~~~~~~~~~~~~~

- Usage examples
- Video tutorials
- API endpoint documentation
- Troubleshooting guides

Reporting Issues
----------------

When reporting issues, include:

- **OS and version**
- **Python version**
- **GPU/CUDA version** (if using GPU)
- **Error messages** (full traceback)
- **Steps to reproduce**
- **config.ini** settings (redact sensitive info)

Code of Conduct
---------------

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help newcomers learn

License
-------

By contributing, you agree that your contributions will be licensed under the project's license.

Contact
-------

- **GitHub Issues**: https://github.com/ast-n/cv4gt/issues
- **Email**: [Contact team members]
