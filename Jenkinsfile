
Map matrix_axes = [
    hosttype: ['clip'],
    media_type: ['inst-iso', 'live-iso'],
    target_name: ['minimal', 'sftp-dropbox', 'apache', 'vpn'],
    os_name: ['rhel', 'centos'],
    os_version: ['7.6', '8.1']
]

@NonCPS
List getMatrixAxes(Map matrix_axes) {
    List axes = []
    Map emptyMap = [:]
    List prevCombo = [emptyMap]
    for (entry in matrix_axes) {
        String axis = entry.key
        List values = entry.value
        List comboNext = []
        for (value in values) {
            for(int i = 0; i < prevCombo.size(); i++) {
                Map newMap = prevCombo[i].clone()
                newMap[axis] = value
                comboNext << newMap
            }
        }
        prevCombo = comboNext
    }
    for (entry in prevCombo) {
        for (letter in entry['os_version']) {
            entry['os'] = entry['os_name'] + letter
            break
        }
    }
    return prevCombo
}

List axes = getMatrixAxes(matrix_axes)

@NonCPS
List getEnvList(Map axis) {
    List envList = []
    for (entry in axis) {
        envList << "${entry.key}=${entry.value}"
    }
    return envList
}

List getTaskMap(List axes) {
    List tasks = []
    for(int i = 0; i < axes.size(); i++) {
        Map axis = axes[i]
        List axisEnv = getEnvList(axis)
        String nodeLabel = axis['os'] + " && " + axis['hosttype']
        println("nodelabel: " + nodeLabel)
        String outerStage = "Build and test " + axis['os'] + "-" + axis['os_version'] + " " + axis['target_name'] + " " + axis['media_type']
        String prepareStage = "Prepare " + axis['os'] + "-" + axis['os_version'] + " " + axis['target_name'] + " " + axis['media_type']
        String buildStage = "Build " + axis['os'] + "-" + axis['os_version'] + " " + axis['target_name'] + " " + axis['media_type']
        String testStage = "Test " + axis['os'] + "-" + axis['os_version'] + " " + axis['target_name'] + " " + axis['media_type']
        String repoFile = "CONFIG_REPOS." + axis['os'] + "-" + axis['os_version']
        String target_name = axis['target_name']
        String media_type = axis['media_type']
        Map task = [name:axisEnv.join(', '), job:{ ->
            stage outerStage
            catchError(message:'stage failed', buildResult:'UNSTABLE', stageResult:'UNSTABLE', catchInterruptions:false) {
                // see if a particular node exists.  there may be better ways to do this
                try {
                    timeout(time: 2, unit: 'SECONDS') {
                        node(nodeLabel) {
                            sh "true"
                        }
                    }
                } catch (hudson.AbortException err) {
                    String message = "${err}"
                    if(message != null && message.contains("Queue task was cancelled")) {
                        error("No suitable nodes found")
                    } else {
                        echo "hudson.AbortException when trying to find node but message is unexpected: message: ${message}"
                        throw err
                    }
                } catch (err) {
                    echo "Some random exception when trying to find node: ${err}"
                    throw err
                }
                // perform the build and test
                try {
                    timeout(time: 120, unit: 'MINUTES') {
                        node(nodeLabel) {
                            sh "sudo rm -rf .* * || true"
                            checkout scm
                            if(!fileExists(repoFile)) {
                                error("No CONFIG_REPO file " + repoFile)
                            }
                            sh "cp ${repoFile} CONFIG_REPOS"
                            sh "make clip-${target_name}-${media_type}"
                            archiveArtifacts "*.iso"
                            sh "./support/tests/media/qemu-test-${media_type}.sh *.iso"
                            archiveArtifacts(artifacts:"scap", allowEmptyArchive:true)
                        }
                    }
                } catch (hudson.AbortException err) {
                    String message = "${err}"
                    if(message != null && message.contains("Queue task was cancelled")) {
                        error("Timeout exceeded during build and test")
                    } else {
                        echo "hudson.AbortException when trying to build and test but message is unexpected: message: ${message}"
                        throw err
                    }
                } catch (err) {
                    echo "Some random exception while running build and test: ${err}"
                    throw err
                }
            }
        }]
        tasks << task
    }
    return tasks
}

List tasks = getTaskMap(axes)


for (int i=0; i< tasks.size(); i++) {
tasks[i]['job'].call()
}
