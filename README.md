# Face Tagging with AWS Rekognition and Cloudinary

## Objective

[AWS Rekognition](https://aws.amazon.com/rekognition/) has the ability to index and search for faces. It requires the creation of a face collection, indexing faces by feeding training data and then running face search. However, Rekognition offers no storage or interface for working with the image assets.

This project aims to combine the use of Cloudinary's DAM with AWS Rekognition for building a user-friendly solution for training and searching assets based on the person name. 

## Architecture

The project relies on Cloudinary's [webhooks](https://cloudinary.com/documentation/notifications) on 2 specific events. 

* User or API event for adding a person's name to a training image.

![Indexing of a new face](https://akshayranganath-res.cloudinary.com/image/upload/f_auto,q_auto/blog/rekognition/indexing-faces.png)
* Upload of new image images that triggers face search.

![Search worflow to find a face](https://akshayranganath-res.cloudinary.com/image/upload/f_auto,q_auto/blog/rekognition/Searching%20face.png)

For detailed overview on the code setup and use, please read the accompanying blog post.

## Setup & Installation

In my case, I have used AWS [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) for building and deploying the code. If you prefer to use other techniques, please follow those steps.

After cloning the repo, do the following:

    sam build lambda/requirements.txt

Once code is built, deploy the app. If your AWS profile name is anything other than `default`, use the following format.

    sam deploy --guided --profile <your-profile-name>

This will create a random S3 bucket to upload the zipped code files. If you want to specify your S3 bucket, please add `--s3-bucket <your-bucket-name> to the command above.

For re-deploying the code, you can use:

    sam deploy --no-confirm-changeset --profile <your-profile-name>

## Troubleshooting Rekognition Face Index

AWS indexes the faces by creating a face collection. Here are some quick commands for troubleshooting. For all the commands, you may need to add the additional `--profile <your-profile-name>` parameter.

**List Collections**

    aws rekognition list-collections

**List Indexed faces**

    aws rekognition  list-faces --collection-id <collection-name> | jq '.Faces[].ExternalImageId'

**Delete Collection**

As you are testing, you want to reset your collection. Here's how to delete it.

    aws rekognition delete-collection --collection-id <collection-name>

 ## Integration in Action

 Here's how training for new faces will work.
 
    