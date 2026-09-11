# Airflow


### Airflow Install
1. airflow requires python version above 3.5
1. airflow on local system UNIX based
1. *venv* python module to create virtual env
	1. python install venv
	1. mkdir airflow
	1. cd airflow
	1. python -m venv venv
	1. source venv/bin/activate
	1. pip install apache-airflow
	1. export AIRFLOW_HOME=$PWD
	1. airflow webserver -p 8080
	1. airflow scheduler
	1. localhost:8080/admin
	1. airflow.cfg change example to False to remove basic dags
	1. run *airlfow resetdb* to remove the dags
	1. In dags folder start writting code 

### Basics
* Airflow features -> scalable, dynamic, extensible, elegant
* Default trigger rule is *all-success*
* https://crontab.guru/
* https://github.com/apache/airflow
* *data profiling* tab can be used to create csv out of metadata of airflow
* Lifecycle state:
	* scheduled 
	* skipped
	* upstream_failed
	* up_for_reschedule
	* up_for_retry
	* failed
	* success
	* running
	* queued
	* *stopped* NOT a state

```py
from airflow import dag
from airflow.utils.dates import days_ago
from airflow.operators.bash_operator import BashOperator

#many utiliy given by airflow to handle dates

dag = Dag(
	dag_id = 'helloworld_dag',
	schedule_interval = '@daily',
	start_date = days_ago(1)
	)

task1 = BashOperator(
	task_id = 't1',
	bash_command = 'echo hello',
	dag = dag
	)
```


### Trigger Rules
1. all_success - default value, all task leading to current task should be complete
1. all_failed - all task leading to current task should be complete
1. all_done - all task leading to current task should be triggered, task status does not matter
1. one_failed - any one task leading to current task is failed
1. one_success - any one task leading to current task is success
1. none_failed - all task leading to current task should be complete or skipped
1. none_failed_or_skipped - all task leading to current task can have any state except be skipped or failed
1. none_skipped - all task leading to current task can have any state except be skipped
1. dummy - just for show, will be trigger on its will


### Dependancies between task
* task1 >> task2
* task1 >> [task2, task3]


## Extending Operators


1. Base operators - base class on top of which we can build own operators
1. Decorator required to create your own operator -> @apply_defaults
1. Multiple operators available out of the box to run jobs in airflow

```py
from airflow.models import BaseOperator
from airflow.utils import apply_defaults

class MyOperator(BaseOperator):

	@apply_defaults
	def __init__(self, name, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.name = name

	def execute(self, context):
		message = 'Hello {}'.format(self.name)
		print(message)
		return message

task = MyOperator(
	name = 'Anubhav',
	task_id = 't4',
	dag = dag
	)
```

### Variables

* Dynamic values to be changed without changing values in code
* create a variable in ADMIN>VARIABLES on UI
```py

#variable defined in UI as - myname = 'PP'

task = MyOperator(
	name = {{var.value.myname}},
	task_id = 't4',
	dag = dag
	)

```

### Airflow Connection to different data sources
* Following information in airflow UI:
	1. Name
	1. HOST
	1. Conn Type
	1. Port
	1. Username/Pass
	1. Scheme - (HTTP or HTTPS)


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Problem:
1. Test file containing closed orders against the customers received between 5-7 PM.
1. Customer related information stored in mysql/oracle db
1. Data to be loaded to Hive, Notifications and HBase data loading

### Solution proposed:
1. Set airfow sensor, to sense files, received in S3 bucket over https connection
1. Download file from S3 to local by doing SSH into edgenode
1. Download customer data to Hive from mysql using sqoop
1. Upload S3 order file to HDFS location
1. To filter data from files with clsoed orders, we will execute a spark program via a {jar file} having <input & output path>
1. Create Hive table from output path available in previous step and Load to HBase
1. Slack - Notification from pipeline Success/Failure of the pipeline


### Initiating dag

```py
from airflow import DAG
from airflow.utils.dates import days_ago
dag = DAG(
	dag_id = 'customer_360_pipeline',
	start_date=days_ago(1)
	)
```

### HTTP Sensor

> * Name of connection same as http_conn_id
> * If 'Poking' in the log, that is sensor is working.

```py
from airflow.utils.dates import days_ago
from airflow.utils.dates import timedelta
from airflow.sensor.http_sensor import HttpSensor

sensor = HttpSensor(
	task_id = 'watch_for_orders',
	http_conn_id = 'order_s3',
	endpoint = 'orders.csv',
	response_check = lambda response: response.status_code == 200,
	dag = dag,
	retry_delay = timedelta(minutes = 5),
	retries = 12
	)
```

### dummy

```python
from airflow.operators.dummy_operator import DummyOperator

dummy = DummyOperator(
	task_id = 'dummy',
	dag = dag
	)
```

> Note: If an operator not found as core offering of the airflow then contrib library can be searched

### SSH connection
1. Create the connection on airflow based on server information
1. Hook in airflow - trying to make a connection to a server
1. All the airflow metadata info is in form of **session**

