import os

class Params:
    run_as = os.environ['RUN_AS'] if os.environ.get('RUN_AS') else 'server'
    collection_name = os.environ['COLLECTION_NAME'] if os.environ.get('COLLECTION_NAME') else 'akshay-collection'
    aws_profile = os.environ['AWS_PROFILE_NAME'] if os.environ.get('AWS_PROFILE_NAME') else 'aws_sol'
    image_threshold = int(os.environ['IMAGE_THRESHOLD']) if os.environ.get('IMAGE_THRESHOLD') else 80
    max_faces = int(os.environ['MAX_FACES']) if os.environ.get('MAX_FACES') else 1
    mtd_external_id = os.environ['EXTERNAL_ID'] if os.environ.get('EXTERNAL_ID') else 'model_name'    
    cloud_name = os.environ['CLOUD_NAME'] if os.environ.get('CLOUD_NAME') else 'dbmataac4'
    default_transformation = os.environ['DEFAULT_TRANSFORMATION'] if os.environ.get('DEFAULT_TRANSFORMATION') else 'f_jpg,q_auto,w_1024'    
    train_path = os.environ['TRAIN_PATH'] if os.environ.get('TRAIN_PATH') else 'test/rekognition/'
    secret_name = os.environ['SECRET_NAME'] if os.environ.get('SECRET_NAME') else 'prod/akshay/react'

    @staticmethod
    def print_params():
        print(Params.run_as, Params.collection_name, Params.aws_profile)
