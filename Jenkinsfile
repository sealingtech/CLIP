pipeline {
    agent none
    stages {
        stage('BuildAndTest') {
            matrix {
                agent { label "${os} && ${hosttype}" }
                options { disableConcurrentBuilds() }
                axes {
                    name 'os'
                    values 'rhel7', 'centos7', 'rhel8', 'centos8'
                }
                axes {
                    name 'hosttype'
                    values 'clip'
                }
                axes {
                    name 'target_name'
                    values 'minimal', 'sftp-dropbox', 'apache', 'vpn'
                }
                axes {
                    name 'media_type'
                    values 'inst-iso', 'live-iso'
                }
                axes {
                    name 'os_version'
                    values '7.6'
                }
            }
            stages {
                stage('Prepare') {
                    steps {
                        if (fileExists("CONFIG_REPOS.${os}-${os_version}")) {
                            writeFile("CONFIG_REPOS", fileRead("CONFIG_REPOS.${os}-${os_version}"))
                        } else {
                            echo "error: missing CONFIG_REPOS.${os}-${os_version}"
                            error()
                        }
                    }
                }
                stage('Build') {
                    steps {
                        sh "make clip-${target_name}-${media_type}"
                    }
                }
                stage('Test') {
                    steps {
                        sh "./support/tests/media/qemu-test-${media_type}.sh *.iso"
                    }
                }
            }
        }
    }
}
