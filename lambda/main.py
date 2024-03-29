import json
from cld_utils import get_changed_model_name, get_image_url, search_and_add_face_mtd
from facerecog import add_image_to_collection
from params import Params

def is_training_image(public_id:str)->bool:
    """
    Check if this is a training image.
    """
    return public_id.startswith(Params.train_path)

# changed runtime as well
def lambda_handler(event:dict, context:dict)->dict:
    """
    AWS Lambda handler function.
    """

    message = 'Default message'
    #Params.print_params()
    
    # Check if the request body is present
    if event['httpMethod'] == "POST" and 'body' in event:
        # Parse the JSON string to extract the request body
        request_body = json.loads(event['body'])
        # check if this is an upload or metadata changed notification
        if request_body['notification_type']=='upload' and request_body['resource_type']=='image':
            # get the public id and URL
            public_id = request_body['public_id'] 
            # make sure this is not a training image 
            if is_training_image(public_id=public_id) == False:
                message = search_and_add_face_mtd(public_id=public_id)
            else:
                message = "Image is part of training path. Won't be checked."
        elif request_body['notification_type']=='resource_metadata_changed':
            # this can be multiple images
            resources = request_body['resources']            
            for public_id in resources:
                if is_training_image(public_id=public_id):
                    if resources[public_id]['resource_type']=='image':
                        changed_model_name =  get_changed_model_name(resource_info=resources[public_id])                    
                            # if it has changed, the value will be a string else a False boolean value
                        if changed_model_name:
                            # now set this new metadata on the training image                                                
                            cloud_name=Params.cloud_name
                            default_transformation=Params.default_transformation
                            image_url = get_image_url(public_id=public_id, cloud_name=cloud_name, default_transformation=default_transformation)
                            collection_name = Params.collection_name
                            print(f'Indexing image {image_url} belonging to {collection_name}')
                            message = add_image_to_collection(image_url=image_url, image_tag=changed_model_name, collection_name=collection_name)                            
                        else:
                            message = "Metadata hasn't changed"                                    
                    else:
                        message = "Object is not an image - won't be checked"
                else:
                    message = "Image is part of training path. Won't be checked."
        else:
            message = f"Lambda wrongly configured. No action for {request_body['notification_type']} events"                
    elif event['httpMethod'] == "GET":
        message = "Welcome from GET"
        if 'queryStringParameters' in event and event['queryStringParameters'] is not None:
            # Access the query parameters
            query_parameters = event['queryStringParameters']

            # default action is to infer the image
            action = 'infer'

            if 'action' in query_parameters and query_parameters.get('action') == 'train':
                action = 'train'
            
            if 'public_id' in query_parameters:
                public_id = query_parameters.get('public_id')
                # make sure public id is not null
                if public_id:
                    if action == 'infer':
                        message = search_and_add_face_mtd(public_id=public_id)
                    else:
                        if is_training_image(public_id=public_id):
                            default_transformation=Params.default_transformation
                            image_url = get_image_url(public_id=public_id, cloud_name=cloud_name, default_transformation=default_transformation)
                            collection_name = Params.collection_name
                            print(f'Indexing image {image_url} belonging to {collection_name}')
                            message = add_image_to_collection(image_url=image_url, image_tag=changed_model_name, collection_name=collection_name)                            
                        else:
                            message = "This is a training image. Won't be checked."                                                   
                else:
                    message = 'Public id query string is empty.'
            else:
                message = "No public_id provided"
        else:
            message = "No query parameters provided"
    else:
        message = "Hello from AWS Lambda! (No request body provided)"

    print(json.dumps({'message': message}))
    # Return response
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'message': message})
    }
