import boto3
import requests
import json
from params import Params

def get_image_bytes(url:str)->bytes:
    result = False
    try:
        resp = requests.get(url)
        if resp.status_code==200:
            result = resp.content
        else:
            print(f'Accessing image failed: {resp.status_code}')
    except Exception as e:
        print(e)
    return result

def get_boto_session()->boto3.client:
    run_mode = Params.run_as
    if run_mode=="local":
        session = boto3.Session(profile_name=Params.aws_profile)
    else:
        session = boto3.Session()    
    return session.client('rekognition')

def create_collection(client:boto3.client, collection_name:str)->bool:
    result = False
    try:
        if client.create_collection(CollectionId=collection_name):
            result = True
    except Exception as e:
        pass
    return result

def describe_collection(client:boto3.client, collection_name:str):
    result = False
    try:
        result = client.describe_collection(CollectionId=collection_name)            
    except Exception as e:
        pass
    return result

def search_image_in_collection(image_url:str, collection_name:str)->dict:
    result = False
    # get a session for Rekognition
    client = get_boto_session()
    # get the image bytes
    image_bytes = get_image_bytes(url=image_url)
    # now check if image exists in collection    
    if image_bytes:
        result = client.search_faces_by_image(
            CollectionId=collection_name,
            Image={'Bytes': image_bytes},
            MaxFaces=Params.max_faces,            
            FaceMatchThreshold=Params.image_threshold
        )        
    return result

def generate_response(image_url:str, collection_name:str, result:dict)->dict:
    pass

def search_image_for_face(image_url:str):
    result = {
        "url": image_url,
        "image_found": False
    }
    # get collection name
    collection_name = Params.collection_name
    
    # find or create the collection
    if collection_name:        
        # if collection exists or created, proceed    
        image_info = search_image_in_collection(image_url=image_url, collection_name=collection_name)
        # this image was not present in the index
        if image_info: # if no image is found, this returns a False
            result['image_found'] = True
            result['image_info'] = image_info
    else:
        result['error'] = 'Collection not found!'
    return result

def add_image_to_collection(image_url: str, image_tag: str, collection_name:str)->dict:
    
    result = {
        'status': False
    }        
    if collection_name:        
        client = get_boto_session()
        # try to describe the collection first.    
        if describe_collection(client=client, collection_name=collection_name):
            print(f'Collection {collection_name} already exists.')
            collection_exists=True
        else:
            # create the collection
            resp = create_collection(client=client, collection_name=collection_name)
            if resp:
                print(f'Collection {collection_name} does not exist. Created it successfully')
                collection_exists = True
            else:
                # failed to create collection
                result['error'] = 'Failed to create collection.'
                print(resp)
                collection_exists = False
        # make sure the collection was created if it did not exist and then proceed.
        if collection_exists:
            # add the image to collection
            image_bytes = get_image_bytes(url=image_url)             
            if image_bytes:                
                response = client.index_faces(CollectionId=collection_name,
                                      Image={'Bytes': image_bytes},
                                      ExternalImageId=image_tag,
                                      MaxFaces=Params.max_faces,
                                      QualityFilter="AUTO",
                                      DetectionAttributes=['ALL'])
                print(response)
                result['status'] = True
                result['response'] = response
            else:
                result['error'] = f'Unable to access image: {image_url}'
    else:
        result['error'] = 'No collection name was found'
    return result

if __name__=="__main__":
    #run_image_tagging('https://res.cloudinary.com/dbmataac4/image/upload/w_300/test/rekognition/woman-8273285_640.jpg')
    resp = search_image_for_face('https://res.cloudinary.com/dbmataac4/image/upload/v1709757816/test/rekognition/child-807536_640.jpg')
    #resp = add_image_to_collection(image_url='https://res.cloudinary.com/dbmataac4/image/upload/v1709757815/test/rekognition/child-807547_640.jpg', image_tag='child-2')
    print(json.dumps(resp))
