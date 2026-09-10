# Spark SQL — Getting Started Notes

Source: https://spark.apache.org/docs/latest/sql-getting-started.html#getting-started

These notes consolidate the complete discussion around the Spark SQL **Getting Started** documentation, including the detailed clarification of **DataFrame vs `Dataset[Row]` vs `Dataset<T>` in Python, Scala, and Java**.

---

## 1. Starting Point — `SparkSession`

- `SparkSession` is the main entry point for Spark SQL and DataFrame functionality.
- In PySpark:

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("Python Spark SQL basic example")
    .config("spark.some.config.option", "some-value")
    .getOrCreate()
)
```

- `.appName(...)` sets the application name.
- `.config(...)` provides Spark configuration.
- `.getOrCreate()` returns an appropriate existing `SparkSession` if available, otherwise creates one.
- Scala and Java use the same builder idea.
- SparkR uses `sparkR.session(...)`.
- SparkR maintains a global `SparkSession` singleton after initialization.
- Since Spark 2.0, `SparkSession` includes support for important Hive functionality such as HiveQL, Hive UDFs, and Hive tables.
- You do not need a separately installed Hive deployment simply to use Spark's built-in Hive support.

---

## 2. Creating DataFrames

A DataFrame can be created from several sources, including:

- files/data sources such as JSON;
- an existing RDD;
- Hive tables;
- in SparkR, local R data frames.

Example:

```python
df = spark.read.json("examples/src/main/resources/people.json")
```

The example data is conceptually:

```text
+----+-------+
| age|   name|
+----+-------+
|null|Michael|
|  30|   Andy|
|  19| Justin|
+----+-------+
```

`df.show()` displays the DataFrame contents.

Mental model:

```text
Data Source
    ↓
SparkSession.read
    ↓
DataFrame
```

---

# 3. DataFrame, `Dataset[Row]`, `Dataset<T>`, and `Row`

This is the most important conceptual section.

## 3.1 The shortest correct mental model

- A **DataFrame** is structured/tabular Spark data with a schema.
- In **PySpark**, its language-level type is simply:

```python
DataFrame
```

- In **Java**, a Spark DataFrame is represented as:

```java
Dataset<Row>
```

- In **Scala**, `DataFrame` is effectively an alias for:

```scala
Dataset[Row]
```

Therefore:

```text
Python        → DataFrame
Scala         → DataFrame = Dataset[Row]
Java          → Dataset<Row>
```

All three represent the same broad Spark concept: **structured data organized into rows and named columns with a schema**.

---

## 3.2 What does `Dataset<T>` mean?

`T` is the type of object exposed for each element of the Dataset.

For example:

```java
Dataset<Person>
```

means that elements are exposed as `Person` objects.

```java
Dataset<Row>
```

means that elements are exposed as generic Spark `Row` objects.

Conceptually:

```text
Dataset[T]
   │
   ├── Dataset[Person]
   │      └── each element is a Person
   │
   └── Dataset[Row]
          └── each element is a generic Row
```

---

## 3.3 What is a Spark `Row`?

`Row` is Spark's generic representation of one relational record.

Example data:

```text
name    age    country
Andy     30    UK
```

can conceptually be represented as:

```text
Row("Andy", 30, "UK")
```

A `Row` itself is generic. The **schema** tells Spark what the values mean.

```text
Schema
┌─────────┬─────────┬─────────┐
│ name    │ age     │ country │
│ string  │ long    │ string  │
└─────────┴─────────┴─────────┘
              │
              ↓ describes

Row
┌─────────┬─────────┬─────────┐
│ "Andy"  │ 30      │ "UK"    │
└─────────┴─────────┴─────────┘
```

Remember:

```text
Row    = generic record
Schema = column names + Spark SQL data types
```

---

## 3.4 Why Java says `Dataset<Row>` instead of `DataFrame`

In Java you normally write:

```java
Dataset<Row> df = spark.read().json("people.json");
```

There is no separate Java `DataFrame` type that you normally use.

Therefore:

```text
Java DataFrame = Dataset<Row>
```

`Dataset<Row>` and "DataFrame" are not two different datasets here. `Dataset<Row>` is Java's representation of a Spark DataFrame.

---

## 3.5 Scala

Scala provides the more convenient name:

```scala
DataFrame
```

which effectively corresponds to:

```scala
Dataset[Row]
```

So these express the same kind of Spark object:

```scala
val df: DataFrame = spark.read.json("people.json")
```

and conceptually:

```scala
val df: Dataset[Row] = spark.read.json("people.json")
```

---

## 3.6 PySpark

Python does **not expose Spark's typed `Dataset[T]` API**.

In PySpark you use:

```python
df = spark.read.json("people.json")
```

and the object is:

```text
pyspark.sql.DataFrame
```

There is no PySpark equivalent such as:

```text
Dataset[Person]
```

or a public Python `Dataset[Row]` abstraction.

The high-level picture is:

```text
                  Spark Structured APIs
                         │
          ┌──────────────┴──────────────┐
          │                             │
       Python                       JVM APIs
          │                        Scala/Java
          │                             │
      DataFrame                     Dataset[T]
                                    /       \
                           Dataset[Row]   Dataset[Person]
                                │
                            DataFrame
