# Diside for which application code needs to be run.
app_name = input("What is the application code needs to be run for ? ")


# Print massege for which applicaiton code will be executed for.
print("""
Code will be run for """ + app_name.upper() + """ applications in """ + app_name.upper() + """ namespace on DTQ environment
""")

# Iterate thru list of applications. 
sa_list = ["<name>", "<name>", "<name>", "<name>", "<name>" "<name>", "<name>", "<name>", ]

if app_name in sa_list:
    print('Script will be run now for: ' + app_name.upper() + ' application')
else:
    print('This applicaiotn is not in the SA list please enter correct name of applicaiotn ! ! !')
    exit()

# Open the file which has SA list and read it.
sa_list = open("app-sa/" + app_name + ".txt", "r")
content = sa_list.read()

# Create variable as of SA to add it to the Vault command.
sa_list_for_vault = content.replace("\n", ",")

print('''The list for SA added to Role in Vault will be ---> ''' + sa_list_for_vault)


# Login to Vault thru CLI.
import os
#os.system('echo "I am linux command"')
os.system('export VAULT_ADDR=<> ; export VAULT_NAMESPACE=<> ; vault login -method=oidc')
os.system('export VAULT_NAMESPACE=ushi/oms')


# Write a policy in Vault.
os.system("""
vault policy write """ + app_name + """-policy - << EOF
#DEV
path "secrets/data/""" + app_name + """-dev*" {
capabilities = ["create", "update", "read", "list", "delete"]
}
#QA
path "secrets/data/""" + app_name + """-qa*" {
capabilities = ["create", "update", "read", "list", "delete"]
}
#PERF
path "secrets/data/""" + app_name + """-perf*" {
capabilities = ["create", "update", "read", "list", "delete"]
}

#Read root folder
path "secrets*" {
capabilities = ["list"]
}
EOF
""")


# Read a policy from vautl for verification.
os.system('vault policy read ' + app_name + '-policy')

# Enable kv method for application in secrets path.
os.system('vault kv put secrets/' + app_name + '-dev empty=value')
os.system('vault kv put secrets/' + app_name + '-qa empty=value')
os.system('vault kv put secrets/' + app_name + '-perf empty=value')

# Print KV list for vault to check what is available.
os.system('vault kv list secrets')

# Create a role for application i vault.
os.system('vault write auth/dev-kubernetes/role/' + app_name + '-role' ' bound_service_account_names=' + sa_list_for_vault + ' bound_service_account_namespaces=' + app_name + '-dev' + ' policies=' + app_name + '-policy  ttl=24h')
os.system('vault write auth/qa-kubernetes/role/' + app_name + '-role' ' bound_service_account_names=' + sa_list_for_vault + ' bound_service_account_namespaces=' + app_name + '-qa' + ' policies=' + app_name + '-policy  ttl=24h')
os.system('vault write auth/perf-kubernetes/role/' + app_name + '-role' ' bound_service_account_names=' + sa_list_for_vault + ' bound_service_account_namespaces=' + app_name + '-perf' + ' policies=' + app_name + '-policy  ttl=24h')

# Read roles created for verification.
os.system('vault read auth/dev-kubernetes/role/' + app_name + '-role ; vault read auth/qa-kubernetes/role/' + app_name + '-role ; vault read auth/perf-kubernetes/role/' + app_name + '-role')


# Creating auth method for the applicaiton team.
os.system('vault write auth/approle/role/' + app_name + '-role token_ttl="1h" token_max_ttl="4h" token_policies="' + app_name + '-policy"')

# Read role_id created and assign it to variable.
import subprocess
role_id = subprocess.Popen("vault read  auth/approle/role/" + app_name + "-role/role-id | grep -i role_id | awk '{print $2}'", shell=True,stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()

# Create variable secret_id
secret_id = ""

if len(secret_id) == 0:
    # Create secret_id
    #os.system('vault write -force auth/approle/role/' + app_name + '-role/secret-id | grep -i secret_id | head -1 | awk '{print $2}'')
    
    # Read secret_id created and assign it to variable.
    secret_id = subprocess.Popen("vault write -force  auth/approle/role/" + app_name + "-role/secret-id | grep -i secret_id | head -1 | awk '{print $2}' ", shell=True,stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
    print("Secret ID is created")
    print("Secret ID assigned to variable secret_id: " + secret_id)
else:
    print("Secret ID exist")

# Read secret_id created and assign it to variable.
#print('Read secret_id created and assign it to variable')
#secret_id = subprocess.Popen("vault list  auth/approle/role/" + app_name + "-role/secret-id | tail -1 ", shell=True,stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
#print('Secret ID is created')

# Generate output for user
print('Generate output for user.')

print('''
***************************************************************************************************************************************
Please use bellow commands to access vault:

export VAULT_ADDR=https://enterprisevault.npe.gcp.lowes.com:8200
export VAULT_NAMESPACE=ushi/oms
''' + 'vault write auth/approle/login role_id=' + role_id + ' secret_id=' + secret_id +'''

Open browser with Vault endpoint and token, go to secrets find file with respective to your application name and start writing secrets. 
Modify manifest and your property file.
***************************************************************************************************************************************
''')
