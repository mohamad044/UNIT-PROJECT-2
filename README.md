# UNIT-PROJECT-2
----------------------------------------------------------
# user stories
User Stories for Football Application
User Authentication & Profile Management

As a user, I want to register for an account so that I can personalize my football tracking experience.
As a user, I want to log in to access my personalized dashboard and preferences.
As a user, I want to log out to secure my account when I'm done using the application.
As a user, I want to select my favorite teams and competitions so that I can see content relevant to my interests.

Home Page & Navigation

As a user, I want to see today's matches on the home page so that I can quickly find games happening now.
As a user, I want to see a list of upcoming matches for my favorite teams so I can plan when to watch them.
As a user, I want to see live scores of ongoing matches so I can stay updated without watching the game.
As a user, I want to toggle between viewing all matches and only matches from my favorite teams/competitions.

Match Details

As a user, I want to view detailed information about a specific match so I can get in-depth insights.
As a user, I want to see key events (goals, cards) in a match so I understand what happened in the game.
As a user, I want to view team lineups for matches so I know which players are participating.
As a user, I want to bookmark matches of interest so I can easily find them later.

Competition Features

As a user, I want to browse all available competitions so I can explore beyond my favorites.
As a user, I want to see league tables so I can check team standings in the competition.
As a user, I want to view match schedules for specific competitions so I can follow tournaments.
As a user, I want to see tournament knockout stages for cup competitions.

Team Features

As a user, I want to view team profiles so I can learn more about a specific team.
As a user, I want to see a team's upcoming fixtures so I know when they play next.
As a user, I want to view a team's recent results to track their performance.
As a user, I want to see which competitions a team participates in.


-----------------------------------------------------------
# UML 
+--------------------+       +--------------------+       +--------------------+
|       User         |       |    UserProfile     |       |    Competition     |
+--------------------+       +--------------------+       +--------------------+
| id: Integer        |       | id: Integer        |       | id: Integer        |
| username: String   |<>---->| user: User         |<>---->| name: String       |
| password: String   |       | favorite_teams     |       | country: String    |
| email: String      |       | favorite_comps     |       | type: String       |
| is_active: Boolean |       | bookmarked_matches |       | logo: Image        |
+--------------------+       +--------------------+       +--------------------+
                                       |                      |        |
                                       |                      |        |
                                       v                      v        v
+--------------------+       +--------------------+    +----------+  +----------+
|        Team        |       |       Match        |    |LeagueTable|  |CupStage  |
+--------------------+       +--------------------+    +----------+  +----------+
| id: Integer        |<>---->| id: Integer        |    | id: Int  |  | id: Int  |
| name: String       |       | competition        |    | comp     |  | comp     |
| short_name: String |       | home_team          |    | updated  |  | name     |
| country: String    |       | away_team          |    +----------+  | order    |
| logo: Image        |       | datetime: DateTime |          |       +----------+
| stadium: String    |       | status: String     |          |             |
| competitions       |       | home_score: Integer|          v             |
+--------------------+       | away_score: Integer|    +----------------+  |
     |         |             | minute: String     |    |LeagueTableEntry|  |
     |         |             | cup_stage          |    +----------------+  |
     |         |             +--------------------+    | id: Integer    |  |
     |         |                    |   |              | table          |  |
     |         v                    |   |              | team           |  |
+------------+ |                    |   |              | position: Int  |  |
|LineUp      | |                    |   |              | played: Int    |  |
+------------+ |                    |   |              | won: Int       |  |
| id: Integer| |                    |   |              | drawn: Int     |  |
| match      | |                    |   |              | lost: Int      |  |
| team       |<+                    |   |              | goals_for: Int |  |
+------------+                      |   |              | goals_against  |  |
      |                             |   |              | goal_difference|  |
      v                             |   |              | points: Int    |  |
+----------------+                  |   |              +----------------+  |
| LineUpPlayer   |                  |   |                                  |
+----------------+                  |   |                                  |
| id: Integer    |                  |   |                                  |
| lineup         |                  |   |                                  |
| name: String   |                  |   |                                  |
| number: Integer|                  |   v                                  |
| position: String                  |  +----------------+                  |
| is_starter: Bool|                 |  | MatchEvent     |<-----------------+
+----------------+                  +->+----------------+
                                       | id: Integer    |
                                       | match          |
                                       | team           |
                                       | minute: Integer|
                                       | event_type     |
                                       | player_name    |
                                       | additional_info|
                                       +----------------+





Relationships Description:

