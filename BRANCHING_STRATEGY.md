# Branching Strategy

This project follows a **Feature Branch Workflow**.

## Branches

### `main`
-   **Purpose**: The source of truth. Contains production-ready code.
-   **Protection**: Direct commits are discouraged; changes should come via merges from feature branches.

### `feature/*`
-   **Purpose**: Developing new features or enhancements.
-   **Naming Convention**: `feature/short-description` (e.g., `feature/user-auth`, `feature/pdf-export`).
-   **Source**: Branch off `main`.
-   **Merge**: Merge back into `main` upon completion and verification.

### `bugfix/*`
-   **Purpose**: Fixing bugs found during development or testing.
-   **Naming Convention**: `bugfix/short-description` (e.g., `bugfix/fetch-timeout`).
-   **Source**: Branch off `main` (or the relevant feature branch).
-   **Merge**: Merge back into `main` (or the relevant feature branch).

### `hotfix/*`
-   **Purpose**: Critical fixes for issues in production (`main`).
-   **Naming Convention**: `hotfix/short-description`.
-   **Source**: Branch off `main`.
-   **Merge**: Merge back into `main` immediately.

## Workflow

1.  **Start**: Create a new branch from `main`:
    ```bash
    git checkout main
    git pull
    git checkout -b feature/my-new-feature
    ```
2.  **Work**: Make changes and commit frequently.
3.  **Verify**: Run tests and verify functionality.
4.  **Merge**: Switch to `main` and merge the feature branch:
    ```bash
    git checkout main
    git merge feature/my-new-feature
    ```
5.  **Cleanup**: Delete the feature branch (optional but recommended):
    ```bash
    git branch -d feature/my-new-feature
    ```