```

---

## 3.7 Does a PySpark DataFrame contain Rows?

When you bring records into Python, Spark exposes them as `Row` objects.

For example:

```python
df.collect()
```

may return:

```python
[
    Row(age=30, name='Andy'),
    Row(age=19, name='Justin')
]
```

Also:

```python
df.rdd
```

returns an RDD whose elements are Rows:

```text
RDD[Row]
```

However, this does **not** mean PySpark exposes the JVM typed Dataset API as `Dataset[Row]`.

Useful distinction:

```text
df           → PySpark DataFrame

df.rdd       → RDD[Row]

df.collect() → Python list of Row objects on the driver
```

---

## 3.8 Do not imagine a DataFrame as literally a collection of Python/Java `Row` objects internally

This mental model is too simplistic:

```text
Row object
Row object
Row object
Row object
```

Spark SQL uses optimized internal data representations and query execution machinery.

A better conceptual flow is:

```text
PySpark / Scala / Java API
          ↓
Spark SQL logical plan
          ↓
Catalyst analysis + optimization
          ↓
Physical plan
          ↓
Spark execution engine
          ↓
Executors
```

User-facing `Row` objects become especially visible at API boundaries such as `collect()` or `.rdd`.

---

## 3.9 Why is a DataFrame called "untyped" if its columns clearly have types?

This is Spark terminology that can easily be misunderstood.

**Untyped does NOT mean Spark does not know the column types.**

For example, Spark may know:

```text
name : string
age  : long
```

through the DataFrame schema.

The distinction is about the **programming-language type system**.

With:

```java
Dataset<Row>
```

Java knows only that every element is a generic `Row`.

The detailed business structure:

```text
name : string
age  : long
```

lives in Spark's schema rather than in a Java domain class.

With:

```java
Dataset<Person>
```

the Java compiler knows what a `Person` contains.

Example:

```text
Person
├── name : String
└── age  : long
```

So the useful interpretation is:

```text
DataFrame / Dataset<Row>
    → schema-typed by Spark
    → not domain-object typed at compile time

Dataset<Person>
    → Spark schema + domain object type known to Java/Scala compiler
```

---

## 3.10 Why compile-time typing matters

Suppose this DataFrame has only:

```text
name
age
```

Java code:

```java
df.select("salary");
```

is syntactically valid Java because `"salary"` is simply a String.

The Java compiler cannot determine whether the DataFrame actually contains a `salary` column.

Spark detects that later during query analysis.

So for `Dataset<Row>`:

```text
Java compiler
    └── knows element type = Row

Spark analyzer
    └── knows actual DataFrame schema
```

Compare that with:

```java
Dataset<Person> people;
```

If `Person` has no `getSalary()` method and code tries:

```java
person.getSalary()
```

Java can reject it at compile time.

That is the core benefit meant by **typed Dataset transformations**.

---

## 3.11 Why a `Row` is useful

A generic `Row` allows the schema to change while the Java/Scala object type remains the same.

Example:

Initial DataFrame:

```text
Dataset<Row>
Schema:
name : string
age  : long
```

After:

```java
df.select("name")
```

result:

```text
Dataset<Row>
Schema:
name : string
```

After:

```java
df.groupBy("age").count()
```

result:

```text
Dataset<Row>
Schema:
age   : long
count : long
```

Notice that the Java type remains:

```text
Dataset<Row>
```

while Spark's schema can change after every relational transformation.

That flexibility is why `Row` works well as the generic DataFrame record type.

---

## 3.12 Python behaves similarly at the DataFrame level

Start:

```python
df = spark.read.json("people.json")
```

Object type:

```text
DataFrame
```

Schema:

```text
name : string
age  : long
```

Then:

```python
x = df.select("name")
```

`x` is still a `DataFrame`, but its schema is now:

```text
name : string
```

Then:

```python
y = df.groupBy("age").count()
```

`y` is still a `DataFrame`, but now its schema is:

```text
age   : long
count : long
```

Thus both Java and Python separate the language-level container type from the current Spark schema:

```text
Java:
Dataset<Row> + changing Spark schema

