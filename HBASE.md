# Hbase


### Why HBase Database

* Database(DB) has 4 main requirements
	1. Structured - Row & Columns
	1. Random Access - Update 1 row at a time
	1. Low Latency - Very fast **read/write/update** operation
	1. ACID Compliant - data integrity

* ACID properties for a database:
	1. **Atomicity**: Transaction should be all-or-nothing
	1. **Consistency**: DB update not to violate any constraints
	1. **Isolation**: Concurrent operations on DB should appear in some sequence
	1. **Durability**: Safety of data in case of power loss, craches, error

* Hadoop limitation
	1. Unstructured data
	1. No Random access
	1. High latency
	1. Not ACID compliant

* Hbase is distributed database on top of Hadoop, built by google. They mapped:
	1. Bigtable => Hbase
	1. GFS => HDFS
	1. MapReduce => MapReduce

* Hbase Quality:
	1. Distributed - Stores data in HDFS
	1. Scalable - Proportional to number of nodes in the cluster
	1. Fault tolerant - Piggybacks on Hadoop
	1. Structured - Loose data structure
	1. Low latency - fast access due to row based indices
	1. Random access
	1. Somewhat ACID compliant

* Properties of Hbase:
	1. Columnar store (key,value)
	1. Denormalized storage
	1. Only CRUD operations - (Create, Read, Update, Delete)
	1. ACID at the row level

* Storing data as Columnar store:
	1. Sparse tables: No wastage of space when storing sparse data
	1. Dynamic attributes: Update attributes dynamically without changing storage structure