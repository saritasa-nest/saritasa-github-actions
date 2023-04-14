const core = require('@actions/core');
const shelljs = require('shelljs');

const UNKNOWN_VERSION = '0.0.0';

function getVersion(mainBranchName, ref, runNumber, sha) {
    let result = {};

    if (ref.indexOf('refs/tags/') === 0) { // Tag in main branch.
        const semVerTag = getSemVerTag(ref);

        checkTagOnBranch(semVerTag, mainBranchName);

        result.description = 'Main branch';
        result.suffix = '';
        result.majorMinorPatch = semVerTag;
    }
    else if (ref.indexOf('refs/heads/release/') === 0) {
        const matchResult = ref.match(/^refs\/heads\/release\/(\d+\.\d+\.\d+)$/);
        if (matchResult !== null) {
            result.description = 'Release branch';
            result.suffix = `-beta.${runNumber}`;
            result.majorMinorPatch = matchResult[1]
        }
        else {
            throw new Error('Wrong release name. Expected SemVer: release/x.x.x');
        }
    }
    else if (ref.indexOf('refs/heads/hotfix/') === 0) {
        const mainVersion = getMainTagArray(mainBranchName);
        let version;

        if (mainVersion !== null) {
            version = `${mainVersion[0]}.${mainVersion[1]}.${+mainVersion[2] + 1}`;
        }
        else {
            version = UNKNOWN_VERSION;
        }

        const matchResult = ref.match(/^refs\/heads\/hotfix\/(.*)$/);
        if (matchResult !== null) {
            result.description = 'Hotfix branch';
            result.suffix = `-${matchResult[1]}.${runNumber}`;
        }
        else {
            result.description = 'Unknown branch';
            result.suffix = `-unknown.${runNumber}`;
        }

        result.majorMinorPatch = version;
    }
    else if (ref === `refs/heads/${mainBranchName}`) {
        throw new Error(`Unexpected build from ${mainBranchName}. Ignore it and use tags instead.`);
    }
    else { // Develop or feature branch.
        const mainVersion = getMainTagArray(mainBranchName);
        let version;

        if (mainVersion !== null) {
            version = `${mainVersion[0]}.${+mainVersion[1] + 1}.0`;
        }
        else {
            version = UNKNOWN_VERSION;
        }

        if (ref === 'refs/heads/develop') {
            result.description = 'Develop branch'
            result.suffix = `-dev.${runNumber}`;
        }
        else {
            const featureMatch = ref.match(/^refs\/heads\/feature\/(.*)$/);

            if (featureMatch !== null) {
                result.description = 'Feature branch';
                result.suffix = `-${featureMatch[1]}.${runNumber}`;
            }
            else {
                result.description = 'Unknown branch';
                result.suffix = `-unknown.${runNumber}`;
            }
        }

        result.majorMinorPatch = version;
    }

    return formatVersion(result, sha);
} // getVersion

function checkTagOnBranch(tag, mainBranchName) {
    const gitResult = shelljs.exec(`git branch -r --format='%(refname:short)' --contains tags/${tag}`);

    if (gitResult.code === 0) {
        if (gitResult.stdout.indexOf(`origin/${mainBranchName}`) === -1) {
            throw new Error(`Tag ${tag} does not belong to ${mainBranchName} branch.`);
        }
    }
    else {
        throw new Error('Git command failed.');
    }
}

function getSemVerTag(ref) {
    let matchResult = ref.match(/^refs\/tags\/(\d+\.\d+\.\d+)$/);
    if (matchResult !== null) {
        return matchResult[1];
    }
    else {
        throw new Error(`Found a tag ${ref} in the wrong format. Expected SemVer: x.x.x`);
    }
}

function formatVersion(versionInfo, sha) {
    versionInfo.informationalVersion = (versionInfo.majorMinorPatch + versionInfo.suffix +
        '+' + sha).replaceAll('/', '-');

    versionInfo.semVer = versionInfo.majorMinorPatch + versionInfo.suffix;

    versionInfo.assemblySemVer = versionInfo.majorMinorPatch + '.0';

    console.log(`${versionInfo.description} ${versionInfo.majorMinorPatch} ${versionInfo.informationalVersion}`);

    return versionInfo;
}

function getMainTagArray(mainBranchName) {
    const gitResult = shelljs.exec(`git describe --tags --exact-match origin/${mainBranchName}`);

    if (gitResult.code === 0) {
        const foundTag = gitResult.stdout.split('\n')[0];

        if (foundTag.match(/^(\d+\.\d+\.\d+)$/) !== null) {
            return foundTag.split('.');
        }
        else {
            throw new Error(`Found a tag ${foundTag} in the wrong format. Expected SemVer: x.x.x`);
        }
    }
    else {
        core.warning(`Branch ${mainBranchName} does not have a tag.`);
        return null;
    }
}

exports.getVersion = getVersion;