Python:
DataFrame     + changing Spark schema
```

---

## 3.13 DataFrame column operations build Spark expressions

In PySpark:

```python
df["age"]
```

does not fetch the whole `age` column into Python.

It creates a Spark `Column` expression referring to the column.

Likewise:

```python
df["age"] + 1
```

constructs an expression conceptually similar to:

```text
Add(
    AttributeReference("age"),
    Literal(1)
)
```

Then:

```python
df.select(df["name"], df["age"] + 1)
```

conceptually follows:

```text
Python API
    ↓
Spark expressions
    ↓
Logical plan
    ↓
Catalyst optimizer
    ↓
Physical execution plan
    ↓
Executors
```

It is **not** equivalent to Python looping through every row and incrementing the value itself.

Java performs the same basic kind of expression construction through APIs such as:

```java
df.select(
    col("name"),
    col("age").plus(1)
);
```

The Python and Java syntax differs, but both ultimately construct work for Spark SQL's execution engine.

---

## 3.14 DataFrame vs RDD operations

Compare:

```python
df.filter(df.age > 21)
```

with:

```python
df.rdd.filter(lambda row: row.age > 21)
```

The first uses a DataFrame expression that Spark SQL understands semantically:

```text
age > 21
```

Therefore Spark can analyze and optimize it through its structured query engine.

The second is an RDD transformation over row objects and behaves through the lower-level RDD API.

Conceptually:

```text
DataFrame API
    ↓
Column expressions
    ↓
Logical plan
    ↓
Catalyst optimization
    ↓
execution
```

versus:

```text
RDD API
    ↓
function over RDD records
    ↓
RDD execution
```

This is one major reason the structured DataFrame API is so important in modern Spark.

---

## 3.15 Precise cross-language summary

| Concept | PySpark | Scala | Java |
|---|---|---|---|
| DataFrame API | Yes | Yes | Yes |
| DataFrame language type | `DataFrame` | `DataFrame` / `Dataset[Row]` | `Dataset<Row>` |
| Typed `Dataset[T]` API | No | Yes | Yes |
| Example typed Dataset | — | `Dataset[Person]` | `Dataset<Person>` |
| Spark SQL schema | Yes | Yes | Yes |
| Catalyst-optimized structured operations | Yes | Yes | Yes |

The four statements to remember are:

1. **PySpark has DataFrames but does not expose the typed `Dataset[T]` API.**
2. **A Java DataFrame is `Dataset<Row>`.**
3. **A Scala DataFrame is effectively `Dataset[Row]`.**
4. **`Dataset<Person>` is different because the Java/Scala compiler understands the `Person` type, whereas a generic `Row` relies on Spark's schema for its business structure.**

The single most important sentence is:

> `Dataset<Row>` does not mean Spark does not know the types of the columns. Spark knows those from the schema. It means the Java/Scala compiler sees each record as a generic `Row` rather than a domain-specific object such as `Person`.

---

# 4. Common DataFrame Operations

DataFrames provide a domain-specific language for structured transformations.

Examples:

### Inspect schema

```python
df.printSchema()
```

Example:

```text
root
 |-- age: long (nullable = true)
 |-- name: string (nullable = true)
```

### Select a column

```python
df.select("name")
```

### Select expressions

```python
df.select(df["name"], df["age"] + 1)
```

### Filter rows

```python
df.filter(df["age"] > 21)
```

### Group and aggregate

```python
df.groupBy("age").count()
```

In PySpark, prefer:

```python
df["age"]
```

over attribute access such as:

```python
df.age
```

because bracket access avoids potential naming conflicts with DataFrame attributes/methods.

Scala commonly uses syntax such as `$"age"` after importing `spark.implicits._`.

Java commonly uses `col("age")`.

---

# 5. Running SQL Queries Programmatically

A DataFrame can be registered as a temporary SQL view:

```python
df.createOrReplaceTempView("people")
```

Then SQL can query it:

```python
sqlDF = spark.sql("SELECT * FROM people")
```

SQL results are again structured Spark objects:

```text
Python → DataFrame
Scala  → DataFrame / Dataset[Row]
Java   → Dataset<Row>
```

Therefore DataFrame operations and SQL are not separate execution systems.

You can move between them:

```text
DataFrame API
     ↓
