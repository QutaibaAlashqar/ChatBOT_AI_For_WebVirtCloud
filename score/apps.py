


###
######
#########
############
############### First Version 
############
#########
######
###



from django.apps import AppConfig

class ScoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'score'



###
######
#########
############
############### Secend Version 
############
#########
######
###



"""


from django.apps import AppConfig
import subprocess
import os

class ScoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'score'
    model_process = None

    def ready(self):
        self.start_model()

    def start_model(self):
        if ScoreConfig.model_process is not None:
            return  # Model process already started

        process = subprocess.Popen(
            ['/home/ozgur-ent/Desktop/ChatBotAI/open-interpreter/venv39/bin/interpreter', '--local', '--llama3'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Check if the model is fully loaded
        while True:
            line = process.stdout.readline()
            if 'Model loaded.' in line:
                break

        # Create a flag file to indicate the model is ready
        with open('/tmp/llama_ready.flag', 'w') as f:
            f.write('Llama model is ready')

        ScoreConfig.model_process = process

    @staticmethod
    def get_model_process():
        return ScoreConfig.model_process



"""