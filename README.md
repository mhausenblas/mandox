# mandox

The polyglot persistence UI. Allows you to discover datasources in a 
cluster. Datasources can be anything that expose a network interface such as
HTTP. For example, in a Hadoop cluster you'd expect to find HDFS, HBase, or
Hive running.

![mandox screen-shot](https://dl.dropboxusercontent.com/u/10436738/tmp/mandox-screen-shot-0.png "mandox screen-shot")

## Installation

In order to run mandox, you need to have Python 2.7 installed. I've tested it 
under MacOS but it should also run under Linux without modifications.

All you need to do is to get the content of the repo, like in:

	$ git clone https://github.com/mhausenblas/mandox.git
	$ cd mandox

## Usage

You can launch mandox in the `server` directory:

	$ pwd
	/Users/mhausenblas2/Documents/repos/mandox/server
	$ ./man-man.sh start
	
That's all. You can check how mandox is doing as well:

	$ ./man-man.sh status
	Yes, mandox server is running. See details in mandox.log
	
When you don't need mandox anymore, it's time to get rid of it:

	$ ./man-man.sh stop
	Shutting down mandox server

Now, head over to your Web browser and, depending on the host you've deployed it,
point it to the respective location. Note that mandox is per default listening 
on port `6543`. 

So, for example, if you run mandox on the local machine, you'd visit 
[http://localhost:6543/](http://localhost:6543/) and you should see the start screen.

Once you see the start screen you can specify the scan range and explore the
running services.

## Configuration

There are two configuration files that allow you to modify the behavior
of mandox: `.mandox_config` (see also the [default](https://github.com/mhausenblas/mandox/blob/master/server/.mandox_config)) 
and `.mandox_mapping` (see also the [default](https://github.com/mhausenblas/mandox/blob/master/server/.mandox_mapping)).

### .mandox_config

Defines the port range that will be scanned per host, in the scan range. 
The format used in this file is a new-line separated list of entries. 
Lines starting with a `#` are interpreted as comments and ignored. 
Each entry has the following form:

	SERVICE:START_PORT-END_PORT

Note that the `START_PORT` is included and the `END_PORT` is excluded. For 
example, to scan service ABC on port 8080 you would add the following line:
 
	ABC:8080-8081

The default content of `.mandox_config` is as follows:

	HDFS:50070-50076
	MapR1:8443-8444
	MapR2:7220-7223
	HBase1:60000-60031
	HBase2:8080-8081
	Hive1:10000-10001
	Hive2:9083-9084
	MongoDB:28017-28018
	CouchDB:5984-5985
	Riak:8091-8092
	LDAP1:389-390
	LDAP2:636-637
	NFS1:2049-2050
	NFS2:9997-9999

### .mandox_mapping

Defines the visual information the client (the WebUI) uses to render each
service. The format used in this file is CSV and looks roughly like the following:

	port,title,icon,schema,docURL
	50070,HDFS Namenode,img/hdfs.png,HTTP,http://hadoop.apache.org/docs/stable/hdfs_user_guide.html
	50075,HDFS Datanode,img/hdfs.png,HTTP,http://hadoop.apache.org/docs/stable/hdfs_user_guide.html
	60000,HBase Master,img/hbase.png,HTTP,http://hbase.apache.org/book.html#ops_mgt
	60010,HBase Master,img/hbase.png,HTTP,http://hbase.apache.org/book.html#ops_mgt
	60030,HBase Regionservers,img/hbase.png,HTTP,http://hbase.apache.org/book.html#ops_mgt
	8080,HBase REST Service,img/hbase.png,HTTP,http://hbase.apache.org/book.html#ops_mgt
	...

## Acknowledgements	

Kudos for the icons, used with permission from [Iconic](http://somerandomdude.com/work/iconic/).

## License

[Apache 2](http://www.apache.org/licenses/LICENSE-2.0.html). All rights
MapR Technologies, 2013.