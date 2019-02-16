
const fs = require('fs');

const chokidar = require('chokidar');
const mergeYaml = require('merge-yaml');
const jsYaml = require('js-yaml');
const path = require('path');

const watcher = chokidar.watch(__dirname, {
    // To be refactored to the sane regex
    ignored: /(node_modules|\.git|deploy|\.idea|\.vscode|\.json|\.js|\.md|Dockerfile|result.yaml)/,
    persistent: true,
});

const componentsDir = path.join(__dirname, 'components');
const pathsDir = path.join(componentsDir, 'paths');
const outputFile = path.join(__dirname, 'result.yaml')

const clearRef = (object) => {
    for (property in object) {
        if (object[property] instanceof Object) {
            clearRef(object[property]);
        } else if (property === '$ref') {
            object[property] = object[property]
                .slice(object[property].lastIndexOf('#'));
        };
    };
};

const mergeYamlFiles = () => {
    const paths = fs.readdirSync(pathsDir)
        .map(fileName => path.join(pathsDir, fileName));

    const components = fs.readdirSync(componentsDir)
        .map(fileName => path.join(componentsDir, fileName));

    const files = paths.concat(components, path.join(__dirname, 'api.yaml'))
        .filter(fileName => fileName.indexOf('.yaml') > -1);

    const api = mergeYaml(files);

    clearRef(api);

    fs.writeFileSync(outputFile, jsYaml.dump(api));
};

const merge = (filePath) => {
    console.log(`${filePath} has been changed, recompiling...`);
    mergeYamlFiles();
};

if (process.argv.indexOf('merge') > -1) {
    mergeYamlFiles();
    process.exit(0);
}

watcher
    .on('add', merge)
    .on('change', merge)
    .on('unlink', merge)
    .on('error', merge)