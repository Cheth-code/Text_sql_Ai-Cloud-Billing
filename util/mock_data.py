# this is capable of generating mock csv data for both azure_cost_usage and aws_cost_usage 
import pandas as pd
import random
from datetime import datetime, timedelta

print("Generating mock data for AWS and Azure...")

# --- Configuration ---
START_DATE = datetime.now() - timedelta(days=60)
NUMBER_OF_DAYS = 60

# --- AWS Config ---
AWS_SERVICES = ['Amazon Simple Storage Service', 'Amazon Elastic Compute Cloud', 'Amazon RDS']
AWS_REGIONS = ['us-east-1', 'us-west-2', 'ap-southeast-2', 'eu-west-1']
AWS_EC2_USAGE = ['BoxUsage:t3.micro', 'BoxUsage:r5.large', 'EBS:VolumeUsage.gp3']
AWS_S3_USAGE = ['TimedStorage-ByteHrs', 'Requests-Tier1']

# --- Azure Config ---
AZURE_SERVICES = ['Virtual Machines', 'Storage', 'Azure SQL Database']
AZURE_REGIONS = ['East US', 'West Europe', 'Southeast Asia']
AZURE_METERS = ['Standard_B1s VM', 'P10 LRS Disk', 'S0 DTUs']
AZURE_METER_CATEGORY = ['Virtual Machines', 'Storage', 'SQL Database']

aws_data = []
azure_data = []
current_date = START_DATE

for i in range(NUMBER_OF_DAYS):
    # Format date as 'YYYY-MM-DD'
    date_str = (START_DATE + timedelta(days=i)).strftime('%Y-%m-%d')
    
    # --- Generate AWS Data ---
    for _ in range(random.randint(2, 4)):
        is_ec2 = random.choice([True, False])
        service = 'Amazon Elastic Compute Cloud' if is_ec2 else 'Amazon Simple Storage Service'
        usage = random.choice(AWS_EC2_USAGE) if is_ec2 else random.choice(AWS_S3_USAGE)
        aws_data.append({
            'BillingPeriodStart': date_str, # Corrected to match PDF 
            'ServiceName': service,
            'RegionName': random.choice(AWS_REGIONS),
            'UsageType': usage,
            'EffectiveCost': random.uniform(1.0, 5.0), # Corrected to match PDF 
            'UsageAmount': random.uniform(1, 24) # Corrected to match PDF 
        })

    # --- Generate Azure Data ---
    for _ in range(random.randint(2, 4)):
        service_choice = random.choice(AZURE_SERVICES)
        meter_cat = AZURE_METER_CATEGORY[AZURE_SERVICES.index(service_choice)]
        meter = AZURE_METERS[AZURE_SERVICES.index(service_choice)]
        
        azure_data.append({
            'UsageDateTime': date_str,
            'ServiceName': service_choice,
            'ResourceLocation': random.choice(AZURE_REGIONS),
            'MeterCategory': meter_cat, # Corrected to match PDF 
            'Meter': meter,
            'EffectiveCost': random.uniform(0.5, 4.0),
            'UsageAmount': random.uniform(1, 50)
        })

# --- Create and Save AWS CSV ---
aws_df = pd.DataFrame(aws_data)
aws_df['ResourceId'] = 'arn:aws:ec2:' + aws_df['RegionName'] + ':123456789:instance/i-123abc' # Add ResourceId 
aws_df.to_csv('aws_cost_usage.csv', index=False)
print(f"Created aws_cost_usage.csv with {len(aws_df)} rows.")

# --- Create and Save Azure CSV ---
azure_df = pd.DataFrame(azure_data)
azure_df['ResourceId'] = '/subscriptions/12345-abc/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm-' + azure_df['ResourceLocation']
azure_df.to_csv('azure_cost_usage.csv', index=False)
print(f"Created azure_cost_usage.csv with {len(azure_df)} rows.")

print("\nMock data generation complete!")