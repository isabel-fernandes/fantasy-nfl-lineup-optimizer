# Fantasy NFL Lineup Optimizer

This project provides optimized fantasty football lineups for Daily Fantasy Sports (DFS) Leagues such as Draft Kings or Fan Duel. Historical data is pulled from fantasydata.com to train a weekly fantasy projection model. These projections along with historical DFS salaries and scores are used to determine an optimal lineup of players for the coming week of NFL games. This information is then displayed via dashboard.

## Project Components

- Data Scraper
- Exploratory Analysis
- Projection Model
- Lineup Optimizer
- Display Dashboard

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

## Data Scraper

### Sources
- https://fantasydata.com/nfl/fantasy-football-leaders
- http://rotoguru1.com/cgi-bin/fyday.pl

### FanDuel Salaries
Found a existing project with a scraper for pulling weekly salary data (https://github.com/rjh336/ffb_metis) <br>
Sample: `data/fanduel_salaries/fd_salaries_2019.csv`
- Note that this sample csv does not exactly match with the definitions outlined in the variable definitions table below. Please follow the variable definitions when preparing the actual webscraper outputs.

#### Variable Definitions
| Parameter             | Descriptionn                  | Data Type | Notes              |
|-----------------------|-------------------------------|-----------|--------------------|
| Week                  | Week of season.               | Int       | 1-17               |
| Year                  | Starting year of the season   | Int       |                    |
| Name                  | First and Last name of player | String    | "Patrick Mahomes"  |
| Team                  | Team abbreviation             | String    | GB, CAR, NYG, ...  |
| Pos                   | Position of Player            | String    | QB, RB, WR, TE     |
| Opp                   | Opponent team's abbreviation  | String    | GB, CAR, NYG, ...  |
| fd_points             | FanDuel points scored         | Float     |                    |
| fg_salary             | FanDuel salary                | Int       |                    |

### Weekly Player Stat Requirements
If a stat (such as passing stats) is not applicable to a particular player, then the value will be 0, not empty. <br>
Sample: `data/weekly_players/sample_weekly.csv`
- Note that this sample csv does not exacly match with the definitions outlined in the variable definitions table below. Please follow the variable definitions when preparing the actual web-scraper outputs.

#### Variable Definitions
| Parameter             | Descriptionn                  | Data Type | Notes              |
|-----------------------|-------------------------------|-----------|--------------------|
| Name                  | First and Last name of player | String    | "Patrick Mahomes"  |
| Team                  | Team abbreviation             | String    | GB, CAR, NYG, ...  |
| Pos                   | Position of Player            | String    | QB, RB, WR, TE     |
| Wk                    | Week of season                | Int       | 1-17               |
| Opp                   | Opponent team's abbreviation  | String    | GB, CAR, NYG, ...  |
| Year                  | Starting year of the season   | Int       |                    |
| Status                | Injury Status of Player       | String    | Q, O, IR, ,<-n/a   |
| TeamScore             | Player's team's score in game | Int       |                    |
| OppScore              | Opponent team's score in game | Int       |                    |
| PassingYds            | Passing yards                 | Int       |                    |
| PassingTD             | Passing touchdowns            | Int       |                    |
| Int                   | Interceptions                 | Int       |                    |
| PassingAtt            | Passing Attempts              | Int       |                    |
| Cmp                   | Completions                   | Int       |                    |
| RushingAtt            | Rushing attempts              | Int       |                    |
| RushingYds            | Rushing yards                 | Int       |                    |
| RushingTD             | Rushing touchdowns            | Int       |                    |
| Rec                   | Receptions                    | Int       |                    |
| Tgt                   | Targets                       | Int       |                    |
| ReceivingYds          | Receiving yards               | Int       |                    |
| ReceivingTD           | Receiving touchdowns          | Int       |                    |
| FL                    | Fumbles                       | Int       |                    |

## Exploratory Analysis
- Generate and explore features that are correlated with fantasy score
- Generate a weekly predictive model of score for each postion. Let's do a combined model for QB, RB, WR

## Projection model

## Lineup Optimizer

## Display dashboard