Temporary View
     ↓
Spark SQL
     ↓
DataFrame
     ↓
DataFrame API again
```

---

# 6. Temporary Views vs Global Temporary Views

## Normal temporary view

Created with:

```python
df.createOrReplaceTempView("people")
```

Properties:

- scoped to the SparkSession;
- disappears when that session terminates;
- another independent SparkSession does not automatically see it as its own normal temporary view.

Conceptually:

```text
SparkSession A
    └── people
```

## Global temporary view

Created with:

```python
df.createGlobalTempView("people")
```

Properties:

- can be accessed across Spark sessions inside the same Spark application;
- lasts for the Spark application's lifetime;
- stored in Spark's reserved database:

```text
global_temp
```

Therefore query it using:

```sql
SELECT * FROM global_temp.people
```

Another session can access it:

```python
spark.newSession().sql(
    "SELECT * FROM global_temp.people"
)
```

Mental model:

```text
Spark Application
│
├── SparkSession A
│     └── session temp views
│
├── SparkSession B
│     └── session temp views
│
└── global_temp
      └── global temporary views
```

Lifetime:

```text
Normal temp view  → SparkSession lifetime
Global temp view  → Spark application lifetime
```

A global temporary view can also be created through SQL:

```sql
CREATE GLOBAL TEMPORARY VIEW temp_view
AS SELECT a + 1, b * 2 FROM tbl
```

---

# 7. Typed Datasets

Typed Datasets are primarily a Scala/Java API concept.

Examples:

```text
Dataset[Person]
Dataset[Long]
```

Spark uses specialized **Encoders** for Dataset objects.

Conceptually:

```text
Dataset[T]
    ↓
Encoder[T]
    ↓
Spark internal representation
```

Encoders allow Spark to work efficiently with structured JVM data and support operations such as filtering, sorting, and hashing through Spark's internal representation.

## Scala example

```scala
case class Person(name: String, age: Long)
```

Spark can work with:

```scala
Dataset[Person]
```

Importing:

```scala
import spark.implicits._
```

provides conveniences and encoders for common Scala types.

Example:

```scala
Seq(1, 2, 3).toDS()
```

creates a typed Dataset.

A DataFrame can also be converted to a typed Dataset:

```scala
spark.read.json(path).as[Person]
```

## Java example

Java commonly uses JavaBeans and encoders:

```java
Encoder<Person> personEncoder = Encoders.bean(Person.class);
```

Common encoders are available through `Encoders`, such as:

```java
Encoders.LONG()
```

---

# 8. RDD and DataFrame Interoperability

Spark provides two broad ways to convert RDD-based data into structured DataFrames.

```text
RDD
 │
 ├── structure already known
 │       ↓
 │   infer schema
 │
 └── structure determined dynamically
         ↓
     explicitly build schema
```

---

# 9. RDD → DataFrame by Inferring Schema

## PySpark

Typical flow:

```text
Text file
   ↓
RDD[String]
   ↓ split
RDD[parts]
   ↓ map to Row
RDD[Row]
   ↓ createDataFrame
DataFrame
```

Example idea:

```python
lines = sc.textFile(".../people.txt")
parts = lines.map(lambda line: line.split(","))
people = parts.map(lambda p: Row(name=p[0], age=int(p[1])))
schemaPeople = spark.createDataFrame(people)
```

The names supplied to `Row`, such as `name` and `age`, become DataFrame column names, and Spark infers corresponding types.

The DataFrame can then be registered as a temporary view and queried using SQL.

A DataFrame can also expose an RDD again:

```python
schemaPeople.rdd
```

which gives an RDD of Rows.

## Scala

Scala can use reflection over case classes.

Example:

```scala
case class Person(name: String, age: Long)
```

An RDD of `Person` objects can be converted into a DataFrame, with case-class field names becoming DataFrame column names.

Case classes can be nested and can contain structures such as sequences and arrays.

`import spark.implicits._` enables conveniences such as `.toDF()`.

Returned Rows can be accessed by position or by field name.

## Java

Java can infer DataFrame schemas from JavaBeans through reflection.

A JavaBean should provide appropriate getters/setters and normally implement `Serializable`.

Spark supports nested JavaBeans, lists, and arrays in this conversion model.

The documentation notes limitations for JavaBean `Map` fields in this automatic conversion path.

Example pattern:

```java
spark.createDataFrame(peopleRDD, Person.class)
```

---

# 10. RDD → DataFrame by Programmatically Specifying Schema

Use this approach when the schema is dynamic or cannot conveniently be represented by predefined classes/objects.

Typical reasons:

- column names are determined at runtime;
- data types are determined at runtime;
- records arrive in a raw structure such as strings;
- the desired projected structure depends on runtime input.

The process has three essential steps:

1. Convert each RDD record into a predictable positional representation such as `Row` or a tuple.
2. Build a `StructType` schema.
3. Pass both the records and schema to `SparkSession.createDataFrame()`.

Conceptually:

```text
RDD[String]
    ↓ transform
