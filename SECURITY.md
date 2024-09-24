# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability within the project, we encourage responsible disclosure to protect our users. Please follow the guidelines below:

1. **Report privately**: Do not create a public GitHub issue. Instead, report the vulnerability by emailing [Security](mailto:dr3394@nyu.edu,jjl9839@nyu.edu).
2. **Provide details**: Include a clear and concise description of the vulnerability, the steps required to reproduce it, and the potential impact.
3. **Wait for response**: We will acknowledge your report within 48 hours and aim to provide a resolution within 7 days.

## Security Practices

This repository follows the best security practices outlined below:

1. ✔ **GitHub Security Configuration**: 
   - All roles and permissions are based on the Principle of Least Privilege. Teams are assigned the minimal access necessary to perform their tasks.  
   - Refer to [GitHub Docs on Managing Teams](https://docs.github.com/en/organizations/managing-peoples-access-to-your-organization-with-roles/managing-team-access-to-an-organization-repository).
   - Removed owner/admin access for engineering, and granted write access to engineering

2. ✔ **Two-factor Authentication (2FA)**:
   - 2FA is required for all contributors to secure GitHub accounts.  
   - Reference: [Secure your GitHub Organization with 2FA](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/about-two-factor-authentication).
   - Enforced 2FA in the GitHub organization

3. ❌ **Secure Version Control Practices**:
   - No sensitive information such as API keys, passwords, or environment variables should be committed to the repository.
   - Use `.gitignore` to prevent committing sensitive files.
   - Refer to [Best Practices for Secrets Management](https://docs.github.com/en/actions/security-guides/encrypted-secrets).

4. ✔ **SSH for Authentication**:
   - Use SSH keys for secure access to the repository instead of HTTPS.
   - Reference: [GitHub Docs on SSH Key Generation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).

5. ✔ **Branch Protection Rules**:
   - We enforce branch protection rules, including code review before merging.  
   - Reference: [GitHub Docs on Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/about-branch-protection).
   - Created a develop branch so that code in development can be pushed there as needed

6. ✔ **Signed Commits**:
   - All commits must be signed to verify their authenticity and integrity.  
   - Reference: [GitHub Docs on Signing Commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits).
   - Created a branch rule that requires signed commits for all branches

7. ✔ **Static Code Analysis**:
   - We use tools like Black, Ruff, and Flake8 to maintain code quality and catch syntax errors.
   - Reference: [Using Python Linters](https://black.readthedocs.io/en/stable/).

8. ✔ **Secret Scanning**:
   - We have enabled GitHub’s Secret Scanning feature to detect if sensitive information gets committed.
   - Reference: [GitHub Docs on Secret Scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning).

9. ✔ **Container Security**:
   - We follow Docker security best practices as relevant to our project, ensuring that containers run with the least privileges necessary.  
   - Reference: [Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html).

10. ✔ **Testing**:
   - Unit and integration tests are encouraged to improve security and functionality.
   - We use GitHub Codespaces for consistent development environments.

For more details on secure coding practices, please refer to the [OWASP Developer Guide](https://owasp.org/www-project-top-ten/).

