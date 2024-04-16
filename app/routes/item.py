from fastapi import APIRouter, Depends, HTTPException
from boto3.dynamodb.conditions import Key 
from datetime import datetime
from ..dependencies import authenticate_user
from ..utilities.db import DynamoDBManager



dynamodb = DynamoDBManager()

router = APIRouter()


@router.post("/create_item")
async def create_item(text:str, current_user: dict = Depends(authenticate_user)):
    """
    Creates a new item in the database.

    Parameters:
        item (dict): The item data to be created.

    Returns:
        dict: The created item.

    Raises:
        HTTPException: If there is an error creating the item.
    """
    user_id = current_user.get("sub")
    timestamp= datetime.now().isoformat()
    
    try:
        textTable = dynamodb.table.put_item(
            Item={
                
                "user_id": user_id,
                "timestamp": timestamp,
                "text": text,
               
                    }
        )
        print(textTable)
        return {"message": "Text saved successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error creating item")
  
    

@router.get("/fetch_my_items")
async def read_items(current_user=Depends(authenticate_user) ):
    """
    Fetches the items associated with the current user.

    Parameters:
        current_user (dict): The current user information.

    Returns:
        list: A list of items associated with the current user.

    Raises:
        HTTPException: If there is an error retrieving the items.
    """
    
    user_id = current_user.get("sub")
    try:
        response = dynamodb.table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)  
        )
        items = response['Items']
        return items
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error retrieving items")
    

@router.get("/fetch_all_items_by_admin")
async def read_items(current_user=Depends(authenticate_user) ):
    """
    Fetches all items in the database by an admin user.

    Parameters:
        current_user (dict): The current user information.

    Returns:
        list: A list of items in the database.

    Raises:
        HTTPException: If the user is not an admin or there is an error retrieving the items.
    """

    try:
        if "cognito_groups" in current_user and "admin" in current_user["cognito_groups"]:
        
            response = dynamodb.table.scan()
            items = response['Items']
            return items
        else:
            raise HTTPException(status_code=500, detail="Error retrieving items")
           
    except Exception as e:
        print(e)
        raise HTTPException(status_code=403, detail="Forbidden")
        
