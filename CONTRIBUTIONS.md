# Contribution Guidelines

Thank you for your interest in contributing to the Kubernetes Resource Scanner (KRS) tool! We welcome your contributions and are excited to help make this project better.

## Code of Conduct

Before contributing, please review and adhere to the [Code of Conduct](CODE_OF_CONDUCT.md). We expect all contributors to follow these guidelines to ensure a positive and inclusive environment.

## Release Management and Pull Request Submission Guidelines

### Repository Branch Structure

Our project employs a three-branch workflow to manage the development and release of new features and fixes:

- **main**: Stable release branch that contains production-ready code.
- **pre-release**: Staging branch for final testing before merging into main.
- **release-v0.x.x**: Active development branch where all new changes, bug fixes, and features are made and tested.

### Contributing to the Project

To contribute to our project, follow these steps to ensure your changes are properly integrated:

**Selecting the Correct Branch**

- Always base your work on the latest **release-vx.x.x** branch. This branch will be named according to the version, for example, release-v0.1.0.
- Ensure you check the branch name in the repository for the most current version branch.

**Working on Issues**

- Before you start working on an issue, comment on that issue stating that you are taking it on. This helps prevent multiple contributors from working on the same issue simultaneously.
- Include the issue number in your branch name for traceability, e.g., 123-fix-login-bug.

## **Pull Request (PR) Process**

To maintain code quality and orderly management, all contributors must follow this PR process:


### **Step 1: Sync Your Fork**

Before starting your work, sync your fork with the upstream repository to ensure you have the latest changes from the release-v0.x.x branch:
```
    git checkout release-vx.x.x
    git pull origin release-vx.x.x
```


### **Step 2: Create a New Branch**

Create a new branch from the **release-vx.x.x** branch for your work:
```
    git checkout -b your-branch-name
```


### **Step 3: Make Changes and Commit**

Make your changes locally and commit them with clear, concise commit messages. Your commits should reference the issue number:
```
    git commit -m "Fix issue #123: resolve login bug"
```


### **Step 4: Push Changes**

Push your branch and changes to your fork:

```
    git push -u origin your-branch-name
```


### **Step 5: Open a Pull Request**

- Go to the original repository on GitHub and open a pull request from your branch to the **release-vx.x.x** branch.
- Clearly describe the changes you are proposing in the PR description. Link the PR to any relevant issues.


### **Step 6: PR Review**

- All pull requests must undergo review by at least two peers before merging.
- Address any feedback and make required updates to your PR; this may involve additional commits.


### **Step 7: Final Merging**

- Once your PR is approved by the reviewers, one of the maintainers will merge it into the release-v0.x.x branch.
- The changes will eventually be merged into pre-release and then main as part of our release process.


**Notes on Contribution**

- Please make sure all tests pass before submitting a PR.
- Adhere to the coding standards and guidelines provided in our repository to ensure consistency and quality.

## Additional Resources

- [GitHub Guides: Contributing to Open Source](https://guides.github.com/activities/contributing-to-open-source/)
- [How to Contribute to an Open Source Project](https://opensource.guide/how-to-contribute/)
- [The Art of Readable Code](https://www.goodreads.com/book/show/86770.The_Art_of_Readable_Code)
