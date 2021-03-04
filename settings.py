# XLS SETTINGS
FAMILY_PER_TAB = False
LOOKUP_CODE = True
RI_INPUT_TEMPLATE = True

# PLAN SETTINGS
PLAN_TYPE = 'compute'
INSTANCE_FAMILY = ['m5','t3','t2','c4','t3a']
PLAN_LENGTH = [1,3]                           
PLAN_COMMIT = ['N', 'A']      
REGIONS = ['eu-west-1', 'eu-west-2']
OSES = ['RHEL', 'Windows', 'Linux', 'Windows with SQL Std']
TENANCY = ['Shared', 'Dedicated']