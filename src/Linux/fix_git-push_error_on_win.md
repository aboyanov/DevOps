# FIX - Error with pushing to git remote repo from windows host<a name="fix_git-push_win"></a>

This simple guide is showing how to resolve `Error: fatal: could not read Username for 'https://github.com': Invalid argument`\. The problem occurs when trying to push from a local branch to the remote origin(E.g. `git push origin master`)


**Below I am listing steps to fix the problem:**

1. Delete your remote data from `.git/config`\.
Delete the [remote "origin"] block
   
   ```sh
   [core]
        repositoryformatversion = 0
        filemode = false
        bare = false
        logallrefupdates = true
        symlinks = false
        ignorecase = true
    [remote "origin"]
        url = https://github.com/Alexsa6ko94/DevOps.git
        fetch = +refs/heads/*:refs/remotes/origin/*
    [branch "master"]
        remote = origin
        merge = refs/heads/master
   ```

1. Add the new `[remote "origin"]`\.
Type in the terminal:
   ```
   git remote add origin https://{username}:{password}@github.com/{username}/project.git
   ```

1. Test it with push command\.

   ```
   git push origin master
   ```
