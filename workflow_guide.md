# Git Workflow Guidelines

## Getting Started
- Install Anaconda: https://docs.anaconda.com/anaconda/install/
- Install git
- Clone repo: `git clone https://github.com/cshono/fantasy-nfl-lineup-optimizer`
- Set up env: `conda env create --file environment.yml`
- Activate to env: `conda activate dfs`
- Fetch all remote branches: `git fetch origin`

### Git Workflow
- Switch to your personal dev branch: `git checkout corey-dev`
- Create some new files...
- Stage changes: `git add .`
- Commit changes to your local dev: `git commit -m "created some new files for new feature"`
- Edit those file to complete feature...
- Stage changes: `git add .`
- Commit changes to local dev: `git commit -m "completed new feature"`
- Merge changes to master:
    - Switch to master: `git checkout master`
    - Pull current version of master from remote: `git pull`
    - Switch back to dev branch: `git checkout corey-dev`
    - Merge dev branch with master: `git merge master`
    - If there is merge conflict:
        - Resolve conflicts
        - `git add .` `git commit` `[esc]:wq`
- Push merged dev branch to remote dev: `git push origin corey-dev`
- Navigate to remote dev branch on GitHub repo
- Create a pull request. Tag others to review pull requests. ESPECIALLY if you
are not the owner of the project directory where modifications are being made.
- Message relevant collabroator to review and "merge pull request" when changes
are approved.

### Pull Request Guidelines
- Always use your personal dev branch or a new feature branch when working on new/updating code
- Do not push changes to `remote/master` or `remote/<other person's-dev>`
- Create pull requests to merge new features with `remote/master`. Include the
project component owner for pull request approval. Not a bad idea to tag someone else
in pull requests where you are the owner of the updates, just for a second pair of eyes.
    - `scraper/`: Oscar
    - `projection_model/`: Corey
    - `lineup_optimizer/`: Corey
    - `dashboard/`: Isabel
    - `data/`: Tag the whole team, do not approve your own pull request
    - `meta_data/`: Tag the whole team, do not approve your own pull request

### .gitignore
Git is primarily used to track changes to actual code. Not data, or visualizations.
Include these files in the .gitignore file. It is o.k. to keep small data or meta
data files in the git repo.
