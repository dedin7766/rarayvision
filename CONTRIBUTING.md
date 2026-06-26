# Contributing to Raray Vision

Thank you for your interest in contributing to Raray Vision! We welcome contributions from developers of all skill levels. Whether it's fixing a bug, adding a feature, improving documentation, or suggesting ideas — every contribution matters.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Branch Naming Convention](#branch-naming-convention)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)
- [Community](#community)

---

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. Be kind, constructive, and professional in all interactions.

---

## How Can I Contribute?

| Type | Description |
|---|---|
| 🐛 **Bug Fix** | Found a bug? Fix it and submit a PR |
| ✨ **New Feature** | Have an idea? Propose it via an Issue first |
| 📖 **Documentation** | Improve README, API docs, or code comments |
| 🧪 **Testing** | Add unit tests or integration tests |
| 🎨 **UI/UX** | Improve the frontend design or user experience |
| 🔧 **Refactor** | Clean up code, improve performance, reduce tech debt |
| 🌐 **Translation** | Help translate the UI or docs to other languages |

---

## Getting Started

### 1. Fork the Repository

Click the **Fork** button on the top right of the [Raray Vision repository](https://github.com/dedin7766/rarayvision) to create your own copy.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR-USERNAME/rarayvision.git
cd rarayvision
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/dedin7766/rarayvision.git
```

### 4. Create a New Branch

```bash
git checkout -b feature/your-feature-name
```

---

## Development Setup

### Backend (Python / FastAPI)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run the backend
uvicorn backend.main:app --host 0.0.0.0 --port 5000 --reload
```

### Frontend (Vue 3 / Vite)

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server runs on `http://localhost:5173` and proxies API requests to the backend on port 5000.

### Database

Make sure you have MySQL or MariaDB running with the database configured:

```sql
CREATE DATABASE rarayvision CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'raray'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON rarayvision.* TO 'raray'@'localhost';
FLUSH PRIVILEGES;
```

---

## Branch Naming Convention

Use descriptive branch names with the following prefixes:

| Prefix | Usage | Example |
|---|---|---|
| `feature/` | New feature | `feature/face-grouping` |
| `fix/` | Bug fix | `fix/liveness-camera-error` |
| `docs/` | Documentation | `docs/update-api-guide` |
| `refactor/` | Code refactoring | `refactor/optimize-embedding` |
| `test/` | Adding tests | `test/auth-unit-tests` |
| `chore/` | Maintenance tasks | `chore/update-dependencies` |

---

## Commit Message Guidelines

Write clear and meaningful commit messages:

```
<type>: <short description>

[optional body with more details]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance, dependency updates

### Examples

```
feat: add face grouping endpoint
fix: resolve liveness detection timeout on low-light cameras
docs: update API authentication section in README
refactor: optimize cosine similarity calculation
```

---

## Pull Request Process

1. **Sync with upstream** before submitting:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Open a Pull Request** on GitHub:
   - Go to the original repo: https://github.com/dedin7766/rarayvision
   - Click **"Compare & pull request"**
   - Fill in the PR template

4. **PR Requirements**:
   - Provide a clear title and description
   - Reference related Issues (e.g., `Closes #12`)
   - Make sure the code builds without errors
   - Add screenshots for UI changes
   - Keep changes focused — one feature/fix per PR

5. **Code Review**:
   - The maintainer will review your PR
   - You may be asked to make changes
   - Once approved, your PR will be merged 🎉

---

## Coding Standards

### Python (Backend)

- Follow **PEP 8** style guidelines
- Use **type hints** where possible
- Keep functions small and focused
- Add docstrings for public functions
- Use meaningful variable and function names

```python
# ✅ Good
def calculate_similarity(embedding_a: np.ndarray, embedding_b: np.ndarray) -> float:
    """Calculate cosine similarity between two face embeddings."""
    return np.dot(embedding_a, embedding_b) / (np.linalg.norm(embedding_a) * np.linalg.norm(embedding_b))

# ❌ Bad
def calc(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

### JavaScript / Vue (Frontend)

- Use **Vue 3 Composition API** (`<script setup>`)
- Use **camelCase** for variables and functions
- Use **PascalCase** for component names
- Keep components focused and reusable

---

## Reporting Bugs

Found a bug? Please open an [Issue](https://github.com/dedin7766/rarayvision/issues/new) with:

- **Title**: Clear and concise bug description
- **Environment**: OS, Python version, browser, etc.
- **Steps to Reproduce**: Step-by-step instructions
- **Expected Behavior**: What should have happened
- **Actual Behavior**: What actually happened
- **Screenshots / Logs**: If applicable

### Bug Report Template

```markdown
**Bug Description**
A clear description of what the bug is.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: Ubuntu 22.04
- Python: 3.11
- Browser: Chrome 120
```

---

## Requesting Features

Have an idea? Open an [Issue](https://github.com/dedin7766/rarayvision/issues/new) with:

- **Title**: Short description of the feature
- **Problem**: What problem does this solve?
- **Proposed Solution**: How would you implement it?
- **Alternatives**: Any alternative approaches considered?

> **Important**: For major features, please open an Issue first to discuss the approach before writing code. This helps avoid wasted effort.

---

## Community

- 💬 **WhatsApp**: [Chat with Dedin](https://wa.me/6282299331066)
- 📧 **Email**: dedintoyibah70@gmail.com
- ☕ **Support**: [Trakteer](https://trakteer.id/dedin_toyibah)
- 🌐 **Live Demo**: [rarayvision.dfs.co.id](https://rarayvision.dfs.co.id)

---

## Thank You! 🙏

Every contribution, no matter how small, helps make Raray Vision better. We appreciate your time and effort in improving this project. Together, we can build the best open-source face recognition platform!