User ↔ UserProfile: One-to-one relationship. Each user has exactly one profile.
UserProfile ↔ Team/Competition/Match: Many-to-many relationships for favorites and bookmarks.

A profile can have many favorite teams and competitions
A profile can bookmark many matches
Each team/competition/match can be favorited/bookmarked by many users


Competition ↔ Team: Many-to-many relationship. Teams participate in multiple competitions, and competitions have multiple teams.
Competition → LeagueTable: One-to-one relationship for league competitions.
Competition → CupStage: One-to-many relationship. A cup competition can have multiple stages.
LeagueTable → LeagueTableEntry: One-to-many relationship. A league table has multiple entries (one for each team).
Team → Match: One-to-many relationships as both home and away teams.

A team can be the home team in many matches
A team can be the away team in many matches
Each match has exactly one home team and one away team


Competition → Match: One-to-many relationship. A competition has many matches.
Match → MatchEvent: One-to-many relationship. A match has multiple events.
Team → LineUp: One-to-many relationship. A team can have lineups for different matches.
Match → LineUp: One-to-many relationship. A match has lineups for both teams.
LineUp → LineUpPlayer: One-to-many relationship. A lineup consists of multiple players.

This UML diagram and these relationships represent the database schema we've implemented in the Django models for the Football Tracker application.
-----------------------------------------------------------

## Create a Project of your own choosing

Base on what you’ve learned until now , create a project of your choosing. Impress us with your creativity and execution.


## Minimum Requirements
- Use Django.
- Use Templates & Template Inheritance.
- Use static, media & dynamic urls as needed.
- Organize your project in apps as needed.
- Use models to represent you data.
- Use a CSS library to style your website.
- Must be responsive (good looking of big screens and small screens).
- User Authentication & Authorization (register, login, logout, Limit access to some pages using permissions , etc.)
- Use naming conventions & best practices.
- Strive to make the user journey intuitive and complete.

## Use python-dotenv to save your sensitive data.
- https://pypi.org/project/python-dotenv/


## Use a CDN or cloud storage provider to sore your large static files (videos, images, etc.), such as:
- https://firebase.google.com/docs/storage

## Use Git & Github to manage and track changes in your project.
- At lease commit and sync the changes once at the end of everyday.

## Edit the README.md file to include (include the info at the top):
- Project Name
- Project Description
- Features list.
- User Stories (link or file)
- UML (link or file)
- Wireframe (link or file)


## Example Projects :


1. **Task Management System:**
- **Overview:** Create a platform for managing tasks and projects within a team or organization.
- **Features:**
- User authentication and role-based access control.
- Task creation, assignment, and tracking.
- Project management with milestones.
- File uploads and comments on tasks.
- Notification system for task updates.




**Online Learning Platform:**

- **Overview:** Develop a platform for online courses, quizzes, and educational resources.
- **Features:**
- User registration and profile management.
- Course creation and enrollment.
- Quiz and assessment functionalities.
- Progress tracking and certificates.




**Crowdfunding Platform:**

- **Overview:** Build a crowdfunding website where users can create campaigns and seek financial support for their projects.
- **Features:**
    - User profiles with project history.
    - Campaign creation and customization.
    - Payment integration for contributions.
    - Progress tracking and updates.

**Job Board and Recruitment System:**

- **Overview:** Develop a platform for job seekers and employers to connect.
- **Features:**
    - User profiles with resumes.
    - Job posting and application functionalities.
    - Search and filter options for jobs.
    - Employer dashboards for managing postings.


**Inventory Management System:**

- **Overview:** Build a system for tracking and managing inventory for businesses.
- **Features:**
    - User authentication with roles (e.g., admin, staff).
    - Product catalog with stock levels.
    - Order processing and tracking.
    - Reporting and analytics.


**Recipe Sharing Platform:**

- **Overview:** Create a platform where users can share and discover recipes.
- **Features:**
    - User accounts with saved recipes.
    - Recipe creation and editing.
    - Search and categorization of recipes.
    - User ratings and reviews.
      
## Resources:

**Free high quality images :**

- https://www.pexels.com/
- https://unsplash.com

**Free sounds website:**

- https://mixkit.co/

**Free stock videos:**

- https://pixabay.com/videos/

**Free Fonts:**

- https://fonts.google.com

**Free Icons**

- https://fonts.google.com/icons
- https://icons.getbootstrap.com/

**CSS Library:**

- https://getbootstrap.com/
- https://get.foundation/index.html

**CSS Animation libraries:**

- https://animate.style
- https://www.minimamente.com/project/magic/



 
