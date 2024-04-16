from fastapi import APIRouter, HTTPException
import boto3 
from pydantic import BaseModel  
from dotenv import load_dotenv
import os 
from ..utilities.db import DynamoDBManager

load_dotenv()
router = APIRouter()
cognito_client = boto3.client('cognito-idp', region_name='eu-west-2')
dynamodb = DynamoDBManager()

class User(BaseModel):
    email: str = 'test@test.com'
    password: str = 'pAssw0rd@'
    


# create a dummy endpoint for registering users
@router.post("/register")
def register_user(user: User):
    try:
        response = cognito_client.sign_up(
            ClientId=f"{os.environ.get('COGNITO_APP_CLIENT_ID')}",
            Username=user.email,
            Password=user.password
        )
        return {"message": "User registered successfully"}
    except cognito_client.exceptions.UsernameExistsException:
        raise HTTPException(status_code=400, detail="Email already exists")
        
    except cognito_client.exceptions.InvalidPasswordException:
        raise HTTPException(status_code=400, detail="Invalid password")
    except Exception as e:
        return {"message": f"An error occurred: {str(e)}"}
    

# create an endpoint for logging in users

@router.post("/login")
def login_user(user: User):
    try:
        response = cognito_client.initiate_auth(
            ClientId=f"{os.environ.get('COGNITO_APP_CLIENT_ID')}",
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': user.email,
                'PASSWORD': user.password
            }
        )
       
        return {"message": "User logged in successfully", "token": response.get('AuthenticationResult').get('AccessToken')}
    except cognito_client.exceptions.NotAuthorizedException:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    except cognito_client.exceptions.UserNotFoundException:
        raise HTTPException(status_code=404, detail="User not found")
    except cognito_client.exceptions.UserNotConfirmedException:
        raise HTTPException(status_code=400, detail="User not confirmed")
    except Exception as e:
        print(e)
        return {"message": f"An error occurred: {str(e)}"}