RDD[Row] / records
    +
StructType schema
    ↓
createDataFrame(...)
    ↓
DataFrame
```

The order and types of values in each record must correspond to the schema being applied.

---

# 11. `StructType` and `StructField`

`StructType` describes an entire Spark SQL row schema.

`StructField` describes one field/column.

Conceptually:

```text
StructType
│
├── StructField
│     ├── name
│     ├── data type
│     └── nullable?
│
├── StructField
│     ├── name
│     ├── data type
│     └── nullable?
│
└── ...
```

Example:

```python
StructField("name", StringType(), True)
```

means:

```text
column name = name
data type    = string
nullable     = true
```

A collection of fields forms a `StructType`.

---

# 12. Scalar Functions

A scalar function returns **one output value for each input row**.

```text
row 1 → result 1
row 2 → result 2
row 3 → result 3
```

Spark SQL provides many built-in scalar functions.

Spark also supports user-defined scalar functions (UDFs).

---

# 13. Aggregate Functions

An aggregate function processes a group of rows and produces an aggregate result for that group.

```text
row
row   → one aggregate result
row
```

Common examples include:

- `count()`
- `count_distinct()`
- `avg()`
- `max()`
- `min()`

Spark also supports user-defined aggregate functions.

---

# 14. Complete Page Mental Model

The Getting Started page is teaching this progression:

```text
1. SparkSession
       ↓
2. Read/create structured data
       ↓
   DataFrame
       ↓
3. Manipulate with DataFrame expressions
   select / filter / groupBy / functions
       ↓
   DataFrame
       ↓
4. Optionally expose the DataFrame as a SQL view
       ↓
   Spark SQL
       ↓
   DataFrame
       ↓
5. Understand view lifetime
   ├── temporary view        → SparkSession
   └── global temporary view → Spark application
       ↓
6. Scala/Java can additionally use typed Dataset[T]
       ↓
7. Existing RDDs can become DataFrames
   ├── infer schema
   └── explicitly build StructType
       ↓
8. Process data using SQL/DataFrame functions
   ├── scalar functions
   └── aggregate functions
```

A wider mental map is:

```text
                   Spark SQL / Structured APIs
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
      Data Sources           RDD                SQL
          │                   │                   │
          └──────────────→ DataFrame ←────────────┘
                              │
                   DataFrame expressions
                              │
                       Logical Plan
                              │
                          Catalyst
                              │
                    Optimized/Physical Plan
                              │
                          Executors
```

For PySpark, the most important chain to retain is:

```text
SparkSession
    ↓
DataFrame
    ↓
Schema + Column expressions
    ↓
select / filter / groupBy / functions
    ↓
Temporary views / spark.sql()
    ↓
DataFrame
    ↓
Optional RDD interoperability
```

---

# Final Precision Summary

If everything else becomes blurry, retain these statements:

- **DataFrame = distributed structured/tabular Spark data + schema.**
- **PySpark calls it `DataFrame`.**
- **Java represents a DataFrame as `Dataset<Row>`.**
- **Scala's `DataFrame` is effectively `Dataset[Row]`.**
- **`Row` is a generic record; the DataFrame schema explains its fields.**
- **`Dataset<Person>` is a typed JVM Dataset whose domain type is visible to the Java/Scala compiler.**
- **"Untyped DataFrame" does not mean columns have no types; it means the compiler does not know a domain-specific type such as `Person` for every row.**
- **PySpark does not expose the typed `Dataset[T]` API.**
- **DataFrame column operations build Spark expressions and logical plans; they do not normally loop through data row-by-row in Python.**
- **Spark SQL and the DataFrame API feed into the same structured query engine.**
- **`.collect()` brings records to the driver as language-visible Row objects.**
- **`.rdd` crosses from the structured DataFrame API into the lower-level RDD API.**
