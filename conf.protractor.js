exports.config = {
    framework: 'jasmine',
    specs: ['**/*spec.js'],
    allScriptsTimeout: 50000,
    jasmineNodeOpts: { defaultTimeoutInterval: 260000 },
    capabilities: {
        'browserName': 'chrome'
    },
}
