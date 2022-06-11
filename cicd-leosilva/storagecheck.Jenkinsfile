pipeline {
    agent {
        label('terraform')
    }
    environment {
        AWS_ACCESS_KEY_ID     = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')   
    }
    triggers {
        cron('*/10 * * * *')
    }
    stages {
        stage ('check') {
            steps {
                sh 'ls'
                sh 'chmod +x checkdev.sh'
                sh './checkdev.sh'
                sh 'chmod +x checkprod.sh'
                sh './checkprod.sh'
            }

        }
    }
}
