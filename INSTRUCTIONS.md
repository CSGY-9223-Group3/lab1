# Lab One Instructions: Source

## Objective
In this lab, each group will be required to create a public Open Source Software (OSS) GitHub repository for an app written in Python using the Flask web application framework. The app will be an internal Pastebin, and students must implement secure software development practices.

## Web App Details: Internal Pastebin

### Features:
- **Authentication**: Users must authenticate with secret API keys using bearer tokens. More advanced authentication is optional.
- **API Functionality**:
  - **Create new notes**: Users should be able to create new notes. Each note has exactly one author who should be publicly attributed. A note may be either private or public.
  - **User Registration**: Set up a registration flow to assign specific API keys based on user. No need for integrating with a public identity provider.
  - **Read old notes**: Users should be able to read all public notes from all users as well as their own private notes.
  - **Update old notes**: Authors can overwrite their own notes.
  - **Delete old notes**: Authors can delete their old notes.
- **Web UI (optional)**: Only JSON API endpoints for the operations above are required.
- **Container-Based Development**: The app will be containerized for deployment using Docker. Use a Python base image with the Flask application to expose the service.
- **Persistent Storage (optional)**: The application’s storage may be ephemeral, meaning notes may be deleted when the container stops.

## Task: Introduce and Fix Vulnerabilities
The engineering team is tasked with "accidentally" introducing at least one vulnerability in the code. The security team will then review the code, identify these vulnerabilities, and raise GitHub issues detailing the vulnerabilities along with remediation steps to fix them, following OWASP Top 10.

### Engineering Team's Responsibilities:
- Design and implement the required features.
- Introduce vulnerabilities such as insecure API endpoints, improper input validation, or insecure handling of sensitive data.
- Ensure the vulnerabilities are subtle and realistic.

### Security Team's Responsibilities:
- Inspect the GitHub organization and repository security settings to make sure that the best security practices are being followed.
- Perform a thorough code review and optionally use automated tools to aid in finding vulnerabilities.
- Raise GitHub issues that clearly explain the vulnerability, why it exists, the potential impact, and include proposed remediation steps.

## Security Practices
Students are required to satisfy at least 10 out of the following security practices as part of the lab. These are derived from best practices discussed in Weeks 2-4 of lectures. Points marked with advanced or optional may or may not be included.

### GitHub Security Configuration
- Ensure that roles and permissions are properly set up in the GitHub repository, and configure teams with minimal access rights required to perform their tasks. Principle of Least Privilege.  
**Reference**: [GitHub Docs on Managing Teams](https://docs.github.com/en/organizations/managing-peoples-access-to-your-organization-with-roles/managing-team-access-to-an-organization-repository).

### Two-factor Authentication (2FA)
- Enforce 2FA for all GitHub users to secure account access.  
**Reference**: [Secure your GitHub Organization with 2FA](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/about-two-factor-authentication).

### Secure Version Control Practices
- Sensitive data such as API keys or environment variables should not be committed to the repository. Use `.gitignore` and environment files. Feature branches, etc.

### SSH for Authentication
- Use SSH keys instead of HTTPS to securely clone, push, and pull changes to the Git repository.  
**Reference**: [GitHub Docs on SSH Key Generation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).

### Branch Protection Rules
- Implement branch protection rules, including requiring at least one code review before merging to the main branch.  
**Reference**: [GitHub Docs on Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/about-branch-restrictions).

### Signed Commits
- Use Git commit signing to verify the authenticity and integrity of each commit.  
  **[Advanced]** Use tools like `gitsign`.

### Static Code Analysis
- Use linters like Black, Ruff, Flake8 for Python to maintain code quality and catch syntax errors early.

### Secret Scanning
- Enable GitHub's secret scanning feature to detect if sensitive information (like API keys) gets committed to the repository.  
**Reference**: [GitHub Docs on Secret Scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning).

### Proper Documentation (Markdown format preferred for all docs):
- **CONTRIBUTING.md**: Include guidelines for contributors on best practices for contributing securely to the project.  
**Reference**: [GitHub Docs on Creating a Contributing Guide](https://docs.github.com/en/get-started/quickstart/github-flow).
- **SECURITY.md**: Add a security policy document that outlines how to report vulnerabilities and security issues.  
**Reference**: [Creating a Security Policy on GitHub](https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository).
- **LICENSE**: Include an open-source license for the project.

### Container Security
- Follow Docker security best practices by referring to the Docker Security Cheat Sheet. This includes ensuring that containers are run with the least privileges necessary.  
**Reference**: [Docker Security Documentation](https://docs.docker.com/engine/security/).

### Test Cases (optional)
- Write both unit and integration tests for the Pastebin app. Bonus points will be awarded for good test coverage and quality.

### GitHub Codespaces
- Use remote workspaces instead of a local one.

## Important Resources
There is a lot of documentation online. Try to use documentation from GitHub, OWASP, and official sources.

- **Development**: [OWASP Developer Guide](https://owasp.org/www-project-top-ten/OWASP-Top-10-2017_Development.html)
- **Flask Documentation**: [Flask Web Framework](https://flask.palletsprojects.com/)
- **GitHub Security Overview**: [GitHub Docs on Security](https://docs.github.com/en/code-security)

## Additional Notes
- **GitHub Copilot**: Students are allowed and encouraged to use GitHub Copilot to assist in writing secure code.  
  **Reference**: [Getting free access to Copilot as a student](https://docs.github.com/en/copilot/getting-started-with-github-copilot/getting-started-with-github-copilot).

## Evaluation Criteria
Students will be evaluated on the following:
1. **Correctness and Functionality**: Is the Pastebin app functioning as specified?
2. **Security Best Practices**: Have at least 10 of the security practices listed above been implemented?
3. **Vulnerability Detection**: Has the security team successfully identified and raised issues for the vulnerabilities introduced by the engineering team, with proper remediation steps?
