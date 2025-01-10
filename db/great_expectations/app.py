import great_expectations as gx
import pandas as pd

# Chargement des données pandas
data = {
    "name": ["Alice", "Bob", "Charlie", None],
    "age": [25, 30, None, 40],
    "status": ["active", "inactive", "active", "inactive"]
}
df = pd.DataFrame(data)
context = gx.get_context()

data_source = context.data_sources.add_pandas(name="data_source")