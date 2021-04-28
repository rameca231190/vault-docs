# Diside for which application code needs to be run

app_name = input("What is the application code needs to be run for ? ")
print("""
Code will be run for """ + app_name.upper() + """ applications in DFS namespace on DTQ environment
""")

sa_list = open("sa_list.txt", "r")
content = sa_list.read()

# Create variable as of SA to add it to the Vault command.
sa_list_for_vault = content.replace("\n", ",")

print('''The list for SA added to Role in Vault will be ---> ''' + sa_list_for_vault)

# Login to Vault thru CLI
import os
os.system('echo "I am linux command"')
os.system('ls -ls')





