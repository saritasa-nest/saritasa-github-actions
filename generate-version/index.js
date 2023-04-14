const core = require('@actions/core');
const github = require('@actions/github');

const gitversion = require('./gitversion');
const dotnet = require('./dotnet');

try {
    const mainBranchName = core.getInput('main-branch-name');
    const updateDotnetProjectFiles = core.getInput('update-dotnet-project-files');
    const dotnetProjects = core.getInput('dotnet-projects');

    const versionInfo = gitversion.getVersion(mainBranchName,
        github.context.ref, github.context.runNumber, github.context.sha)

    // 1.2.3+master.dc6ebc32aa8ecf20529a677d896a8263df4900ee
    // 1.3.0-beta.12+release-1.3.0.56793f7f6259dd4042d57e9d206cb9b1d8434508
    core.setOutput('informational-version', versionInfo.informationalVersion);
    // 1.2.3
    // 1.3.0-beta.12
    core.setOutput('semver', versionInfo.semVer);
    // 1.2.3.0
    // 1.3.0.0
    core.setOutput('assembly-semver', versionInfo.assemblySemVer);

    console.log(`informational-version: ${versionInfo.informationalVersion}`);
    console.log(`semver: ${versionInfo.semVer}`);
    console.log(`assembly-semver: ${versionInfo.assemblySemVer}`);

    if (updateDotnetProjectFiles === 'true') {
        dotnet.updateDotnetProjectFiles(dotnetProjects, versionInfo.informationalVersion);
    }
} catch (error) {
    core.setFailed(error.message);
    console.log(error);
}
