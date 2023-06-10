# Polyglotter

Official implementation of "Translating synthetic natural language to database queries with a polyglot deep learning framework", published in Nature Scientific Reports ([link](https://www.nature.com/articles/s41598-021-98019-3))

# Description

Polyglotter supports the mapping of natural language searches to database queries. Importantly, it does not require the creation of manually annotated data for training and therefore can be applied easily to multiple domains. The framework is polyglot in the sense that it supports multiple different database engines that are accessed with a variety of query languages, including SQL and Cypher. Furthermore Polyglotter supports multi-class queries. Good performance is achieved on both toy and real databases, as well as a human-annotated WikiSQL query set. Thus Polyglotter may help database maintainers make their resources more accessible.

# Graphical summary of the proposed system

<p align="center">
  <img src="https://github.com/AdrianBZG/Polyglotter/assets/8275330/8dcaedf6-8465-4f27-9d3e-25852fba03ed"/>
</p>
  
# Running Polyglotter

In this section, we describe the necessary steps to run Polyglotter on a MySQL database.

## Step 1: Generating database schema

In order to generate a dataset to train the translation model, the schema of the target database needs to be generated first.
We provide an example script [here](https://github.com/AdrianBZG/Polyglotter/blob/master/RandomQueryGenerator/MySQLGetDBSchema.py).
The only required change is to specify your database credentials at the end of the script, where the MySQLGetDBSchema object is created, such as:

`MySQLSchema = MySQLGetDBSchema('MySQL Example', {"host":"localhost", "user": "root", "passwd": "test", "database": "testdb", "port": 3306})`

Then, call the method getDBSchema() method from the object, which will handle all the logic for you in order to generate the DB schema and save it to a pickle file:

`MySQLSchema.getDBSchema()`

At this point, you should have a `MySQLdbSchema.obj` generated for you, which should be moved to the `Data\Schemas` directory.

## Step 2: Generating the dataset of question-query pairs

Next, a dataset containing pairs of question-SQL query pairs have to be generated for your target database. Following the use case above, we provide an example script to generate the dataset, preprocess it and compute the FastText embeddings. The script is located [here](https://github.com/AdrianBZG/Polyglotter/blob/master/RandomQueryGenerator/MySQLGenerateRandomQueries.py). The output of the script should be moved to the `Data\TrainingData\MySQL` directory.

## Step 3: Training the model using OpenNMT

Finally, you are now able to traing a model for the text-to-SQL translation using OpenNMT. We provide an example script in https://github.com/AdrianBZG/Polyglotter/blob/master/NLP/TrainModels.py, which you can adapt to your needs.

Once the training concludes, you will find the model object in the `Models` directory. This object can now be used for serving the model.

# Trying a trained model

Once you have a trained model, you can use the Jupyter Notebook available in [here](https://github.com/AdrianBZG/Polyglotter/blob/master/Notebook.ipynb) to quickly run some questions and obtain the corresponding SQL queries over your target database.

# Deploying a Web Service to query the model

Also, we are providing a [Dockerfile](https://github.com/AdrianBZG/Polyglotter/blob/master/Dockerfile) to spin up a web service, so that you can serve your model over an API and obtain its predictions.
