pipeline { 
    agent any 
    options {
        skipStagesAfterUnstable()
    }   
    stages {
        stage('Build') { 
            steps { 
                echo "building"
            }
        }
        stage('Test'){
            steps {
                echo "testing"
                
            }
        }
        stage('Deploy') {
            steps {
                echo "deployment"
            }
        }
    }
}