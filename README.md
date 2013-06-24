# mandox

The polyglot persistence UI. Allows you to manage and use datasources in a 
cluster. Datasources can be anything that expose a network interface 
(HTTP, Thrift, etc.) such as HDFS, HBase, Hive, MongoDB, CouchDB, etc.

## To do

* write auto discovery-DONE
* gather logos-DONE
* init UI (tabs, datasource pane)-DONE
* implement host/IP range clientside-DONE
* add more DS mappings to front-end-DONE
* add icons (datasource, inspect, definition/doc)


## Background

### Well-known default ports
                                  
| Datasource               | Port   |
| ------------------------ | ------:|
| HDFS Namenode HTTP       | 50070  |
| HDFS Datanodes HTTP      | 50075  |
| *HBase Master Binary*    | 60000  |
| HBase HTTP               | 60010  |
| HBase Regionservers HTTP | 60030  |
| HBase REST Service       |  8080  |
| Hive Server              | 10000  |
| *Hive Metastore Thrift*  |  9083  |
| *MySQL/JDBC*             |  3306  |
| MongoDB/mongod           | 28017  |
| CouchDB/Futon            |  5984  |
| Riak HTTP                |  8091  |

## Dependencies

TBD.

## License

Apache 2