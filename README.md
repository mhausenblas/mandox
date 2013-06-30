# mandox

The polyglot persistence UI. Allows you to manage and use datasources in a 
cluster. Datasources can be anything that expose a network interface 
(HTTP, Thrift, etc.) such as HDFS, HBase, Hive, MongoDB, CouchDB, etc.

![mandox screen-shot](https://dl.dropboxusercontent.com/u/10436738/tmp/mandox-screen-shot-0.png "mandox screen-shot")

## To do

### Current

* Detailed View | Compact View | Reporting View panes in result
* Report View: generate nice PDF for print
* write launch bash script (nohup, background, etc)
* write  documentation: config files, deployment guide, screen shots, screen cast

## Done

* write auto discovery via server-side port scanner (IP range/host list)
* gather logos of services
* init UI (tabs, datasource pane)
* implement host/IP range clientside
* add more DS mappings to front-end
* add test function (end-to-end, that is, API to front-end)
* add icons (inspect, definition/doc)
* add up/down cmds to scan panel and hide scan panel when hitting scan
* add extended test (5 hosts)
* move PORT2SERVICE mapping to server-side and GET with init (.mandox_mapping)
* when more than one host in result, show grid-overview (number of services detected)
* add MapR specific stuff (MCS, NFS, CLDB, etc)

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

See also [MapR ports](http://www.mapr.com/doc/display/MapR2/Ports+Used+by+MapR).

## Dependencies

TBD.

## Acknowledgements

Icons from [Iconic](http://somerandomdude.com/work/iconic/).

## License

Apache 2