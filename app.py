
'''
Python version used: 3.12. Pip install requirements.txt to reproduce the code.
This script follows along this Azure Learn tutorial:
https://github.com/Azure/azureml-examples/blob/main/tutorials/azureml-getting-started/azureml-getting-started-studio.ipynb

IMPORTANT: The above tutorial assumes automatic authentication. Authentication will NOT work out of the box.
Follow along this tutorial to create your AZURE_CLIENT_ID, CLIENT_SECRET, and TENANT_ID, and add them to your project as contributor:
https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/manage-azureml-service/authentication-in-azureml/authentication-in-azureml.ipynb
Only follow the service principal authentication part - the rest is not relevant here.

Finally, you must export the  variables you created in the tutorial to bashrc.
AZURE_CLIENT_ID
AZURE_CLIENT_SECRET
AZURE_TENANT_ID

In bash, do the following:

nano ~/.bashrc
export AZURE_CLIENT_ID='<your-client-id-here>'
export AZURE_CLIENT_SECRET='<your_client_secret_here>'
export AZURE_TENANT_ID='<your_tenant_id_here>'

Then save the script. You can now reference your new environmental variables.
'''

# Import libraries -----------------------------------------------------------------------------------------------------
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

# Specify workspace
ml_client = MLClient(
    credential=credential,
    subscription_id="9afe6e00-d64a-4427-9ff4-4990adeac165",
    resource_group_name="Pay-as-you-go-resource-group",
    workspace_name="Pay-as-you-go-workspace")

# Check successful authentication. If no error, you're good to go.
ws = ml_client.workspaces.get("Pay-as-you-go-workspace")
print(ws.location, ":", ws.resource_group)

train_src_dir = "./src"
# os.makedirs(train_src_dir, exist_ok=True)

# Configure and run job ------------------------------------------------------------------------------------------------

# import the libraries
from azure.ai.ml import command
from azure.ai.ml import Input

# name the model you registered earlier in the training script
registered_model_name = "credit_defaults_model"

# configure the command job
job = command(
    inputs=dict(
        # uri_file refers to a specific file as a data asset
        data=Input(
            type="uri_file",
            path="https://azuremlexamples.blob.core.windows.net/datasets/credit_card/default%20of%20credit%20card%20clients.csv",
        ),
        test_train_ratio=0.2,  # input variable in main.py
        learning_rate=0.25,  # input variable in main.py
        registered_model_name=registered_model_name,  # input variable in main.py
    ),
    code="./src/",  # location of source code
    # The inputs/outputs are accessible in the command via the ${{ ... }} notation
    command="python main.py --data ${{inputs.data}} --test_train_ratio ${{inputs.test_train_ratio}} --learning_rate ${{inputs.learning_rate}} --registered_model_name ${{inputs.registered_model_name}}",
    # This is the ready-made environment you are using
    environment="azureml://registries/azureml/environments/sklearn-1.5/labels/latest",
    # This is the compute you created earlier. You can alternatively remove this line to use serverless compute to run the job
    compute="cpu-cluster-1",
    # An experiment is a container for all the iterations one does on a certain project. All the jobs submitted under the same experiment name would be listed next to each other in Azure ML studio.
    experiment_name="train_model_credit_default_prediction",
    display_name="credit_default_prediction",
)

# submit the command job
ml_client.create_or_update(job)


