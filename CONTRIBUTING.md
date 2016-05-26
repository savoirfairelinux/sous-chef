# Contributing to Sous-Chef

First of all, thanks for reading this and taking time to contribute! :+1: We need volunteer developers to help this project grow.

The following is a set of guidelines for contributing to Sous-Chef, which is hosted in the [Savoir-faire Linux organization](https://github.com/savoirfairelinux) on GitHub. 
Feel free to propose changes to this document in a pull request.

If you haven't already, please join us on IRC: `#feastproject` on Freenode.

## Useful resources

* [Coding style guide](https://www.python.org/dev/peps/pep-0008/)
* [CI server (Travis)](https://travis-ci.org/savoirfairelinux/santropol-feast)
* [Waffle Dashboard](https://waffle.io/savoirfairelinux/santropol-feast)
* [Coveralls](https://coveralls.io/github/savoirfairelinux/santropol-feast?branch=dev)
* [Semantic UI](http://semantic-ui.com/)
* [Interactive wireframes](https://marvelapp.com/2187ig4)
* [Creating a Pull Request on GitHub](https://help.github.com/articles/creating-a-pull-request/)
* [IRC](http://webchat.freenode.net): channel **#feastproject**

## How can I contribute ?

### Code contribution

A pre-requisite is to have Sous-Chef installed on your machine.
The installation procedure is based on Docker and is described [on GitHub](https://github.com/savoirfairelinux/santropol-feast/blob/dev/INSTALL.md).

#### Issues

If you are unsure where to begin contribution to Sous-Chef, you can start by looking through the issues page. 
Numerous issues are created and waiting for your love on the [issue board](https://github.com/savoirfairelinux/santropol-feast/issues).

You may also use [Waffle](https://waffle.io/savoirfairelinux/santropol-feast) as a more *Agile-like* dashboard.

Please refer to the issues labels and topics for more information on how categorizing the issues.

#### Pull Requests

Contributions will be accepted through the creation of Pull Requests. Here is the workflow:

* Fork the repository into yours and work from there
* Commit and push your changes into your fork
* When you are done, create a [Pull Request](https://github.com/savoirfairelinux/santropol-feast/compare) in Feast repository on the **dev** branch

A template is provided to create your Pull Request. Try to fill the information at the best of your knowledge.

For your Pull Request to be merged, it should respect the following:

* Tests must pass
* PEP-8 coding style must be respected
* Code coverage must be complete
* The branch can be merged automatically

[TravisCI](https://travis-ci.org/) is configured to run those checks on every Pull-Request. It is recommanded you configure your fork to do the same.

### Documentation

Documentation is important and can always be improved:

* Installation instructions
* Test procedures
* How to help translating the project
* Updating the [Roadmap](https://github.com/savoirfairelinux/santropol-feast/wiki/ROADMAP)

The prefered syntax is Asciidoc. Markdown is also accepted.

The [project wiki](https://github.com/savoirfairelinux/santropol-feast/wiki/) on GitHub could also be used.

### Reporting bugs

Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/). 

#### How to submit a good bug report

Please include as many details as possible. An issue template is automatically loaded when you create an issue.

* Use a clear and comprehensive title for the issue
* Describe the expected behaviour in as many details as possible
* Describe the actual behaviour in as many details as possible
* Detail the steps which reproduce the problem
* Include screenshots and animated GIFs. You can use [this tool](https://github.com/colinkeenan/silentcast) on Linux.

### Testing the application

Our development process is based on Continuous Integration. We love to have a nice code coverage! 

Each Django module comes with its own `tests.py` file. Feel free to implement missing unit or functional tests.

### Translating

Sous-Chef is a bilingual (french/english) application and needs your talent of translators!

It uses Django multilingual framework, based on Gettext and po files.

Each module has its own set of translation files. To list them all:

```
$ find . -name "*.po"
```

[Poedit](https://poedit.net/) can be used to translate those files.
Follow the workflow described in the Code section to contribute your translations.

An other way to contribute there is to review the code and make sure all strings are translatable.

## Additional notes

### Issue labels

| Label name | Description |
| --- | --- |
| `enhancement` | Feature requests. |
| `bug` | Confirmed bugs or reports that are very likely to be bugs. |
| `question` | Questions more than bug reports or feature requests (e.g. how do I do X). |
| `help-wanted` | The Sous-Chef core team would appreciate help from the community in resolving these issues. |
| `beginner` | Less complex issues which would be good first issues to work on for users who want to contribute to Sous-Chef. |
| `duplicate` | Issues which are duplicates of other issues, i.e. they have been reported before. |
| `wontfix` | The core team has decided not to fix these issues for now, either because they're working as intended or for some other reason. |
| `invalid` | Issues which aren't valid (e.g. user errors). |

### Issue topics

| Label name | Description |
| --- | --- |
| `client` | Related to client management. |
| `documentation` | Related to any kind of documentation. |
| `frontend` | Related to Semantic UI integration, or Javascript problems. |
| `i18n` | Related to any kind of internationalization problem. |
| `python` | Related to python programming. |
| `tests` | Related to unit tests, functional tests or manual testing. |
| `ux/ui` | Related to user experience, user interface, design. |