```py
from airflow.contrib.operators.ssh_operators import SSHOperator
from airflow import settings
from airflow.models import 

def get_url():
	session = settings.Session()
	connection = session.query(Connection).filter(connection.conn_id == 'order_s3').first()
	return f'{connection.schema}://{connection.host}/orders.csv'


#download_order_command = 'rm -rf airflow_pipeline && mkdir -p airflow_pipeline && cd airflow_pipeline && wget https://trendy.s3.aws.south.com/orders.csv'
#Using airflow sessions to get the connection value as parameter
download_order_command = f'rm -rf airflow_pipeline && mkdir -p airflow_pipeline && cd airflow_pipeline && wget {get_url()}'

download_to_edge = SSHOperator(
	task_id = 'download_orders',
	ssh_conn_id = 'itversity',
#	command = 'hostname', # any unix comamnd to execute via edge node
	command = download_order_command,#command can be mentioned in single qutes as well as above
	dag = dag
	)

upload_orders_info = SSHOperator(
	task_id = 'upload_orders_to_hdfs',
	ssh_conn_id = 'itversity',
	command = 'hdfs dfs -rm -R -f airflow_input && hdfs dfs -mkdir -p airflow_input && hdfs dfs -put ./airflow_pipeline/orders.csv',
	dag = dag
	)
```

### sqoop data from db to hive

```py

def fetch_customer_info_cmd():
	command_one = "hive -e 'Drop Table airflow.customers'"
	command_one_ext = 'hdfs dfs -rm -R -f customers' # remove customers folder
	command_two = "sqoop import --connect jdbc:myql://xxxx --username xxx --password xxx --table customers --hive-import --create-hive-table --hive-table airflow.customers"
	command_three = "exit 0"
	return f'{command_one} && {command_one_ext} && {command_two} || {command_three}'

import_cust_info = SSHOperator(
	task_id = 'download_customers',
	ssh_conn_id = 'itversity',
	command = fetch_customer_info_cmd(),
	dag = dag
	)
```

> * Issue that can come up like connection to db, then notification channel to be added to paste such error and be notified.
> * First we do clean up and then load data, pattern followed in airflow generally!

### Run spark Jar file to filter data

```py
def get_order_filtered_cmd():
	command_zero = 'export SPARK_MAJOR_VERSION=2'
	command_one = 'hdfs dfs -rm -R -f airflow_output'
	command_two = 'spark-submit --class DataFramesExample sparkbundle.jar airflow_input/order.csv airflow_output'
	return f'{command_zero} && {command_one} && {command_two}'


process_order_info = SSHOperator(
	task_id = 'process_order',
	ssh_conn_id = 'itversity',
	command = get_order_filtered_cmd(),
	dag = dag
	)
```

### Create a hive table and upload to HBASE

```py
def order_hive_tb_cmd():
	command_one = 'hive -e "CREATE external table if not exists airflow.orders(order_id int,order_date string, status string) row format delimited fields terminated by \',\' stored as textfile location \'/user/bigdatabysumit/airflow_output" '
	return command_one


def load_hbase_cmd():
	command_one = 'hive -e "CREATE table if not exists airflow.airflow_hbase(customer_id int, customer_fname string ,customer_lname string ,order_id int ,order_date string) STORED BY \'org.apache.hadoop.hive.hbase.HBaseStorageHandler\' with SERDEPROPERTIES(\'hbase.columns.mapping\'=\':key,personal:customer_fname, personal:customer_lname,personal:order_id,personal:order_date\')"'
	command_two = 'hive -e "insert overwrite table airflow.airflow_hbase select c.customer_id, c.customer_fname, c.customer_lname, o.order_id, o.order_date from airflow.customers c join airflow.orders o ON c.customer_id = o.customer_id"'
	return f'{command_one} && {command_two}'

create_orders_table_hive = SSHOperator(
	task_id = 'create_orders_table_hive',
	ssh_conn_id = 'itversity',
	command = order_hive_tb_cmd(),
	dag = dag
	)

load_hbase = SSHOperator(
	task_id = 'load_hbase',
	ssh_conn_id = 'itversity',
	command = load_hbase_cmd(),
	dag = dag
	)
```

### Notification

1. get the webhook from slack
1. webhook to be defined in **connection**
1. channel - which channel to post notification
1. slack_password = can be given via hardcoding or some secret maanger


```py
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator 

success_notify = SlackWebhookOperator(
	task_id = 'success_notify',
	http_conn_id = 'slack_webhook',
	channel = 'xxxxx',
	message = 'Data loaded success in HBase',
	username = 'airflow',
	webhook_token=slack_password(),
	dag = dag
	)

def slack_password():
	return '<xxxxpasswordxxxx>'

failure_notify = SlackWebhookOperator(
	task_id = 'failure_notify',
	http_conn_id = 'slack_webhook',
	channel = 'xxxxx',
	message = 'Data loaded is failed',
	username = 'airflow',
	webhook_token=slack_password(),
	dag = dag,
	trigger_rule = 'all_failed'
	)

```

### Flow of Dag

```py

sensor >> import_cust_info
sensor >> download_to_edge >> upload_orders_info >> process_order_info >> 
[import_cust_info,create_orders_table_hive] >> load_hbase >> [success_notify,failure_notify] >> dummy

```
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
