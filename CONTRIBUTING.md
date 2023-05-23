# Contribution guidelines

Table of contents
- [Contribution guidelines](#contribution-guidelines)
  - [How can you contribute?](#how-can-you-contribute)
    - [Help triage issues](#help-triage-issues)
    - [Updating documentation](#updating-documentation)
  - [Getting started](#getting-started)
    - [Making changes](#making-changes)
    - [Keeping your fork up to sync](#keeping-your-fork-up-to-sync)
    - [Pull requests](#pull-requests)
      - [Considerations before submitting a pull request](#considerations-before-submitting-a-pull-request)
    - [Closing issues](#closing-issues)
    - [Triage help](#triage-help)

## How can you contribute?
CYFS Browser welcomes contributions of all kinds! You can make a huge impact without writing a single line of code

### Help triage issues
One of the easiest ways to help is to [look through our issues tab](https://github.com/buckyos/cyfs-browser/issues)
* Does the issue still happen? Sometimes we fix the problem and don't always close the issue
* Are there clear steps to reproduce the issue? If not, let's find and document some
* Is the issue a duplicate? If so, share the issue that is being duplicated in the conversation
* See our [Triage Guidelines page](https://github.com/buckyos/cyfs-browser/wiki/Triage-Guidelines) for more info about this process
* Making sure issues that are fixed have the appropriate milestone set. There may be pull requests fixing the bug on the different product channels and sometimes the issues are forgotten about (and aren't updated)

### Updating documentation
Documentation is extremely important. There are lots of areas we can improve:
* Having more clear or up-to-date instructions in the README for both [`cyfs-browser`](https://github.com/buckyos/cyfs-browser/blob/master/README.md) .
* Capturing/updating helpful information [in our wiki](https://github.com/buckyos/cyfs-browser/wiki). You'll need to reach out to a CYFS team member to request permission - you can do this by creating a new issue or tagging a CYFS team member in an existing issue.
* Helping to propose a way to bring documentation to other languages. Right now, everything is in English
* Improving this document :smile:


## Getting started
* Make sure you have a [GitHub account](https://github.com/join).
* Submit a [ticket](https://github.com/buckyos/cyfs-browser/issues) for your issue if one does not already exist. Please include the CYFS version, operating system, and steps to reproduce the issue.
* Fork the repository on GitHub, this might be [`CYFS-browser`](https://github.com/buckyos/cyfs-browser).
* For changes to JavaScript files, we recommend installing a [Standard](http://standardjs.com/) plugin for your preferred text editor in order to ensure code style consistency.
* For C++ changes, you can consider setting up [clang-format](https://chromium.googlesource.com/chromium/src/+/master/docs/sublime_ide.md#Format-Selection-with-Clang_Format-Chromium-only) for your editor.
* For changes which involve patches, please check out our [Patching Chromium](https://github.com/buckyos/cyfs-browser/script/Patching-Chromium) guide.

### Making changes
Once you've cloned the repo to your computer, you're ready to start making edits!

Depending on which you're editing, you'll need to add your fork to the remotes list. By default, `origin` is set to upstream.


There are a few tips we can suggest:

* Make a new branch for your work. It helps to have a descriptive name, like `fix-some-issue`.
* Make commits in logical units. If needed, run `git rebase -i` to squash commits before opening a pull request.
* New features and most other pull requests require a new [test](https://github.com/buckyos/cyfs-browser/wiki/Tests) to be written before the pull request will be accepted.  Some exceptions would be a tweak to an area of code that doesn't have tests yet, text changes, build config changes, things that can't be tested due to test suite limitations, etc.
* Use GitHub [auto-closing keywords](https://help.github.com/articles/closing-issues-via-commit-messages/) in the commit message, and make the commit message body as descriptive as necessary. Ex:

````
    Add contributing guide

    This is a first pass at a contributor's guide so now people will know how to
    get pull requests accepted faster.

    Fix https://github.com/buckyos/cyfs-browser/issues/108
````


### Keeping your fork up to sync
- `cyfs-browser` clone themselves with the remote `origin` being upstream, so you can update either using `git pull`.
- Once `origin` is fetched, you can rebase your `beta` branch against `origin/beta`
    ```sh
    git fetch origin
    git checkout -b fork_master origin/beta
    git rebase origin/master
    git push origin fork_master:beta
    ```

An easier strategy might be to keep `origin` in sync and then create branches based on that (and push those to your fork).


### Pull requests
After the changes are made in your branch, you're ready to submit a patch. Patches on GitHub are submitted in the format of a pull request.

#### Considerations before submitting a pull request
Some helpful things to consider before submitting your work
* Did you manually test your new change?
* Does your pull request fix multiple issues? If so, you may consider breaking into separate pull requests.

### Closing issues

* Issues should be assigned the milestone when the PR is merged (and the fix is landed in Nightly aka master).
* Some issues may need to be uplifted to other channels (Dev / Beta / Release). Please see our notes on [uplifting a pull request](https://github.com/buckyos/cyfs-browser/wiki/Uplifting-a-pull-request).
* If an issue is closed without a fix, because it was a duplicate, or perhaps it was invalid, then any milestone markers should be removed.
* If a bug is not fully fixed after its issue is closed, open a new issue instead of re-opening the existing one (unless the code has been reverted).

### Triage help

* Invalid bugs should be closed, tagged with invalid, or a comment should be added indicating that they should if you do not have permission.
* Asking for more detail in an issue when it is needed is helpful.
* Adding applicable labels to an issue is helpful.
* Adding and finding duplicates, and linking them together is helpful.
* Creating tracking issues for an area of work with multiple related issues is helpful.
* Calling out things which seem important for extra attention is helpful.
* Improving steps to reproduce is helpful.
* Testing and adding a comment with "Could not reproduce" if an issue seems obscure is helpful.
* Testing open pull requests.
* You can be granted write permission if you've helped a lot with triage by pinging @bbondy, @bsclifton, @kjozwiak, or another CYFS team member.
* Helping make sure issues have a clear and understandable name (ex: not something like "CYFS is broken").
* The first comment in an issue ideally would have a clear description of the issue and describe the impact to users. Asking folks for screenshots, steps to reproduce, and more information is highly recommended so that the issue is as clear as possible.
* If the issue is a duplicate, please let the issue creator know in a polite way how they can follow and track progress of the parent issue (including an ETA if it's marked with a milestone).
