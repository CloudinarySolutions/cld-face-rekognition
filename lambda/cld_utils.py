import cloudinary.api
import cloudinary.uploader
from unidecode import unidecode
from facerecog import search_image_for_face
from params import Params
from awsutil import get_secret

def initialize_cloudinary(credentials:dict):
    #print(type(credentials), credentials)
    cloudinary.config(
        cloud_name = credentials['cloud_name'],
        api_key = credentials['api_key'],
        api_secret = credentials['api_secret']
    )

def stringify_metadata(external_id:str, values:list[str])->str:
    values = [f'\"{sanitize_name(_)}\"' for _ in values]
    return f'{external_id}=[{",".join(values)}]'

def add_metadata_to_image(public_id:str, model_names:list[str])->bool:
    # first check if the model name exists in metadata
    # find metadata field name
    result = False    
    
    external_id = Params.mtd_external_id
    add_model_to_metadata(external_id=external_id, model_names=model_names) 
    mtd_string = f'{external_id}={model_names[0]}' # stringify_metadata(external_id=external_id,values=model_names )
    print(f"Applying: {mtd_string} to {public_id}")
    resp = cloudinary.uploader.update_metadata(
        mtd_string, #{[sanitize_name(x) for x in model_names]}',
        [public_id]
    )
    print("Done")
    result = True

    return result
    

def sanitize_name(name:str)->str:
    # convert name to lower case
    name = name.lower()
    # convert space to underscore
    name = name.replace(' ', '_')
    # replace the '`' character
    name = name.replace('`','')
    # remove any accent characters
    name = unidecode(name)
    return name

def add_model_to_metadata(external_id:str, model_names:list[str])->bool:
    result = False    
    # get the existing model names
    fields = cloudinary.api.metadata_field_by_field_id(external_id)
    existing_model_names = set()
    if fields.get('datasource') and fields['datasource'].get('values'):        
        for field in fields['datasource']['values']:
            print(field)        
            existing_model_names.add(field['value'])
    
    
    # check each model name and add them if needed
    for model_name in model_names:
        name_id = sanitize_name(model_name)
        
        if model_name not in existing_model_names:
            # this is a new model. add it to the metadata set
            #resp = cloudinary.api.update_metadata_field_datasource(
            #    external_id,
            #    [{
            #        'external_id': name_id,
            #        'value': model_name
            #    }]
            #)
            #print(f'{model_name} not found. Added name successfully\n{resp}')
            #added - so let's say we're done
            result = True
        else:
            # this is an existing model. nothing to do.
            print(f'{model_name} already exists')
            result = True
    
    return result

def get_changed_model_name(resource_info:dict)->dict:
    # first get the metadata field name
    result = False
    old_mtd = resource_info['previous_metadata'].get(Params.mtd_external_id) if resource_info.get('previous_metadata') else None
    new_mtd = resource_info['new_metadata'].get(Params.mtd_external_id)  
    
    if new_mtd:
        if old_mtd:
            if old_mtd != new_mtd:
                result = new_mtd
            else:
                print(f'{Params.mtd_external_id} hasn\'t changed')
        else:
            # this is the first time value is being set
            result = new_mtd
               
    return result

def get_image_url(public_id:str, cloud_name:str, default_transformation:str="q_auto")->str:
    # for this purpose, we will simply use res.cloudinary.com, cloudname, default transformation if specified and the public id    
    default_transformation = default_transformation if default_transformation!=None else ''

    url = f'https:////res.cloudinary.com/{cloud_name}/image/upload/{default_transformation}/v1/{public_id}'
    # in case there are double //, clean it up
    return url.replace('//','/')

def search_and_add_face_mtd(public_id:str)->dict:    
    resp = False
    # first configure cloudinary object
    credentials = get_secret(secret_name=Params.secret_name)
    if credentials:
        initialize_cloudinary(credentials)
    else:
        print('Unable to get Cloudinary credentials')
        return resp

    image_url = get_image_url(public_id=public_id, cloud_name=Params.cloud_name)
    resp = search_image_for_face(image_url=image_url)
    if resp['image_found']:
        # did it find a face?
        if len(resp['image_info']['FaceMatches']) > 0:
            name = resp['image_info']['FaceMatches'][0]['Face']['ExternalImageId']
            print(f'Model name found: {name}')
            resp = add_metadata_to_image(public_id=public_id, model_names=[name])
            resp = {'image_found': True, 'message': f'Added {name} to {public_id}'}
        else:
            resp = {'image_found':False, 'error':'No face found'}
    return resp
    
if __name__=="__main__":
    resp = search_image_for_face('https://res.cloudinary.com/dbmataac4/image/upload/v1709685211/test/rekognition/girl-1387118_640.jpg')
    if resp['image_found']:
        #print(json.dumps(resp))
        name = resp['image_info']['FaceMatches'][0]['Face']['ExternalImageId']
        public_id = 'test/rekognition/girl-1387118_640'
        add_metadata_to_image(public_id=public_id, model_names=[name])    