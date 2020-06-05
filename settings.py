# XLS SETTINGS
FAMILY_PER_TAB = False
LOOKUP_CODE = False
RI_INPUT_TEMPLATE = False

# PLAN SETTINGS
PLAN_TYPE = 'compute'
INSTANCE_FAMILY = ['m5','m6']
PLAN_LENGTH = [1,3]                           
PLAN_COMMIT = ['N', 'A']      
REGIONS = ['eu-west-1', 'eu-west-2']
OSES = ['Windows', 'RHEL', 'Linux']
TENANCY = ['Shared', 'Dedicated']