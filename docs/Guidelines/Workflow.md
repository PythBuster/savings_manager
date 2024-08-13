# General

- Versioning: [Github](https://github.com/PythBuster/savings_manager)
- Issue Tracker: [Github](https://github.com/users/PythBuster/projects/1)
- Communication Tools: [Discord Channel](https://discord.gg/GH5jrMXbMJ)
- For detailed information, see README.md in project root dir.

# Branching

Git Flow strategy is used for the [savings_manager repository](https://github.com/PythBuster/savings_manager).

main-Branches:
- main
- dev (set as **default**-branch, see [Linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue))
- release

feature-Branches:
- feauture/issue-number-...
- hotfix/issue-number-...
- bug/issue-number-...
- refactor/issue-number-...
- doc/issue-number-...
- test/issue_number-...
# Commits

Each commit need to start with the keyword **issue** and the issue number, followed by a keyword like **fix, feat, doc, refactor** or **build** and the commit message.

__Example__:
`issue #1 feat: implement db manager`

or if issue is a bug to resolve:

`issue #1 fix: prevent session start before starting the database 

