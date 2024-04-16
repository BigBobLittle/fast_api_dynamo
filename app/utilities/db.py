
#  setup dynamo db database 
import os 
import boto3
from datetime import datetime, timedelta
import uuid
from decimal import Decimal

class DynamoDBManager:
    def __init__(self):
            # Create a DynamoDB resource
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=os.environ.get('COGNITO_REGION'),
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_KEY')
            )

            # Get or create the DynamoDB table for items
            self.table_name = 'scultureai_items'
            self.table = self.get_or_create_table(
                self.table_name,
                
                key_schema=[
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'}, 
                    {'AttributeName': 'text', 'KeyType': 'RANGE'},
                    # {'AttributeName': 'createdAt', 'KeyType': 'HASH'},
                   
                ],
                attribute_definitions=[
                    {'AttributeName': 'user_id', 'AttributeType': 'S'}, 
                    {'AttributeName': 'text', 'AttributeType': 'S'},
                    # {'AttributeName': 'created_at', 'AttributeType': 'N'}, 
                    # {'AttributeName': 'updated_at', 'AttributeType': 'N'}
                ],
                
            )

         



    def get_or_create_table(self, table_name, key_schema, attribute_definitions):
        # Check if the table already exists
        existing_tables = self.dynamodb.tables.all()
        for table in existing_tables:
            if table.name == table_name:
                return table

       
        # Define the table schema
        table_schema = {
            'TableName': table_name,
            'KeySchema': key_schema,
            'AttributeDefinitions': attribute_definitions,
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,  
                'WriteCapacityUnits': 5  
            }
        }

        # Create the DynamoDB table
        return self.dynamodb.create_table(**table_schema)

