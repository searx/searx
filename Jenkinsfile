node {
    checkout scm

    def pythonImage
    stage('build docker image') {
        pythonImage = docker.build("python")
    }
    stage('test') {
        pythonImage.inside {
            sh './manage.sh update_dev_packages'
            sh './manage.sh pep8_check'
            sh './manage.sh unit_tests'
        }
    }
}