pipeline { 
    agent any 
    options {
        skipStagesAfterUnstable()
    }   
    stages {
        stage('Build') { 
            steps { 
                sh echo 'build'
                sh 'make' 
            }
        }
        stage('Test'){
            steps {
                sh 'echo test'
                sh 'make' 
                
            }
        }
        stage('Deploy') {
            steps {
                sh 'echo deploy'
                sh 'echo deploy2'
                sh 'make' 
            }
        }
    }
}