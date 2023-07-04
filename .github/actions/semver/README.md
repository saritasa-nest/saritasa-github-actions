# Purpose

This is github action with bash based script that provides semantic version generation with specific logic (different than gitversion).
A unique release name is guaranteed for every branch+changeset combination.

Semantic version based on tag. Tag choose priority according branch type

- main branch releases can be versioned only from current commit tag
- detached HEAD should have tag that belongs main branch
- release/* releases can be versioned only from branch name but not tag, like release/1.1.1
- hotfix releases based on main tag (or failover) and postfix as title for semver
- all others in priority: branch tag -> main tag -> failover.
That grants us option when we can build well versioned feature/* releases with any tag inside. 

Image below is editable via draw.io

![image](semver.png)

# Usage
- `actions/checkout` with `fetch-depth: 0` is required for proper semver script work


```yaml
      - id: semver
        uses: saritasa-nest/saritasa-github-actions/.github/actions/semver@action/semver
      - run: |
          echo "Building ${{fromJson(steps.semver.outputs.version).SemVer}}"
      - name: Release app
        uses: saritasa-nest/saritasa-github-actions/.github/actions/fastlane-ios@v2.1
        env:
          REVISION: ${{fromJson(steps.semver.outputs.version).SemVer}}
          FL_UNLOCK_KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
          FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD: ${{ secrets.APPLICATION_SPECIFIC_PASSWORD }}
          FASTLANE_USER: ${{ secrets.TESTFLIGHT_USER }}
          FIREBASE_TOKEN: ${{ secrets.FIREBASE_TOKEN }}
          FL_VERSION_NUMBER_VERSION_NUMBER: ${{fromJson(steps.semver.outputs.version).MajorMinorPatch}}
          SLACK_URL: ${{ secrets.SLACK_URL }}
```